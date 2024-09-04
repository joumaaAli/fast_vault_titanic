from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    database_url: str = Field(..., env='DATABASE_URL')
    secret_key: str = Field(..., env='SECRET_KEY')
    algorithm: str = Field(default="HS256")
    csv: str = Field(default=os.path.join(os.path.dirname(__file__), "../../tested.csv"))
    class Config:
        # Specify the path to the .env file
        env_file = os.path.join(os.path.dirname(__file__), '../../.env')
        env_file_encoding = 'utf-8'

# Instantiate the settings object
settings = Settings()
