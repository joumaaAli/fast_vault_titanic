from pydantic import BaseModel

class User(BaseModel):
    id: int
    username: str
    email: str
    hashed_password: str
    model_config = {
        'from_attributes': True  # Enables validation from ORM attributes
    }
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
