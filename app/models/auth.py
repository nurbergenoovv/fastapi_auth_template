from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.schemas.auth import UserSchema


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, unique=True, index=True)
    role = Column(String, default="user")
    password = Column(String)
    reset_token = Column(String, unique=True, index=True, nullable=True)
    is_activated = Column(Boolean, default=False)