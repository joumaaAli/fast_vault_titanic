import logging
from fastapi import APIRouter, HTTPException, Request, Depends
from dependency_injector.wiring import inject, Provide
from app.entities.synthetic_data import SynthesizerType
from app.use_cases.services.data_services import DataService
from app.container import AppContainer

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate/")
@inject
async def generate_synthetic_data_endpoint(
    request: Request,
    synthesizer_type: SynthesizerType,
    data_service: DataService = Depends(Provide[AppContainer.data_service])
):
    try:
        synthetic_data_id = data_service.generate_synthetic_data(synthesizer_type)
        return {"id": synthetic_data_id, "synthesizer_type": synthesizer_type.value}
    except Exception as e:
        logger.error(f"Error during synthetic data generation: {e}")
        raise HTTPException(status_code=500, detail="Error generating synthetic data")


@router.post("/augment-and-train/")
@inject
async def augment_and_train_endpoint(
    request: Request,
    synthesizer_type: SynthesizerType,
    augmentation_factor: int = 2,
    data_service: DataService = Depends(Provide[AppContainer.data_service])
):
    try:
        accuracy = data_service.augment_and_train(synthesizer_type, augmentation_factor)
        return {"status": "Model training initiated", "accuracy": accuracy}
    except Exception as e:
        logger.error(f"Error during data augmentation and training: {e}")
        raise HTTPException(status_code=500, detail="Error during data augmentation and training")


@router.post("/evaluate/")
@inject
async def evaluate_synthetic_data_endpoint(
    request: Request,
    synthetic_data_id: int,
    data_service: DataService = Depends(Provide[AppContainer.data_service])
):
    try:
        scores = data_service.evaluate_synthetic_data(synthetic_data_id)
        return scores
    except Exception as e:
        logger.error(f"Error during evaluation: {e}")
        raise HTTPException(status_code=500, detail="Error during evaluation of synthetic data")
