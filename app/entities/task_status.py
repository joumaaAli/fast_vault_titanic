import enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class TaskStatusEnum(str, enum.Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskStatus(BaseModel):
    status: TaskStatusEnum
    accuracy: Optional[float] = None
    error: Optional[str] = None
    description: Optional[str] = None
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None  # Mark updated_at as optional
    model_config = {
        'from_attributes': True
    }
