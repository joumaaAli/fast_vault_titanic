from sqlalchemy import Column, Integer, String
from app.db.base import Base

class DBSyntheticData(Base):
    __tablename__ = 'synthetic_data_titanic'
    id = Column(Integer, primary_key=True, index=True)
    synthesizer_type = Column(String, index=True)
    data = Column(String)
    original_data_ids = Column(String)
