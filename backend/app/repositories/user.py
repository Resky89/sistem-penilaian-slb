from sqlalchemy.orm import Session
from app.models.db_models import User
from app.schemas.auth import UserCreate

class UserRepository:
    @staticmethod
    def get_by_username(db: Session, username: str) -> User:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create(db: Session, user: UserCreate, hashed_password: str) -> User:
        db_user = User(
            full_name=user.full_name,
            username=user.username,
            password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
