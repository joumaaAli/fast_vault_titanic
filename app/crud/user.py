from app.db.models.user import DBUser
from app.entities.user import User
from sqlalchemy.orm import Session

def get_user_by_username(db, username: str) -> User | None:
    db_user = db.query(DBUser).filter(DBUser.username == username).first()
    if db_user:
        return User.model_validate(db_user)
    return None


def create_user(db: Session, user_data: dict) -> User:
    db_user = DBUser(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=user_data["hashed_password"]
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return User.model_validate(db_user)

def get_user_by_id(db: Session, user_id: int):
    return db.query(DBUser).filter(DBUser.id == user_id).first()