import pandas as pd
from sqlalchemy.orm import Session

from app.db.models.data_record import DBDataRecord
from app.entities.data_record import DataRecord
from app.entities.synthetic_data import SyntheticData
from app.db.models.synthetic_data import DBSyntheticData


def get_synthetic_data_by_id(db: Session, synthetic_data_id: int):
    db_record = db.query(DBSyntheticData).filter(DBSyntheticData.id == synthetic_data_id).first()
    if db_record:
        return SyntheticData.validate(db_record)
    return None


def save_synthetic_data(db: Session, synthesizer_type: str, data: str, original_data_ids: str) -> SyntheticData:
    db_record = DBSyntheticData(
        synthesizer_type=synthesizer_type,
        data=data,
        original_data_ids=original_data_ids
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    # Return the SyntheticData instance with the assigned id from the database
    return SyntheticData.model_validate(db_record)


def get_all_data_records(db: Session):
    db_records = db.query(DBDataRecord).all()
    return [DataRecord.model_validate(record) for record in db_records]

def convert_data_records_to_dataframe(records):
    return pd.DataFrame([record.dict() for record in records])