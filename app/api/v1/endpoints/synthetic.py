import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.schema.synthetic import SyntheticDataResponse
from app.services.data_services import generate_synthetic_data, evaluate_synthetic_data, augment_and_train

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate/", response_model=SyntheticDataResponse)
async def generate_synthetic_data_endpoint(
    request: Request,
    synthesizer_type: str = "ctgan"
):
    user = getattr(request.state, 'user', None)
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    logger.info(f"Received request to generate synthetic data using {synthesizer_type} by user {user.username}")

    # Access the session from the request state
    db = request.state.db

    try:
        synthetic_data_id = generate_synthetic_data(db, synthesizer_type)
        logger.info(f"Synthetic data generation completed with ID: {synthetic_data_id}")
        return {"id": synthetic_data_id, "synthesizer_type": synthesizer_type}
    except Exception as e:
        logger.error(f"Error during synthetic data generation: {e}")
        raise HTTPException(status_code=500, detail="Error generating synthetic data")

@router.post("/augment-and-train/")
async def augment_and_train_endpoint(
    request: Request,
    synthesizer_type: str = "ctgan",
    augmentation_factor: int = 2
):
    user = getattr(request.state, 'user', None)
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    logger.info(f"Received request to augment and train model with synthesizer {synthesizer_type} by user {user.username}")

    # Access the session from the request state
    db = request.state.db

    try:
        accuracy = augment_and_train(db, synthesizer_type, augmentation_factor)
        logger.info(f"Model training completed with accuracy: {accuracy}")
        return {"status": "Model training initiated", "accuracy": accuracy}
    except Exception as e:
        logger.error(f"Error during data augmentation and training: {e}")
        raise HTTPException(status_code=500, detail="Error during data augmentation and training")

@router.post("/evaluate/")
async def evaluate_synthetic_data_endpoint(
    request: Request,
    synthetic_data_id: int
):
    user = getattr(request.state, 'user', None)
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    logger.info(f"Received request to evaluate synthetic data with ID: {synthetic_data_id} by user {user.username}")

    # Access the session from the request state
    db = request.state.db

    try:
        scores = evaluate_synthetic_data(db, synthetic_data_id)
        logger.info(f"Evaluation completed for synthetic data ID: {synthetic_data_id}")
        return JSONResponse(content=scores)
    except Exception as e:
        logger.error(f"Error during evaluation: {e}")
        raise HTTPException(status_code=500, detail="Error during evaluation of synthetic data")
