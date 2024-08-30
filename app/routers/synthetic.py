# app/routers/synthetic.py

from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Depends
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import asyncio

from app.auth.utils import get_current_user
from app.common.models import User
from app.common.tasks import augment_and_train_task, evaluate_synthetic_data_task, generate_synthetic_data_task
from app.database import get_db

router = APIRouter()


# Initialize a ThreadPoolExecutor with a limited number of threads
executor = ThreadPoolExecutor(max_workers=4)


@router.post("/generate_synthetic_data/")
async def generate_synthetic_data(background_tasks: BackgroundTasks,
                                  db: Session = Depends(get_db),
                                  current_user: User = Depends(get_current_user),
                                  synthesizer_type: str = "ctgan"):  # Default parameter at the end
    # Function body remains the same
    loop = asyncio.get_running_loop()
    synthetic_data_id = await loop.run_in_executor(
        executor, generate_synthetic_data_task, synthesizer_type, db, current_user
    )

    return {"status": "Synthetic data generation initiated", "synthetic_data_id": synthetic_data_id}


@router.post("/augment_and_train/")
async def augment_and_train(background_tasks: BackgroundTasks,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user),
                            synthesizer_type: str = "ctgan",
                            augmentation_factor: int = 2):
    loop = asyncio.get_running_loop()
    accuracy = await loop.run_in_executor(
        executor, augment_and_train_task, synthesizer_type, augmentation_factor, db, current_user
    )
    return {"status": "Model training initiated", "accuracy": accuracy}


@router.post("/evaluate_synthetic_data/")
async def evaluate_synthetic_data(synthetic_data_id: int,
                                  background_tasks: BackgroundTasks,
                                  db: Session = Depends(get_db),
                                  current_user: User = Depends(get_current_user)):
    loop = asyncio.get_running_loop()
    scores = await loop.run_in_executor(
        executor, evaluate_synthetic_data_task, synthetic_data_id, db
    )

    return JSONResponse(content=scores)