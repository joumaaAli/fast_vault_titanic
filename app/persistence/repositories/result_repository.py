# result_repository.py
from app.db.session import get_db
from app.db.models.result import DBResult

class ResultRepository:
    def __init__(self):
        self.db = next(get_db())

    def create_result(self, task_id: int, accuracy: float):
        new_result = DBResult(task_id=task_id, accuracy=accuracy)
        self.db.add(new_result)
        self.db.commit()

    def get_result_by_task_id(self, task_id: int):
        return self.db.query(DBResult).filter(DBResult.task_id == task_id).first()
