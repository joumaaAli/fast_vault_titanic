from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from app.entities.user import LoginRequest, RegisterRequest
from app.persistence.repositories.user_repository import UserRepository
from app.utils.password_hasher import PasswordHasher
from app.use_cases.services.jwt_service import JWTService
from app.container import AppContainer

router = APIRouter()

@router.post("/login")
@inject
def login(
    request: LoginRequest,
    user_repo: UserRepository = Depends(Provide[AppContainer.user_repository]),
    password_hasher: PasswordHasher = Depends(Provide[AppContainer.password_hasher]),
    jwt_service: JWTService = Depends(Provide[AppContainer.jwt_service])
):
    user = user_repo.get_user_by_username(request.username)
    user_repo.close()

    if user and password_hasher.verify_password(request.password, user.hashed_password):
        access_token = jwt_service.create_access_token(data={"sub": user.id, "username": user.username})
        return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/register")
@inject
def register(
    request: RegisterRequest,
    user_repo: UserRepository = Depends(Provide[AppContainer.user_repository]),
    password_hasher: PasswordHasher = Depends(Provide[AppContainer.password_hasher])
):
    if user_repo.get_user_by_username(request.username):
        user_repo.close()
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = password_hasher.hash_password(request.password)

    user = user_repo.create_user({
        "username": request.username,
        "email": request.email,
        "hashed_password": hashed_password
    })
    user_repo.close()

    return {"message": "User registered successfully"}
