# app/main.py

import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.container import AppContainer

from app.core.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.core.logger import configure_logging
from app.middleware.auth_middleware import AuthMiddleware
from app.presentation.controllers.auth_controller import router as auth_controller
from app.presentation.controllers.synthetic_data_controller import router as synthetic_data_controller

configure_logging()

logger = logging.getLogger(__name__)
app = FastAPI()

# Add AuthMiddleware after DBSessionMiddleware

app.include_router(auth_controller, prefix="/auth", tags=["auth"])
app.include_router(synthetic_data_controller, prefix="/synthetic", tags=["synthetic"])

container = AppContainer()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Your API Title",
        version="1.0.0",
        description="Your API description",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Add Exception Handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# @app.on_event("startup")
# async def run_migrations():
#     """
#     Runs Alembic migrations when the application starts.
#     """
#     try:
#         logger.info("Running migrations...")
#
#         # Create an Alembic Config object and specify the ini file path
#         alembic_cfg = Config(os.path.join(os.path.dirname(__file__), '../alembic.ini'))
#
#         # Update the sqlalchemy.url dynamically
#         alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
#
#         # Ensure Alembic knows where the migration scripts are
#         logger.info("Setting script location for Alembic migrations.")
#         alembic_cfg.set_main_option("script_location", os.path.join(os.path.dirname(__file__), "alembic"))
#
#         # Run migrations
#         logger.info("Executing Alembic upgrade command...")
#         command.upgrade(alembic_cfg, "head")
#
#         logger.info("Migrations complete.")
#     except Exception as e:
#         logger.error(f"Error running migrations: {e}")
#         raise e
