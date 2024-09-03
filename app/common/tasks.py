import logging
import os

import joblib
import pandas as pd
import simplejson as json
from fastapi import HTTPException
from sdv.metadata import SingleTableMetadata
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sqlalchemy.orm import Session

from app.common.models import User, SyntheticData, DataRecord
from app.common.utils import anonymize_data
from app.repository import get_all_data_records, convert_data_records_to_dataframe, save_synthetic_data, \
    get_synthetic_data_by_id
from app.sdv.evaluators import evaluate_data_quality
from app.sdv.factories import SynthesizerFactory

logger = logging.getLogger(__name__)


def generate_synthetic_data_task(synthesizer_type: str, current_user_id: int):
    from app.database import SessionLocal
    logger.info(f"Starting synthetic data generation with synthesizer type: {synthesizer_type}")
    try:
        # Create a new database session within the task
        db = SessionLocal()
        # Perform the task using the session
        data_records = get_all_data_records(db)
        data = convert_data_records_to_dataframe(data_records)
        original_data_ids = list(data['id'])
        data = data.drop(columns=['id', 'cabin'], errors='ignore')
        sensitive_columns = ['name', 'email', 'ticket']
        data = anonymize_data(data, sensitive_columns)

        metadata = SingleTableMetadata()
        metadata.detect_from_dataframe(data)

        synthesizer = SynthesizerFactory.get_synthesizer(synthesizer_type, metadata)
        synthesizer.fit(data)

        synthetic_data = synthesizer.sample(num_rows=len(data))
        synthetic_data_json = synthetic_data.to_json(orient='records')

        new_synthetic_data = SyntheticData(
            synthesizer_type=synthesizer_type,
            data=synthetic_data_json,
            original_data_ids=json.dumps(original_data_ids),
        )
        saved_synthetic_data = save_synthetic_data(db, new_synthetic_data)

        logger.info(f"Synthetic data generation completed successfully. ID: {saved_synthetic_data.id}")
        return saved_synthetic_data.id
    except Exception as e:
        logger.error(f"Error during synthetic data generation: {e}")
        raise
    finally:
        db.close()  # Make sure to close the session after the task is done


def augment_and_train_task(synthesizer_type: str, augmentation_factor: int, current_user: User):
    from app.database import SessionLocal  # Importing here to avoid circular imports
    logger.info(
        f"Starting data augmentation and training with synthesizer type: {synthesizer_type}, augmentation factor: {augmentation_factor}")

    try:
        # Create a new database session within the task
        with SessionLocal() as db:
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

            logger.info(f"Model training completed successfully with accuracy: {accuracy}")
            return accuracy
    except Exception as e:
        logger.error(f"Error during data augmentation and training: {e}")
        raise


def evaluate_synthetic_data_task(synthetic_data_id: int):
    from app.database import SessionLocal  # Importing here to avoid circular imports
    logger.info(f"Starting synthetic data evaluation for ID: {synthetic_data_id}")

    try:
        # Create a new database session within the task
        with SessionLocal() as db:
            synthetic_data_record = get_synthetic_data_by_id(db, synthetic_data_id)
            if not synthetic_data_record:
                logger.error(f"Synthetic data with ID {synthetic_data_id} not found")
                raise HTTPException(status_code=404, detail="Synthetic data not found")

            original_data_ids = json.loads(synthetic_data_record.original_data_ids)
            original_data_records = db.query(DataRecord).filter(DataRecord.id.in_(original_data_ids)).all()
            real_data = convert_data_records_to_dataframe(original_data_records)
            synthetic_data = pd.read_json(synthetic_data_record.data)

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

            scores = evaluate_data_quality(synthetic_data, real_data, metadata)

            logger.info(f"Synthetic data evaluation completed for ID: {synthetic_data_id}")
            return scores
    except Exception as e:
        logger.error(f"Error during synthetic data evaluation: {e}")
        raise
