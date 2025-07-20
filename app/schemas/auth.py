from typing import Optional

from pydantic import BaseModel

class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    password: Optional[str] = None
    is_activated: Optional[bool] = False
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = "user"

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    is_activated: bool
    email: str
    class Config:
        from_attributes = True

class ForgetPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class UserUpdate(BaseModel):
    username: str
    password: str
    email: str
    role: Optional[str] = "user"

class Activation(BaseModel):
    token: str