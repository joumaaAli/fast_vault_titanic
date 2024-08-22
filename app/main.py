from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.sdv.routes import router as sdv_router
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(sdv_router, prefix="/sdv", tags=["sdv"])

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI with SDV example"}
