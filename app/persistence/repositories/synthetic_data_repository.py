import pandas as pd

from app.db.models.synthetic_data import DBSyntheticData
from app.db.session import get_db
from app.entities.synthetic_data import SyntheticData


class SyntheticDataRepository:
    """
       Repository class for handling operations related to synthetic data.

       Methods:
           get_synthetic_data_by_id(synthetic_data_id): Fetches synthetic data by ID.
           save_synthetic_data(synthesizer_type, data, original_data_ids): Saves new synthetic data.
           get_all_data_records_from_csv(csv_path): Reads and returns all records from a CSV file.
   """
    def __init__(self):
        self.db = next(get_db())

    def get_synthetic_data_by_id(self, synthetic_data_id: int) -> SyntheticData | None:
        """Fetch synthetic data by ID."""
        db_record = self.db.query(DBSyntheticData).filter(DBSyntheticData.id == synthetic_data_id).first()
        if db_record:
            return SyntheticData.model_validate(db_record)
        return None

    def save_synthetic_data(self, synthesizer_type: str, data: str, original_data_ids: str) -> SyntheticData:
        """Save new synthetic data."""
        db_record = DBSyntheticData(
            synthesizer_type=synthesizer_type,
            data=data,
            original_data_ids=original_data_ids
        )
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return SyntheticData.model_validate(db_record)

    def get_all_data_records_from_csv(self, csv_path: str) -> pd.DataFrame:
        try:
            data = pd.read_csv(csv_path)
            return data
        except FileNotFoundError as e:
            raise ValueError("CSV file not found.")
        except Exception as e:
            raise ValueError("Error reading CSV file.")

    def close(self):
        """Close the database session."""
        self.db.close()
