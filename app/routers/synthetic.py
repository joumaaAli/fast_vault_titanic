# app/routers/synthetic.py

import asyncio
import logging

import joblib  # To load the model
import pandas as pd
from fastapi import APIRouter, Request, HTTPException
from fastapi import Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth.utils import get_current_user
from app.common.models import User, PredictionInput
from app.common.tasks import augment_and_train_task, evaluate_synthetic_data_task, generate_synthetic_data_task
from app.database import get_db

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/generate_synthetic_data/")
async def generate_synthetic_data(
    request: Request,
    synthesizer_type: str = "ctgan"
):
    user = getattr(request.state, 'user', None)
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    logger.info(f"Received request to generate synthetic data using {synthesizer_type} by user {user.username}")
    loop = asyncio.get_running_loop()

    # Extract necessary information from user before sending to the executor
    current_user_id = user.id

    # Run the task in the background
    synthetic_data_id = await loop.run_in_executor(
        None,  # Use the default executor
        generate_synthetic_data_task,
        synthesizer_type,
        current_user_id
    )
    logger.info(f"Synthetic data generation completed with ID: {synthetic_data_id}")

    return {"status": "Synthetic data generation initiated", "synthetic_data_id": synthetic_data_id}


@router.post("/augment_and_train/")
async def augment_and_train(
    request: Request,
    synthesizer_type: str = "ctgan",
    augmentation_factor: int = 2
):
    user = getattr(request.state, 'user', None)
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    logger.info(f"Received request to augment and train model with synthesizer {synthesizer_type} by user {user.username}")
    loop = asyncio.get_running_loop()

    accuracy = await loop.run_in_executor(
        None,  # Use the default executor
        augment_and_train_task,
        synthesizer_type,
        augmentation_factor,
        user
    )
    logger.info(f"Model training completed with accuracy: {accuracy}")

    return {"status": "Model training initiated", "accuracy": accuracy}


@router.post("/evaluate_synthetic_data/")
async def evaluate_synthetic_data(
    request: Request,
    synthetic_data_id: int
):
    user = getattr(request.state, 'user', None)
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    logger.info(f"Received request to evaluate synthetic data with ID: {synthetic_data_id} by user {user.username}")
    loop = asyncio.get_running_loop()

    scores = await loop.run_in_executor(
        None,  # Use the default executor
        evaluate_synthetic_data_task,
        synthetic_data_id
    )
    logger.info(f"Evaluation completed for synthetic data ID: {synthetic_data_id}")

    return JSONResponse(content=scores)


# Load the trained model at the start
model = joblib.load("model.joblib")

@router.post("/predict/")
async def predict(input_data: PredictionInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Convert the input data to a DataFrame
    input_df = pd.DataFrame([input_data.model_dump()])

    # Use the loaded model to make predictions
    prediction = model.predict(input_df)

    # Assuming binary classification, return a meaningful label
    prediction_label = "Survived" if prediction[0] == 1 else "Did not survive"

    return {"prediction": prediction_label}
