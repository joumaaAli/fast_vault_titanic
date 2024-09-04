from fastapi import APIRouter
from app.api.v1.endpoints import auth, synthetic

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(synthetic.router, prefix="/synthetic", tags=["synthetic"])
