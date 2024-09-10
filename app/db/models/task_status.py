import datetime

from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.entities.task_status import TaskStatusEnum


class DBTaskStatus(Base):
    __tablename__ = "task_status"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default=TaskStatusEnum.QUEUED)
    description = Column(String, nullable=True)
    accuracy = Column(String, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    result = relationship("DBResult", uselist=False, back_populates="task_status")
