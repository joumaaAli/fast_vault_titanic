import json
import logging

from app.core.config import settings
from app.entities.synthetic_data import SynthesizerType

logger = logging.getLogger(__name__)

csv_path = settings.csv

import pandas as pd
import logging
import os
import joblib
from app.use_cases.services.hasher import Hasher
from app.use_cases.factories.factories import SynthesizerFactory
from app.use_cases.evaluators.evaluators import Evaluator
from sdv.metadata import SingleTableMetadata
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from app.persistence.repositories.synthetic_data_repository import SyntheticDataRepository


logger = logging.getLogger(__name__)

data_anonymizer = Hasher()

syntheticDataRepository = SyntheticDataRepository()

class DataService:
    """Service layer for handling synthetic data operations."""

    def __init__(self, factory: SynthesizerFactory, evaluator: Evaluator, csv_path: str):
        self.factory = factory
        self.evaluator = evaluator
        self.csv_path = csv_path

    def generate_synthetic_data(self, synthesizer_type: SynthesizerType):
        """Generate synthetic data based on the specified synthesizer type."""
        logger.info(f"Starting synthetic data generation with synthesizer type: {synthesizer_type}")

        # Load real data from CSV
        data = syntheticDataRepository.get_all_data_records_from_csv(self.csv_path)
        data.columns = data.columns.str.lower()
        original_data_ids = list(data['passengerid']) if 'passengerid' in data.columns else []

        # Clean and anonymize the data
        data = data.drop(columns=['name', 'email', 'ticket', 'cabin'], errors='ignore')
        data = data_anonymizer.anonymize_data(data, ['name', 'email', 'ticket', 'cabin'])

        # Create metadata for SDV
        metadata = SingleTableMetadata()
        metadata.detect_from_dataframe(data)

        # Generate synthetic data
        synthesizer = self.factory.get_synthesizer(synthesizer_type, metadata)
        synthesizer.fit(data)
        synthetic_data = synthesizer.sample(num_rows=len(data))

        # Save the synthetic data to the database
        synthetic_data_json = synthetic_data.to_json(orient='records')
        synthetic_data_id = syntheticDataRepository.save_synthetic_data(synthesizer_type.value, synthetic_data_json,
                                                json.dumps(original_data_ids))

        logger.info(f"Synthetic data generation completed with ID: {synthetic_data_id}")
        return synthetic_data_id

    def evaluate_synthetic_data(self, synthetic_data_id: int):
        """Evaluate the quality of the generated synthetic data."""
        # Retrieve synthetic data from the database
        synthetic_data_record = syntheticDataRepository.get_synthetic_data_by_id(synthetic_data_id)
        if not synthetic_data_record:
            raise ValueError("Synthetic data not found")

        # Load real data from CSV
        real_data = syntheticDataRepository.get_all_data_records_from_csv(self.csv_path)
        synthetic_data = pd.read_json(synthetic_data_record.data)

        real_data.columns = real_data.columns.str.lower()
        synthetic_data.columns = synthetic_data.columns.str.lower()

        # Clean data
        real_data = real_data.drop(columns=['name', 'email', 'ticket', 'cabin'], errors='ignore')
        synthetic_data = synthetic_data.drop(columns=['name', 'email', 'ticket', 'cabin'], errors='ignore')

        # Create metadata for evaluation
        metadata = SingleTableMetadata()
        for column in real_data.columns:
            metadata.add_column(column, sdtype='numerical' if column in ['age', 'fare'] else 'categorical')

        # Perform evaluation
        scores = self.evaluator.evaluate_data_quality(synthetic_data, real_data, metadata)
        return scores

    def augment_and_train(self, synthesizer_type: SynthesizerType, augmentation_factor: int):
        """Augment data and train a machine learning model."""
        logger.info(
            f"Starting data augmentation and training with synthesizer type: {synthesizer_type}, augmentation factor: {augmentation_factor}")

        # Load real data from CSV
        data = syntheticDataRepository.get_all_data_records_from_csv(self.csv_path)
        data.columns = data.columns.str.lower()
        data = data.drop(columns=['name', 'email', 'ticket', 'cabin'], errors='ignore')

        # One-hot encode categorical variables
        data = pd.get_dummies(data, columns=['sex', 'embarked', 'pclass'], drop_first=True)

        # Create metadata
        metadata = SingleTableMetadata()
        metadata.detect_from_dataframe(data)

        # Generate synthetic data
        synthesizer = self.factory.get_synthesizer(synthesizer_type, metadata)
        synthesizer.fit(data)
        synthetic_data = synthesizer.sample(num_rows=len(data) * augmentation_factor)

        # Combine original and synthetic data
        augmented_data = pd.concat([data, synthetic_data], ignore_index=True)
        X = augmented_data.drop(columns=['survived'])  # Features
        y = augmented_data['survived']  # Target

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train RandomForest model
        model = RandomForestClassifier(random_state=42)
        model.fit(X_train, y_train)

        # Save and evaluate the model
        model_path = os.path.join(os.getcwd(), "model.joblib")
        joblib.dump(model, model_path)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        logger.info(f"Model training completed successfully with accuracy: {accuracy}")
        return accuracy


