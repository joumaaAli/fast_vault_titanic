from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(..., env='DATABASE_URL')  # Load from .env or environment variables
    secret_key: str = Field(..., env='SECRET_KEY')      # Load from .env or environment variables
    algorithm: str = Field(default="HS256")             # Default value if not set

    class Config:
        env_file = '../../.env'  # Path to your .env file

# Instantiate the settings object, which will load variables
settings = Settings()
