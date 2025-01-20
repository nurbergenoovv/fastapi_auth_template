from typing import Optional

from pydantic import BaseModel

class UserSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    password: Optional[str] = None
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    class Config:
        from_attributes = True

class ForgetPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    email: str