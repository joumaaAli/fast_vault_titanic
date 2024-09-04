from pydantic import BaseModel
from typing import List, Optional

class SyntheticDataCreate(BaseModel):
    synthesizer_type: str
    data: str
    original_data_ids: str

class SyntheticDataResponse(BaseModel):
    id: int
