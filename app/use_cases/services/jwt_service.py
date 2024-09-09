import jwt
from datetime import datetime, timedelta
from app.core.config import settings


class JWTService:

    def __init__(self, secret_key: str, algorithm: str):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
        """Create a JWT token with optional expiration."""
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta if expires_delta else datetime.utcnow() + timedelta(hours=1)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> dict | None:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
