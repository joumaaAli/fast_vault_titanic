from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from app.routers.auth import router as auth_router
from app.routers.synthetic import router as synthetic_router
from app.routers.health import router as health_router
from app.routers.model import router as models_router
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(synthetic_router, prefix="/synthetic", tags=["synthetic"])

app.include_router(models_router, prefix="/models", tags=["models"])

app.include_router(health_router, prefix="/health", tags=["health"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the FastAPI application...")
    yield
    logger.info("Shutting down the FastAPI application...")

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI with SDV example"}
