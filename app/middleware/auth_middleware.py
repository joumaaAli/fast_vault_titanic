import logging

from fastapi import HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.auth.utils import get_current_user


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Define paths that don't require authentication
        public_paths = ["/favicon.ico", "/docs", "/openapi.json", "/auth/token"]

        # Skip authentication for public paths
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)

        # Check for the Authorization header
        token = request.headers.get("Authorization")
        logging.info(f"Authorization header: {token}")

        if token is None or not token.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization token missing",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Remove "Bearer " prefix and validate the token
        token = token[len("Bearer "):]
        try:
            user = get_current_user(token)
            request.state.user = user  # Attach user to the request state
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        response = await call_next(request)
        return response
