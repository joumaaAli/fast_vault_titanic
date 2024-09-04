from app.crud.data_record import get_all_data_records, convert_data_records_to_dataframe
from app.db.session import SessionLocal
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pandas as pd
import json
import logging

logger = logging.getLogger(__name__)

def train_model(training_data_id: int):
    with SessionLocal() as db:
        logger.info(f"Starting model training with data ID: {training_data_id}")

        data_records = get_all_data_records(db)
        data = convert_data_records_to_dataframe(data_records)
        if 'id' in data.columns:
            data = data.drop(columns=['id'])

        X = data.drop(columns=['survived'])
        y = data['survived']

        model = RandomForestClassifier()
        model.fit(X, y)

        # Simulate model training score
        predictions = model.predict(X)
        accuracy = accuracy_score(y, predictions)
        logger.info(f"Model training completed with accuracy: {accuracy:.2f}")

        return accuracy
