# app/main.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.db_middleware import DBSessionMiddleware
from app.api.v1.router import router as api_router
from app.core.logger import configure_logging

configure_logging()
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
