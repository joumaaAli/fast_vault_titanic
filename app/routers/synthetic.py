# app/routers/synthetic.py

import asyncio
import logging
from concurrent.futures import ProcessPoolExecutor

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth.utils import get_current_user
from app.common.models import User
from app.common.tasks import augment_and_train_task, evaluate_synthetic_data_task, generate_synthetic_data_task
from app.database import get_db

# Configure logging
logger = logging.getLogger(__name__)

# Initialize a ProcessPoolExecutor with a limited number of processes
executor = ProcessPoolExecutor(max_workers=4)

router = APIRouter()


@router.post("/generate_synthetic_data/")
async def generate_synthetic_data(background_tasks: BackgroundTasks,
                                  db: Session = Depends(get_db),
                                  current_user: User = Depends(get_current_user),
                                  synthesizer_type: str = "ctgan"):
    logger.info(f"Received request to generate synthetic data using {synthesizer_type}")
    loop = asyncio.get_running_loop()

    # Extract necessary information from db and user before sending to the executor
    current_user_id = current_user.id

    # Run the task in the background
    synthetic_data_id = await loop.run_in_executor(
        executor, generate_synthetic_data_task, synthesizer_type, current_user_id
    )
    logger.info(f"Synthetic data generation completed with ID: {synthetic_data_id}")

    return {"status": "Synthetic data generation initiated", "synthetic_data_id": synthetic_data_id}


@router.post("/augment_and_train/")
async def augment_and_train(background_tasks: BackgroundTasks,
                            current_user: User = Depends(get_current_user),
                            synthesizer_type: str = "ctgan",
                            augmentation_factor: int = 2):
    logger.info(f"Received request to augment and train model with synthesizer {synthesizer_type}")
    loop = asyncio.get_running_loop()
    accuracy = await loop.run_in_executor(
        executor, augment_and_train_task, synthesizer_type, augmentation_factor, current_user
    )
    logger.info(f"Model training completed with accuracy: {accuracy}")

    return {"status": "Model training initiated", "accuracy": accuracy}


@router.post("/evaluate_synthetic_data/")
async def evaluate_synthetic_data(synthetic_data_id: int,
                                  background_tasks: BackgroundTasks,
                                  current_user: User = Depends(get_current_user)):
    logger.info(f"Received request to evaluate synthetic data with ID: {synthetic_data_id}")
    loop = asyncio.get_running_loop()
    scores = await loop.run_in_executor(
        executor, evaluate_synthetic_data_task, synthetic_data_id
    )
    logger.info(f"Evaluation completed for synthetic data ID: {synthetic_data_id}")

    return JSONResponse(content=scores)

