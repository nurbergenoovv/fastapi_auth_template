
import random
import string

from fastapi import HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from authx.schema import RequestToken
from app.schemas.auth import UserCreate, UserLogin, UserSchema, ForgetPasswordRequest, ResetPasswordRequest, UserUpdate
from app.services.mail import send_new_pass, activate_account
from app.utils.config import JWT_SECRET_KEY
from app.utils.repository import AbstractRepository
from authx import AuthX, AuthXConfig
import asyncio

def verify_password(plain_password, hashed_password):
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def create_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))


config = AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY=JWT_SECRET_KEY,
    JWT_TOKEN_LOCATION=["cookies"],
    JWT_ACCESS_COOKIE_NAME="access_token",
    JWT_COOKIE_CSRF_PROTECT=False,
    JWT_CSRF_IN_COOKIES=False
)

auth = AuthX(config=config)


class AuthService:
    def __init__(self, users_repo: AbstractRepository, session: AsyncSession):
        self.users_repo: AbstractRepository = users_repo(session)

    async def get_users(self, token:str):
        if not token:
            raise HTTPException(
                status_code=401,
                detail="Unauthorized",
            )
        tok = RequestToken(
            token=token,
            location="headers",
            type="access"
        )
        payload = auth.verify_token(token=tok, verify_csrf=False)
        user = payload.model_dump()

        if user['role'] != "admin":
            raise HTTPException(
                status_code=403,
                detail="Forbidden",
            )

        users = await self.users_repo.find_all()
        return users

    async def add_user(self, crds: UserCreate, response: Response):
        user_dict = crds.model_dump()
        user_dict["password"] = get_password_hash(user_dict["password"])
        user = await self.users_repo.find_one(username=crds.username, email=crds.email)
        if user:
            raise HTTPException(status_code=400, detail="User already exists")

        user_id = await self.users_repo.add_one(user_dict)
        if user_id:
            access_token = auth.create_access_token(uid=str(user_id), data={**user_dict}, csrf=False)
        asyncio.create_task(activate_account(crds, user_id))

        return access_token

    async def user_login(self, crds: UserLogin, response: Response):
        user_dict = crds.model_dump()
        user: UserSchema = await self.users_repo.find_one(username=crds.username)
        if user:
            if verify_password(user_dict["password"], user.password):
                access_token = auth.create_access_token(uid=str(user.id), data={"role": user.role, "email": user.email,
                                                                                "username": user.username},
                                                        csrf=False)
                return access_token
            else:
                raise HTTPException(status_code=401, detail="Incorrect password")
        raise HTTPException(status_code=401, detail="Incorrect username")

    async def get_current_user(self, token: str):
        if not token:
            raise HTTPException(status_code=401, detail="Unauthorized")
        tok = RequestToken(
            token=token,
            location="headers",
            type="access"
        )
        payload = auth.verify_token(token=tok, verify_csrf=False)
        payload = payload.model_dump()

        return {
            "id": payload['sub'],
            "role": payload['role'],
            "email": payload['email'],
            "username": payload['username'],
        }

    async def forgot_pass(self, crds: ForgetPasswordRequest):
        email = crds.email
        user = await self.users_repo.find_one(email=email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        token = create_token()
        stmt = await self.users_repo.update_one(obj_id=user.id, data={"reset_token": token})

        if not stmt:
            return {"message": "Internal server error"}

        asyncio.create_task(send_new_pass(email, token))

        return {"message": "Token created and message sent to email"}

    async def reset_password(self, crds: ResetPasswordRequest):
        token = crds.token
        new_password = crds.new_password
        user: UserSchema = await self.users_repo.find_one(reset_token=token)
        if not user:
            raise HTTPException(status_code=404, detail="Token not found")

        user_dict = user.model_dump()
        user_dict["password"] = get_password_hash(new_password)
        user_dict["reset_token"] = None
        stmt = await self.users_repo.update_one(obj_id=user.id, data=user_dict)
        if not stmt:
            return {"message": "Internal server error"}
        return {"message": "Password changed successfully"}

    async def update_user(self, user_id: int, crds: UserUpdate, response: Response):
        cuser = await self.users_repo.find_one(id=user_id)
        user_dict = crds.model_dump()
        if not cuser:
            raise HTTPException(status_code=404, detail="User not found")
        user_dict["password"] = get_password_hash(UserUpdate.password)
        user = await self.users_repo.update_one(obj_id=user_id, data=user_dict)
        if not user:
            return {"message": "Internal server error"}
        access_token = auth.create_access_token(uid=str(user.id), data={"role": user.role, "email": user.email,
                                                                        "username": user.username}, csrf=False)
        return {"message": "User updated successfully", "data": user, "access_token": access_token}

    async def delete_user(self, user_id: int):
        user = await self.users_repo.find_one(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        stmt = await self.users_repo.remove_one(obj_id=user_id)
        if not stmt:
            return {"message": "Internal server error"}

        return {"message": "User deleted successfully"}

    async def send_forgot_to_email_async(self, email: str, token: str):
        try:
            await send_new_pass(email, token)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    async def find_by_id(self, id: int):
        user = await self.users_repo.find_one(id=id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def activate_user(self, id: int):
        user = await self.users_repo.find_one(id=id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        stmt = await self.users_repo.update_one(obj_id=id, data={"is_activated": True})
        if not stmt:
            return {"message": "Internal server error"}
        return {"message": "User activated successfully"}
