from pydantic import BaseModel
from typing import Optional

class SyntheticData(BaseModel):
    id: Optional[int]
    synthesizer_type: str
    data: str
    original_data_ids: str
    model_config = {
        'from_attributes': True
    }