# app/routers/synthetic.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.utils import get_current_user
from app.sdv.factories import SynthesizerFactory
from app.sdv.evaluators import evaluate_data_quality
from app.repository import get_all_data_records, get_synthetic_data_by_id, save_synthetic_data, convert_data_records_to_dataframe
from sdv.metadata import SingleTableMetadata
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from app.common.models import User, DataRecord, SyntheticData
import pandas as pd
import simplejson as json
import joblib
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import os

router = APIRouter()


@router.post("/generate_synthetic_data/")
async def generate_synthetic_data(synthesizer_type: str = "ctgan",
                                  db: Session = Depends(get_db),
                                  current_user: User = Depends(get_current_user)):  # Protected route
    # Fetch all data records from the database
    data_records = get_all_data_records(db)

    # Convert data records to a DataFrame
    data = convert_data_records_to_dataframe(data_records)

    # Save the actual IDs before dropping them
    original_data_ids = list(data['id'])

    # Drop columns that are not needed for synthesis
    data = data.drop(columns=['id', 'name', 'ticket', 'cabin'], errors='ignore')

    # Create metadata from the DataFrame
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(data)

    # Get the synthesizer and fit the data
    synthesizer = SynthesizerFactory.get_synthesizer(synthesizer_type, metadata)
    synthesizer.fit(data)

    # Generate synthetic data
    synthetic_data = synthesizer.sample(num_rows=len(data))

    # Convert synthetic data to JSON
    synthetic_data_json = synthetic_data.to_json(orient='records')

    # Save the synthetic data along with the original data IDs
    new_synthetic_data = SyntheticData(
        synthesizer_type=synthesizer_type,
        data=synthetic_data_json,
        original_data_ids=json.dumps(original_data_ids)  # Use the actual IDs
    )
    saved_synthetic_data = save_synthetic_data(db, new_synthetic_data)

    return {"status": "Synthetic data generated successfully", "synthetic_data_id": saved_synthetic_data.id}


@router.post("/augment_and_train/")
async def augment_and_train(synthesizer_type: str = "ctgan",
                            augmentation_factor: int = 2,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user)):  # Protected route
    data_records = get_all_data_records(db)
    data = convert_data_records_to_dataframe(data_records)
    data = data.drop(columns=['id', 'name', 'ticket', 'cabin'], errors='ignore')

    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(data)

    synthesizer = SynthesizerFactory.get_synthesizer(synthesizer_type, metadata)
    synthesizer.fit(data)
    synthetic_data = synthesizer.sample(num_rows=len(data) * augmentation_factor)

    augmented_data = pd.concat([data, synthetic_data], ignore_index=True)

    X = augmented_data.drop(columns=['survived'])
    y = augmented_data['survived']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    model_path = os.path.join(os.getcwd(), "model.joblib")
    joblib.dump(model, model_path)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return {"accuracy": accuracy}

@router.post("/evaluate_synthetic_data/")
async def evaluate_synthetic_data(synthetic_data_id: int,
                                  db: Session = Depends(get_db),
                                  current_user: User = Depends(get_current_user)):  # Protected route
    synthetic_data_record = get_synthetic_data_by_id(db, synthetic_data_id)
    if not synthetic_data_record:
        raise HTTPException(status_code=404, detail="Synthetic data not found")

    original_data_ids = json.loads(synthetic_data_record.original_data_ids)
    original_data_records = db.query(DataRecord).filter(DataRecord.id.in_(original_data_ids)).all()
    real_data = convert_data_records_to_dataframe(original_data_records)
    synthetic_data = pd.read_json(synthetic_data_record.data)

    # Drop the 'id' column from both DataFrames
    real_data = real_data.drop(columns=['id'], errors='ignore')
    synthetic_data = synthetic_data.drop(columns=['id'], errors='ignore')

    metadata = SingleTableMetadata()
    metadata.add_column('pclass', sdtype='categorical')
    metadata.add_column('sex', sdtype='categorical')
    metadata.add_column('age', sdtype='numerical')
    metadata.add_column('sibsp', sdtype='numerical')
    metadata.add_column('parch', sdtype='numerical')
    metadata.add_column('fare', sdtype='numerical')
    metadata.add_column('embarked', sdtype='categorical')
    metadata.add_column('survived', sdtype='categorical')

    # Evaluate the synthetic data
    scores = evaluate_data_quality(synthetic_data, real_data, metadata)

    # Return the scores as a JSON response
    return JSONResponse(content=scores)


