from sqlalchemy.orm import Session
from app.db.models.data_record import DBDataRecord
from app.entities.data_record import DataRecord
import pandas as pd

def get_all_data_records(db: Session):
    db_records = db.query(DBDataRecord).all()
    return [DataRecord.model_validate(record) for record in db_records]

def convert_data_records_to_dataframe(records):
    return pd.DataFrame([record.dict() for record in records])
