from fastapi import APIRouter, HTTPException, Depends
from app.schema.auth import LoginRequest, RegisterRequest
from app.crud.user import get_user_by_username, create_user
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.utils.jwt import create_access_token
import logging

from app.utils.password import hash_password, verify_password

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_username(db, request.username)
    if user and verify_password(request.password, user.hashed_password):
        access_token = create_access_token(data={"sub": user.id, "username": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # Check if the user already exists
    if get_user_by_username(db, request.username):
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hash the password
    hashed_password = hash_password(request.password)

    # Create the user
    user = create_user(db, {
        "username": request.username,
        "email": request.email,
        "hashed_password": hashed_password
    })

    return {"message": "User registered successfully"}