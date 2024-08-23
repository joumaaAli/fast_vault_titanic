from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, String, Integer, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(BaseModel):
    username: str
    email: EmailStr  # Adding email for registration
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None


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
    data = Column(String)  # Store data as a JSON string
    original_data_ids = Column(String)  # Store the list of original data IDs as a JSON string

class PredictionInput(BaseModel):
    pclass: int
    sex: int  # Assuming you've encoded 'sex' as 0 for male, 1 for female
    age: float
    sibsp: int
    parch: int
    fare: float
    embarked: int  #