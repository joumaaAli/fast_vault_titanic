from fastapi import FastAPI
from fastapi.openapi.models import OpenAPI
from fastapi.openapi.utils import get_openapi
from app.middleware.auth_middleware import AuthMiddleware
from app.routers import synthetic, auth

app = FastAPI()

app.add_middleware(AuthMiddleware)  # Add middleware before including routers

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

app.include_router(synthetic.router, prefix="/synthetic", tags=["synthetic"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
