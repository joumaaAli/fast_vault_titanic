from sqlalchemy.orm import Session
from app.db.models.user import DBUser
from app.entities.user import User
from app.db.session import get_db

class UserRepository:
    class UserRepository:
     """
    Repository class for handling operations related to users.

    Methods:
        get_user_by_username(username): Fetches a user by their username.
        create_user(user_data): Creates a new user in the database.
        get_user_by_id(user_id): Fetches a user by their ID.
    """
    def __init__(self):
        self.db = next(get_db())

    def get_user_by_username(self, username: str) -> User | None:
        """Fetch user by username."""
        db_user = self.db.query(DBUser).filter(DBUser.username == username).first()
        if db_user:
            return User.model_validate(db_user)
        return None

    def create_user(self, user_data: dict) -> User:
        """Create a new user."""
        db_user = DBUser(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=user_data["hashed_password"]
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return User.model_validate(db_user)

    def get_user_by_id(self, user_id: int) -> DBUser | None:
        """Fetch user by user ID."""
        return self.db.query(DBUser).filter(DBUser.id == user_id).first()

    def close(self):
        """Close the database session."""
        self.db.close()

