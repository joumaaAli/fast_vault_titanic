import uuid

from app.db.session import get_db
from app.db.models.task_status import DBTaskStatus, TaskStatusEnum
from app.entities.task_status import TaskStatus as TaskStatusEntity

class TaskStatusRepository:
    def __init__(self):
        self.db = next(get_db())

    def create_task(self, description: str, created_at):
        """
        Creates a task with the given description and created_at timestamp.
        """
        # Create a new task with the given description, created_at, and queued status
        new_task = DBTaskStatus(
            status=TaskStatusEnum.QUEUED,
            description=description,
            created_at=created_at,
        )
        self.db.add(new_task)
        self.db.commit()
        self.db.refresh(new_task)
        return TaskStatusEntity.model_validate(new_task).id

    def update_task_status(self, task_id: int, status: TaskStatusEnum, accuracy=None, error=None):
        task = self.db.query(DBTaskStatus).filter(DBTaskStatus.id == task_id).first()
        if task:
            task.status = status
            task.accuracy = accuracy
            task.error = error
            self.db.commit()

    def get_task(self, task_id: int):
        return self.db.query(DBTaskStatus).filter(DBTaskStatus.id == task_id).first()


    def get_task_status(self, task_id: int):

        task = self.db.query(DBTaskStatus).filter(DBTaskStatus.id == task_id).first()
        return task.status if task else None