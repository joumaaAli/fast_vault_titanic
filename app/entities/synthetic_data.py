from pydantic import BaseModel
from typing import Optional
from enum import Enum

class SyntheticData(BaseModel):
    id: Optional[int]
    synthesizer_type: str
    data: str
    original_data_ids: str
    model_config = {
        'from_attributes': True
    }

class SynthesizerType(str, Enum):
    ctgan = "ctgan"
    copulagan = "copulagan"
    gaussiancopula = "gaussiancopula"

class SyntheticDataCreate(BaseModel):
    synthesizer_type: str
    data: str
    original_data_ids: str

class SyntheticDataResponse(BaseModel):
    id: int
