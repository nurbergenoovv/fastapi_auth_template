from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.schemas.auth import UserSchema


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    reset_token = Column(String, unique=True, index=True, nullable=True)

    created_tasks = relationship(
        "Task",
        back_populates="creator",
        foreign_keys="[Task.created_by]",
        cascade="all, delete"
    )
    assigned_tasks = relationship(
        "Task",
        back_populates="assignee",
        foreign_keys="[Task.assigned_to]",
        cascade="all, delete"
    )
    updated_tasks = relationship(
        "Task",
        back_populates="updater",
        foreign_keys="[Task.update_by]",
        cascade="all, delete"
    )

    def to_read_model(self) -> UserSchema:
        return UserSchema(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            password=self.password
        )