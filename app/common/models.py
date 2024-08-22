from pydantic import BaseModel, EmailStr

class User(BaseModel):
    username: str
    email: EmailStr  # Adding email for registration
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

