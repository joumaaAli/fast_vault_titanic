import json
import logging
import os

import joblib
import pandas as pd
from sdv.metadata import SingleTableMetadata
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from app.core.config import settings
from app.crud.data_record import get_all_data_records_from_csv
from app.crud.synthetic import get_synthetic_data_by_id, save_synthetic_data
from app.utils.anonymize import anonymize_data
from app.utils.evaluators import evaluate_data_quality
from app.utils.factories import SynthesizerFactory

logger = logging.getLogger(__name__)

csv_path = settings.csv

def generate_synthetic_data(db, synthesizer_type: str):
    logger.info(f"Starting synthetic data generation with synthesizer type: {synthesizer_type}")

    # Load the CSV and convert columns to lowercase
    data = get_all_data_records_from_csv(csv_path)
    data.columns = data.columns.str.lower()  # Normalize column names to lowercase

    original_data_ids = list(data['passengerid']) if 'passengerid' in data.columns else []

    # Drop 'name', 'email', 'ticket', and 'cabin' columns
    data = data.drop(columns=['name', 'email', 'ticket', 'cabin'], errors='ignore')

    sensitive_columns = []  # No sensitive columns to anonymize now
    data = anonymize_data(data, sensitive_columns)

    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(data)

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

    # Load real data
    real_data = get_all_data_records_from_csv(csv_path)
    synthetic_data = pd.read_json(synthetic_data_record.data)

    # Normalize column names
    real_data.columns = real_data.columns.str.lower()
    synthetic_data.columns = synthetic_data.columns.str.lower()

    # Drop irrelevant columns from both real and synthetic data
    columns_to_drop = ['name', 'email', 'ticket', 'cabin']
    real_data = real_data.drop(columns=[col for col in columns_to_drop if col in real_data.columns], errors='ignore')
    synthetic_data = synthetic_data.drop(columns=[col for col in columns_to_drop if col in synthetic_data.columns], errors='ignore')

    # Create metadata that reflects all columns in the data
    metadata = SingleTableMetadata()
    for column in real_data.columns:
        if column in ['age', 'fare']:
            metadata.add_column(column, sdtype='numerical')
        else:
            metadata.add_column(column, sdtype='categorical')  # Default to categorical if not specified

    # Check if any columns are missing before evaluation
    missing_columns = set(real_data.columns).difference(synthetic_data.columns)
    if missing_columns:
        raise ValueError(f"Missing columns in synthetic data: {missing_columns}")

    # Evaluate data quality
    scores = evaluate_data_quality(synthetic_data, real_data, metadata)
    return scores

def augment_and_train(db, synthesizer_type: str, augmentation_factor: int):
    logger.info(
        f"Starting data augmentation and training with synthesizer type: {synthesizer_type}, augmentation factor: {augmentation_factor}")

    # Load the CSV and convert columns to lowercase
    data = get_all_data_records_from_csv(csv_path)
    data.columns = data.columns.str.lower()  # Normalize column names to lowercase

    # Drop 'name', 'email', 'ticket', and 'cabin' columns
    data = data.drop(columns=['name', 'email', 'ticket', 'cabin'], errors='ignore')

    # One-hot encode categorical variables
    categorical_columns = ['sex', 'embarked', 'pclass']  # Add all categorical columns you need to encode
    data = pd.get_dummies(data, columns=categorical_columns, drop_first=True)

    # Create metadata for SDV
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(data)

    # Fit synthesizer
    synthesizer = SynthesizerFactory.get_synthesizer(synthesizer_type, metadata)
    synthesizer.fit(data)

    # Generate synthetic data
    synthetic_data = synthesizer.sample(num_rows=len(data) * augmentation_factor)

    # Combine original and synthetic data
    augmented_data = pd.concat([data, synthetic_data], ignore_index=True)

    # Separate features (X) and target (y)
    X = augmented_data.drop(columns=['survived'])  # Features
    y = augmented_data['survived']  # Target

    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train a RandomForest model
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    # Save the trained model
    model_path = os.path.join(os.getcwd(), "model.joblib")
    joblib.dump(model, model_path)

    # Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    logger.info(f"Model training completed successfully with accuracy: {accuracy}")
    return accuracy
