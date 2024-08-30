import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db, User as DBUser
from app.auth.utils import verify_password, create_access_token, get_current_user
from app.common.models import User, Token

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login attempt for user: {form_data.username}")
    user = db.query(DBUser).filter(DBUser.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    logger.info(f"Login successful for user: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    logger.info(f"Retrieved information for current user: {current_user.username}")
    return current_user

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: User, db: Session = Depends(get_db)):
    logger.info(f"Signup attempt for username: {user.username}")
    new_user = DBUser(username=user.username, email=user.email)
    new_user.set_password(user.password)
    db.add(new_user)
    try:
        db.commit()
        logger.info(f"User created successfully: {user.username}")
    except IntegrityError:
        db.rollback()
        logger.warning(f"Signup failed: Username or email already registered for username: {user.username}")
        raise HTTPException(status_code=400, detail="Username or email already registered")
    db.refresh(new_user)
    return {"message": "User created successfully."}
