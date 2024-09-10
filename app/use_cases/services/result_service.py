# result_service.py
from app.persistence.repositories.result_repository import ResultRepository


class ResultService:
    def __init__(self, result_repository: ResultRepository):
        self.result_repository = result_repository

    def create_result(self, task_id: int, accuracy: float):
        return self.result_repository.create_result(task_id, accuracy)

    def get_result_by_task_id(self, task_id: int):
        return self.result_repository.get_result_by_task_id(task_id)
