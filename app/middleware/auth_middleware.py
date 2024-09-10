# app/middleware/auth_middleware.py
import logging

from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import settings
from app.use_cases.services.jwt_service import JWTService

algorithm = settings.algorithm
secret_key = settings.secret_key

jwt_service = JWTService(secret_key, algorithm)

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Define paths that don't require authentication
        public_paths = ["/favicon.ico", "/docs", "/openapi.json", "/auth/token", "/auth/login", "/auth/register"]
        # Skip authentication for public paths
        if any(request.url.path.startswith(path) for path in public_paths):
            response = await call_next(request)
            return response

        # Check for the Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                token_type, token = auth_header.split(" ")
                print(token_type)
                print(token)
                if token_type.lower() != "bearer":
                    raise HTTPException(status_code=401, detail="Invalid token type")
                payload = jwt_service.verify_token(token)
                if payload is None:
                    raise HTTPException(status_code=401, detail="Invalid or expired token")
                request.state.user = payload
            except ValueError:
                raise HTTPException(status_code=401, detail="Invalid token")
        else:
            request.state.user = None

        response = await call_next(request)
        return response
