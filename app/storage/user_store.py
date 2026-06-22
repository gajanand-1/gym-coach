import bcrypt
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User


class UserStore:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------ #
    # Auth helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())

    # ------------------------------------------------------------------ #
    # CRUD
    # ------------------------------------------------------------------ #
    def create(self, username: str, email: str, password: str, name: str = "") -> User:
        user = User(
            username=username,
            email=email,
            hashed_password=self.hash_password(password),
            name=name,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self.get_by_username(username)
        if user and self.verify_password(password, user.hashed_password):
            return user
        return None

    def update_profile(self, user_id: int, **kwargs) -> Optional[User]:
        user = self.get_by_id(user_id)
        if not user:
            return None
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_macros(self, user_id: int, bmr: float, tdee: float,
                      target_calories: float, protein_target_g: float,
                      carbs_target_g: float, fat_target_g: float,
                      water_target_liters: float) -> Optional[User]:
        return self.update_profile(
            user_id,
            bmr=bmr,
            tdee=tdee,
            target_calories=target_calories,
            protein_target_g=protein_target_g,
            carbs_target_g=carbs_target_g,
            fat_target_g=fat_target_g,
            water_target_liters=water_target_liters,
        )

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
