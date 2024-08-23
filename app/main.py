from fastapi import FastAPI
from app.routers.auth import router as auth_router
from fastapi.security import OAuth2PasswordBearer
from app.routers.synthetic import router as synthetic_router
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(synthetic_router, prefix="/synthetic", tags=["synthetic"])

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI with SDV example"}
