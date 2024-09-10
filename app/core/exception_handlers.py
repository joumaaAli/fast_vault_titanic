import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom HTTP exception handler for FastAPI to log and return structured responses.

    Args:
        request (Request): The request object.
        exc (HTTPException): The HTTPException raised.

    Returns:
        JSONResponse: JSON response with status code and error message.
    """

    logger.error(f"HTTPException occurred: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "error": "HTTPException"
        },
    )

async def validation_exception_handler(request: Request, exc):
    """
    Handles request validation errors and logs them.
    """
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "status_code": 422,
            "error": "ValidationError"
        },
    )

async def general_exception_handler(request: Request, exc: Exception):
    """
    Catches all unhandled exceptions and logs them.
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred.",
            "status_code": 500,
            "error": "InternalServerError"
        },
    )
