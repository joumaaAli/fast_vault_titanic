from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, SyntheticData, DataRecord
from app.auth.utils import get_current_user
from app.sdv.evaluators import evaluate_synthetic_data
from app.sdv.factories import SynthesizerFactory
from app.sdv.data_factory import DataFactory
from app.common.models import User
from sdv.metadata import SingleTableMetadata
import pandas as pd
import json
import numpy as np
router = APIRouter()

@router.post("/generate_data/")
async def generate_data(synthesizer_type: str = "ctgan", data_type: str = "simple",
                        db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        data = DataFactory.get_data(data_type, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Store the IDs of the original data
    original_data_ids = data['id'].tolist()

    # Exclude the 'id' column from the data
    data = data.drop(columns=['id'], errors='ignore')

    # Create metadata based on the data without 'id'
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(data)

    try:
        synthesizer = SynthesizerFactory.get_synthesizer(synthesizer_type, metadata)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    synthesizer.fit(data)
    synthetic_data = synthesizer.sample(num_rows=5)

    # Convert numpy types if needed
    synthetic_data = synthetic_data.applymap(lambda x: int(x) if isinstance(x, (np.int64, np.int32)) else x)

    # Store the synthetic data in the database
    synthetic_data_json = synthetic_data.to_json(orient='records')

    new_synthetic_data = SyntheticData(
        synthesizer_type=synthesizer_type,
        data=synthetic_data_json,
        original_data_ids=original_data_ids
    )
    db.add(new_synthetic_data)
    db.commit()

    return synthetic_data.to_dict(orient='records')

@router.post("/evaluate_data/")
async def evaluate_data(synthetic_data_id: int, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    # Retrieve the synthetic data record by ID
    synthetic_data_record = db.query(SyntheticData).filter(SyntheticData.id == synthetic_data_id).first()

    if not synthetic_data_record:
        raise HTTPException(status_code=404, detail="Synthetic data not found")

    # Retrieve the original data associated with the synthetic data using the stored IDs
    original_data_ids = json.loads(synthetic_data_record.original_data_ids)
    original_data = db.query(DataRecord).filter(DataRecord.id.in_(original_data_ids)).all()

    if not original_data:
        raise HTTPException(status_code=404, detail="Original data not found")

    # Convert original data to DataFrame
    real_data = pd.DataFrame([{
        'arrival_date': record.arrival_date,
        'efficiency': record.efficiency,
        'leaving_date': record.leaving_date
    } for record in original_data])

    # Convert synthetic data JSON back to DataFrame
    synthetic_data = pd.read_json(synthetic_data_record.data)

    # Exclude the 'id' column from synthetic data if it exists
    synthetic_data = synthetic_data.drop(columns=['id'], errors='ignore')

    # Create metadata based on the real data without 'id'
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(real_data)

    # Evaluate the synthetic data without considering the 'id' column
    score = evaluate_synthetic_data(synthetic_data, real_data, metadata)

    return {"score": score}
