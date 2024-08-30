from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from app.routers.auth import router as auth_router
from app.routers.synthetic import router as synthetic_router
from app.routers.health import router as health_router
from app.routers.model import router as models_router
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(synthetic_router, prefix="/synthetic", tags=["synthetic"])

app.include_router(models_router, prefix="/models", tags=["models"])

app.include_router(health_router, prefix="/health", tags=["health"])
@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI with SDV example"}
