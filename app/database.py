from sqlalchemy import create_engine, Column, Integer, String, Date, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
import json

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)  # Add email field
    hashed_password = Column(String)

    def set_password(self, password):
        self.hashed_password = pwd_context.hash(password)

class DataRecord(Base):
    __tablename__ = 'data_records'

    id = Column(Integer, primary_key=True, index=True)
    arrival_date = Column(Date, nullable=False)
    efficiency = Column(Float, nullable=False)
    leaving_date = Column(Date, nullable=False)

class SyntheticData(Base):
    __tablename__ = 'synthetic_data'

    id = Column(Integer, primary_key=True, index=True)
    synthesizer_type = Column(String, index=True)
    data = Column(Text)  # Store data as a JSON string
    original_data_ids = Column(Text)  # Store the list of original data IDs as a JSON string

    def __init__(self, synthesizer_type, data, original_data_ids):
        self.synthesizer_type = synthesizer_type
        self.data = data
        self.original_data_ids = json.dumps(original_data_ids)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)
