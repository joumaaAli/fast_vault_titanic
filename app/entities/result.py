from sqlalchemy.orm import relationship
from pydantic import BaseModel

class Result(BaseModel):
    task_id: int
    accuracy: float
    task_status: str
    model_config = {
        'from_attributes': True
    }
