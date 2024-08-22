from sqlalchemy.orm import Session
from datetime import datetime

from app.database import DataRecord, SessionLocal


def populate_database():
    db: Session = SessionLocal()
    records = [
        DataRecord(arrival_date=datetime(2023, 1, 1), efficiency=80, leaving_date=datetime(2023, 1, 2)),
        DataRecord(arrival_date=datetime(2023, 2, 1), efficiency=85, leaving_date=datetime(2023, 2, 2)),
        DataRecord(arrival_date=datetime(2023, 3, 1), efficiency=90, leaving_date=datetime(2023, 3, 2)),
    ]
    db.add_all(records)
    db.commit()

populate_database()
