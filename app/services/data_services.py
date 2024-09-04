import json
import logging
import os

import joblib
import pandas as pd
from sdv.metadata import SingleTableMetadata
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from app.crud.data_record import get_all_data_records, convert_data_records_to_dataframe
from app.crud.synthetic import get_synthetic_data_by_id, save_synthetic_data
from app.entities.synthetic_data import SyntheticData
from app.utils.anonymize import anonymize_data
from app.utils.evaluators import evaluate_data_quality
from app.utils.factories import SynthesizerFactory

logger = logging.getLogger(__name__)


def generate_synthetic_data(db, synthesizer_type: str):
    logger.info(f"Starting synthetic data generation with synthesizer type: {synthesizer_type}")

    data_records = get_all_data_records(db)
    data = convert_data_records_to_dataframe(data_records)
    original_data_ids = list(data['id'])

    # Drop 'name', 'email', 'ticket', and 'cabin' columns
    data = data.drop(columns=['id', 'name', 'email', 'ticket', 'cabin'], errors='ignore')

    sensitive_columns = []  # No sensitive columns to anonymize now
    data = anonymize_data(data, sensitive_columns)

    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(data)  # Ensure metadata reflects all columns

    synthesizer = SynthesizerFactory.get_synthesizer(synthesizer_type, metadata)
    synthesizer.fit(data)

    synthetic_data = synthesizer.sample(num_rows=len(data))
    synthetic_data_json = synthetic_data.to_json(orient='records')

    # Save to database
    saved_synthetic_data = save_synthetic_data(
        db,
        synthesizer_type=synthesizer_type,
        data=synthetic_data_json,
        original_data_ids=json.dumps(original_data_ids)
    )

    logger.info(f"Synthetic data generation completed successfully. ID: {saved_synthetic_data.id}")
    return saved_synthetic_data.id

def evaluate_synthetic_data(db, synthetic_data_id: int):
    synthetic_data_record = get_synthetic_data_by_id(db, synthetic_data_id)
    if not synthetic_data_record:
        raise ValueError("Synthetic data not found")

    original_data_ids = json.loads(synthetic_data_record.original_data_ids)
    original_data_records = get_all_data_records(db)
    real_data = convert_data_records_to_dataframe(original_data_records)
    synthetic_data = pd.read_json(synthetic_data_record.data)

    # Drop columns that are not used for evaluation
    real_data = real_data.drop(columns=['id', 'name', 'email', 'ticket', 'cabin'], errors='ignore')
    synthetic_data = synthetic_data.drop(columns=['id', 'name', 'email', 'ticket', 'cabin'], errors='ignore')

    # Create metadata that reflects all columns in the data
    metadata = SingleTableMetadata()
    for column in real_data.columns:
        if column == 'age':
            metadata.add_column(column, sdtype='numerical')
        else:
            metadata.add_column(column, sdtype='categorical')  # Default to categorical if not specified

    scores = evaluate_data_quality(synthetic_data, real_data, metadata)
    return scores

def augment_and_train(db, synthesizer_type: str, augmentation_factor: int):
    logger.info(
        f"Starting data augmentation and training with synthesizer type: {synthesizer_type}, augmentation factor: {augmentation_factor}")

    data_records = get_all_data_records(db)
    data = convert_data_records_to_dataframe(data_records)

    # Drop 'name', 'email', 'ticket', and 'cabin' columns
    data = data.drop(columns=['id', 'name', 'email', 'ticket', 'cabin'], errors='ignore')

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

    logger.info(f"Model training completed successfully with accuracy: {accuracy}")
    return accuracy
