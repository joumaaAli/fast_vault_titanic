import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./test.db')
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"