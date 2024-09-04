# app/main.py
import os

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.db_middleware import DBSessionMiddleware
from app.api.v1.router import router as api_router
from app.core.logger import configure_logging
from alembic.config import Config
from alembic import command
import logging
from app.core.config import settings

configure_logging()

logger = logging.getLogger(__name__)
app = FastAPI()

# Add AuthMiddleware after DBSessionMiddleware
app.add_middleware(AuthMiddleware)

# Add DBSessionMiddleware first
app.add_middleware(DBSessionMiddleware)


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

app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def run_migrations():
    """
    Runs Alembic migrations when the application starts.
    """
    try:
        logger.info("Running migrations...")

        # Create an Alembic Config object and specify the ini file path
        alembic_cfg = Config(os.path.join(os.path.dirname(__file__), '../alembic.ini'))

        # Update the sqlalchemy.url dynamically
        alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)

        # Ensure Alembic knows where the migration scripts are
        alembic_cfg.set_main_option("script_location", os.path.join(os.path.dirname(__file__), "alembic"))

        # Run migrations
        command.upgrade(alembic_cfg, "head")

        logger.info("Migrations complete.")
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        raise e