from sqlalchemy import create_engine, Column, Integer, String, Date, Float, Text, ForeignKey, Boolean
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

class SyntheticData(Base):
    __tablename__ = 'synthetic_data_titanic'

    id = Column(Integer, primary_key=True, index=True)
    synthesizer_type = Column(String, index=True)
    data = Column(String)
    original_data_ids = Column(String)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)
