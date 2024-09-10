from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base

class DBResult(Base):
    __tablename__ = "results"

    task_id = Column(Integer, ForeignKey('task_status.id'), primary_key=True)
    accuracy = Column(Float, nullable=False)

    task_status = relationship("DBTaskStatus", back_populates="result")
