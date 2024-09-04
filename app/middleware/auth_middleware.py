# app/middleware/auth_middleware.py
import logging
from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.utils.jwt import verify_token
from app.crud.user import get_user_by_username, get_user_by_id  # Import your function to get user details

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Define paths that don't require authentication
        public_paths = ["/favicon.ico", "/docs", "/openapi.json", "/auth/token"]
        # Skip authentication for public paths
        if any(request.url.path.startswith(path) for path in public_paths):
            response = await call_next(request)
            return response

        # Check for the Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                token_type, token = auth_header.split(" ")
                if token_type.lower() != "bearer":
                    raise HTTPException(status_code=401, detail="Invalid token type")

                payload = verify_token(token)
                if payload is None:
                    raise HTTPException(status_code=401, detail="Invalid or expired token")

                user_id = payload.get("sub")
                if user_id:
                    db = getattr(request.state, 'db', None)
                    if db is None:
                        raise HTTPException(status_code=500, detail="Database session not available")

                    user = get_user_by_id(db, user_id)  # Ensure this function exists and works
                    if user:
                        request.state.user = user
                    else:
                        raise HTTPException(status_code=401, detail="User not found")
                else:
                    raise HTTPException(status_code=401, detail="User ID missing in token payload")

            except ValueError:
                raise HTTPException(status_code=401, detail="Invalid token")
        else:
            request.state.user = None

        response = await call_next(request)
        return response
