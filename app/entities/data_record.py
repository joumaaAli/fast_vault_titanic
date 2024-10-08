from typing import Optional
from pydantic import BaseModel

class DataRecord(BaseModel):
    id: int
    survived: bool
    pclass: int
    name: str
    sex: str
    age: Optional[float]
    sibsp: int
    parch: int
    fare: float
    embarked: Optional[str]
    model_config = {
        'from_attributes': True
    }
