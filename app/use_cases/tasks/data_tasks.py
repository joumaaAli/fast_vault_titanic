import logging

from app.entities.synthetic_data import SynthesizerType
from app.entities.task_status import TaskStatusEnum
from app.persistence.repositories.result_repository import ResultRepository
from app.persistence.repositories.task_status_repository import TaskStatusRepository
from app.use_cases.services.data_service import DataService

logger = logging.getLogger(__name__)

result_repository =  ResultRepository()

class DataTask:

    def run_augment_and_train_task(
            task_id: int, synthesizer_type: SynthesizerType, augmentation_factor: int, data_service: DataService,
            task_repository: TaskStatusRepository,
    ):
        try:
            task_repository.update_task_status(task_id, TaskStatusEnum.IN_PROGRESS)

            accuracy = data_service.augment_and_train(synthesizer_type, augmentation_factor)

            # Save the result
            result_repository.create_result(task_id, accuracy)

            task_repository.update_task_status(task_id, TaskStatusEnum.COMPLETED, accuracy=accuracy)

        except Exception as e:
            logger.error(f"Error during data augmentation and training: {e}")
            task_repository.update_task_status(task_id, TaskStatusEnum.FAILED, error=str(e))
