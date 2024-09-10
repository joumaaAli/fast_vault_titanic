from sqlalchemy.orm import Session
from app.db.models.synthetic_data import DBSyntheticData
from app.entities.synthetic_data import SyntheticData
from app.db.session import get_db
import pandas as pd

class SyntheticDataRepository:
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())

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
