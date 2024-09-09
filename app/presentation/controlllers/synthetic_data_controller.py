import logging

from fastapi import APIRouter, HTTPException, Request

from app.core.config import settings
from app.entities.synthetic_data import SynthesizerType
from app.use_cases.services.data_services import DataService
from app.use_cases.evaluators.evaluators import Evaluator
from app.use_cases.factories.factories import SynthesizerFactory

router = APIRouter()
logger = logging.getLogger(__name__)

# Dependency Injection for the DataService
factory = SynthesizerFactory()
evaluator = Evaluator()
csv_path = settings.csv
data_service = DataService(factory, evaluator, csv_path)

@router.post("/generate/")
async def generate_synthetic_data_endpoint(
    request: Request,
    synthesizer_type: SynthesizerType
):
    user = getattr(request.state, 'user', None)
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    try:
        synthetic_data_id = data_service.generate_synthetic_data(synthesizer_type)
        return {"id": synthetic_data_id, "synthesizer_type": synthesizer_type.value}
    except Exception as e:
        logger.error(f"Error during synthetic data generation: {e}")
        raise HTTPException(status_code=500, detail="Error generating synthetic data")

@router.post("/augment-and-train/")
async def augment_and_train_endpoint(
    request: Request,
    synthesizer_type: SynthesizerType,
    augmentation_factor: int = 2
):
    user = getattr(request.state, 'user', None)
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    try:
        accuracy = data_service.augment_and_train(synthesizer_type, augmentation_factor)
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

    try:
        scores = data_service.evaluate_synthetic_data(synthetic_data_id)
        return scores
    except Exception as e:
        logger.error(f"Error during evaluation: {e}")
        raise HTTPException(status_code=500, detail="Error during evaluation of synthetic data")
