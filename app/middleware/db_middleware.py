# app/middleware/db_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.db.session import get_db
import logging

logger = logging.getLogger(__name__)

class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            # Attach the database session to the request state
            request.state.db = next(get_db())
            response = await call_next(request)
            return response
        except Exception as e:
            # Log and handle any errors
            logger.error(f"Error in DBSessionMiddleware: {e}")
            raise
