# app/repository.py

from sqlalchemy.orm import Session
from app.common.models import DataRecord, SyntheticData
import pandas as pd

def get_all_data_records(db: Session):
    return db.query(DataRecord).all()

def get_synthetic_data_by_id(db: Session, synthetic_data_id: int):
   return db.query(SyntheticData).filter_by(id=synthetic_data_id).first()

def save_synthetic_data(db: Session, synthetic_data: SyntheticData):
    db.add(synthetic_data)
    db.commit()
    db.refresh(synthetic_data)
    return synthetic_data

def convert_data_records_to_dataframe(data_records):
    return pd.DataFrame([{
        'id': record.id,
        'pclass': record.pclass,
        'sex': record.sex,
        'age': record.age,
        'sibsp': record.sibsp,
        'parch': record.parch,
        'fare': record.fare,
        'embarked': record.embarked,
        'survived': record.survived
    } for record in data_records])
