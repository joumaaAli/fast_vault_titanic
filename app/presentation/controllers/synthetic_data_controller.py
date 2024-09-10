import logging
from fastapi import APIRouter, HTTPException, Request, Depends, BackgroundTasks
from dependency_injector.wiring import inject, Provide
from app.entities.synthetic_data import SynthesizerType
from app.persistence.repositories.task_status_repository import TaskStatusRepository
from app.use_cases.services.data_service import DataService
from app.container import AppContainer
from app.use_cases.services.result_service import ResultService
from app.use_cases.services.task_status_service import TaskStatusService
from app.use_cases.tasks.data_tasks import DataTask

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate/")
@inject
async def generate_synthetic_data_endpoint(
    request: Request,
    synthesizer_type: SynthesizerType,
    data_service: DataService = Depends(Provide[AppContainer.data_service])
):
    """
        Endpoint to generate synthetic data based on a specified synthesizer type.

        Args:
            request (Request): The request object.
            synthesizer_type (SynthesizerType): Type of synthesizer to use.
            data_service (DataService): Data service to handle data generation logic.

        Returns:
            dict: Synthetic data ID and synthesizer type used.
    """
    try:
        synthetic_data_id = data_service.generate_synthetic_data(synthesizer_type)
        return {"id": synthetic_data_id, "synthesizer_type": synthesizer_type.value}
    except Exception as e:
        logger.error(f"Error during synthetic data generation: {e}")
        raise HTTPException(status_code=500, detail="Error generating synthetic data")


@router.post("/augment-and-train/")
@inject
async def augment_and_train_endpoint(
    background_tasks: BackgroundTasks,
    synthesizer_type: SynthesizerType,
    augmentation_factor: int = 2,
    description: str = "Data augmentation and training",
    task_status_service: TaskStatusService = Depends(Provide[AppContainer.task_status_service]),
    data_service: DataService = Depends(Provide[AppContainer.data_service]),
):
    """
        Endpoint to start an asynchronous data augmentation and model training process.

        Args:
            background_tasks (BackgroundTasks): Background tasks to handle async processes.
            synthesizer_type (SynthesizerType): Type of synthesizer to use.
            augmentation_factor (int): Factor by which to augment the data.
            description (str): Description of the task.
            task_status_service (TaskStatusService): Service to handle task statuses.
            data_service (DataService): Service to handle data augmentation and training.

        Returns:
            dict: Task ID and initiation status.
        """
    try:
        # Create the task using the TaskService, including a description and created_at timestamp
        task_id = task_status_service.create_task(description)

        # Add the background task to run the training asynchronously
        background_tasks.add_task(
            DataTask.run_augment_and_train_task,
            task_id,
            synthesizer_type,
            augmentation_factor,
            data_service,
            task_status_service,
        )

        # Return the task ID to the user so they can check the status later
        return {"task_id": task_id, "status": "Task initiated. Check status with the task_id"}
    except Exception as e:
        logger.error(f"Error initiating model training: {e}")
        raise HTTPException(status_code=500, detail="Error initiating data augmentation and training")

@router.post("/evaluate/")
@inject
async def evaluate_synthetic_data_endpoint(
    request: Request,
    synthetic_data_id: int,
    data_service: DataService = Depends(Provide[AppContainer.data_service])
):
    """"
    Endpoint to evaluate a synthetic data based on a specified synthesizer type.
    Args:
        request (Request): The request object.
        synthetic_data_id (int): Synthetic data ID.
        data_service (DataService): Data service to handle data evaluation.
    Returns:
        score: score of the evaluted synthetic data
    """
    try:
        scores = data_service.evaluate_synthetic_data(synthetic_data_id)
        return scores
    except Exception as e:
        logger.error(f"Error during evaluation: {e}")
        raise HTTPException(status_code=500, detail="Error during evaluation of synthetic data")

@router.get("/result/{task_id}")
@inject
async def get_result_by_task_id(
    task_id: str,
    result_service: ResultService = Depends(Provide[AppContainer.result_service])
):
    """
     Endpoint to retrieve the accuracy of a task result by task ID.

     Args:
         task_id (str): ID of the task.
         result_service (ResultService): Service to fetch result data.

     Returns:
         dict: Task ID and accuracy.
     """
    try:
        result = result_service.get_result_by_task_id(task_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Result not found")
        return {"task_id": result.task_id, "accuracy": result.accuracy}
    except Exception as e:
        logger.error(f"Error retrieving result: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving result")

@router.get("/task-status/{task_id}")
@inject
async def get_task_status(
    task_id: int,
    task_status_service: TaskStatusService = Depends(Provide[AppContainer.task_status_service])
):
    """
       Endpoint to get the current status of a task by task ID.

       Args:
           task_id (int): ID of the task.
           task_status_service (TaskStatusService): Service to fetch task status.

       Returns:
           dict: Task ID and status.
       """
    try:
        status = task_status_service.get_task_status(task_id)
        if status is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"task_id": task_id, "status": status}
    except Exception as e:
        logger.error(f"Error retrieving task status: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving task status")
