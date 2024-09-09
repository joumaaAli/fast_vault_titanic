from sqlalchemy.orm import Session
from app.db.models.synthetic_data import DBSyntheticData
from app.entities.synthetic_data import SyntheticData
from app.db.session import get_db

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

    def close(self):
        """Close the database session."""
        self.db.close()
