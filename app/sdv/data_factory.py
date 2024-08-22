import pandas as pd
from sqlalchemy.orm import Session
from app.database import DataRecord, SyntheticData

class DataFactory:
    @staticmethod
    def get_data(data_type: str, db: Session):
        if data_type == "simple":
            records = db.query(DataRecord).all()
            data = pd.DataFrame([{
                'id': record.id,
                'arrival_date': record.arrival_date,
                'efficiency': record.efficiency,
                'leaving_date': record.leaving_date
            } for record in records])
            return data
        else:
            raise ValueError("Unsupported data type")

    @staticmethod
    def get_synthetic_data(synthesizer_type: str, db: Session):
        synthetic_data_record = db.query(SyntheticData).filter(SyntheticData.synthesizer_type == synthesizer_type).order_by(SyntheticData.id.desc()).first()

        if not synthetic_data_record:
            raise ValueError("No synthetic data found for this synthesizer type")

        synthetic_data = pd.read_json(synthetic_data_record.data)
        return synthetic_data
