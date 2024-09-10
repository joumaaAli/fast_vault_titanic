from app.entities.task_status import TaskStatusEnum
from app.persistence.repositories.task_status_repository import TaskStatusRepository


class TaskStatusService:
    def __init__(self, task_repository: TaskStatusRepository):
        self.task_repository = task_repository

    def create_task(self, description: str):
        return self.task_repository.create_task(description)

    def update_task_status(self, task_id: int, status: TaskStatusEnum, accuracy=None, error=None):
        self.task_repository.update_task_status(task_id, status, accuracy, error)

    def get_task_status(self, task_id: int):
        """
        Get the current status of the task.
        """
        return self.task_repository.get_task_status(task_id)
