from sqlalchemy import Column, Integer, String, Float, Boolean
from app.db.base import Base

class DBDataRecord(Base):
    __tablename__ = 'data_records_titanic'
    id = Column(Integer, primary_key=True, index=True)
    survived = Column(Boolean, nullable=False)
    pclass = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    sex = Column(String, nullable=False)
    age = Column(Float, nullable=True)
    sibsp = Column(Integer, nullable=False)
    parch = Column(Integer, nullable=False)
    ticket = Column(String, nullable=False)
    fare = Column(Float, nullable=False)
    cabin = Column(String, nullable=True)
    embarked = Column(String, nullable=True)
