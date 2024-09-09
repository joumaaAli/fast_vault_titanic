from passlib.context import CryptContext


class PasswordHasher:
    def __init__(self, schemes: list[str] = ["bcrypt"], deprecated: str = "auto"):
        self.pwd_context = CryptContext(schemes=schemes, deprecated=deprecated)

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
