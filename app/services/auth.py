import random
import string

from fastapi import HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import UserCreate, UserLogin, UserSchema, ForgetPasswordRequest, ResetPasswordRequest, UserUpdate
from app.services.mail import send_new_pass
from app.utils.config import JWT_SECRET_KEY
from app.utils.repository import AbstractRepository
from authx import AuthX, AuthXConfig, RequestToken


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

    async def get_users(self):
        users = await self.users_repo.find_all()
        return users

    async def add_user(self, crds: UserCreate, response: Response):
        user_dict = crds.model_dump()
        user_dict["password"] = get_password_hash(user_dict["password"])
        user = await self.users_repo.find_one(email=user_dict['email'])
        if user:
            raise HTTPException(status_code=400, detail="User already exists")

        user_id = await self.users_repo.add_one(user_dict)
        if user_id:
            access_token = auth.create_access_token(uid=str(user_id), data={"role": "user", **user_dict},csrf=False)
            response.set_cookie(auth.config.JWT_ACCESS_COOKIE_NAME, access_token, max_age=10800)
        return user_id

    async def user_login(self, crds: UserLogin, response: Response):
        user_dict = crds.model_dump()
        user: UserSchema = await self.users_repo.find_one(email=user_dict["email"])
        if user:
            if verify_password(user_dict["password"], user.password):
                access_token = auth.create_access_token(uid=str(user.id), data={"role": "user", "email": user.email,
                                                                                "first_name": user.first_name,
                                                                                "last_name": user.last_name}, csrf=False)
                response.set_cookie(auth.config.JWT_ACCESS_COOKIE_NAME, access_token, max_age=10800)
                return user.id
            else:
                raise HTTPException(status_code=401, detail="Incorrect password")
        raise HTTPException(status_code=401, detail="Incorrect email")

    async def logout(self, response: Response):
        response.delete_cookie(auth.config.JWT_ACCESS_COOKIE_NAME)
        return {"message": "Logged out successfully"}

    async def get_current_user(self, request: Request):
        token = await auth.get_access_token_from_request(request=request, locations=["cookies"]) or None

        if not token:
            raise HTTPException(status_code=401, detail="No token provided")

        payload = auth.verify_token(token=token, verify_csrf=False)
        payload = payload.model_dump()


        return {
            "id":payload['sub'],
            "role": payload['role'],
            "email": payload['email'],
            "first_name": payload['first_name'],
            "last_name": payload['last_name'],
        }

    async def forgot_pass(self, crds: ForgetPasswordRequest):
        email = crds.email
        user: UserSchema = await self.users_repo.find_one(email=email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        token = create_token()
        stmt = await self.users_repo.update_one(obj_id=user.id, data={"reset_token": token})
        mail = await send_new_pass(email=user.email, token=token)
        if not stmt or not mail:
            return {"message": "Internal server error"}
        return {"message": "Token created and message sended to email"}

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
        user = await self.users_repo.update_one(obj_id=user_id, data=user_dict)
        if not user:
            return {"message": "Internal server error"}
        response.delete_cookie(auth.config.JWT_ACCESS_COOKIE_NAME)

        access_token = auth.create_access_token(uid=str(user.id), data={"role": "user", "email": user.email,
                                                                        "first_name": user.first_name,
                                                                        "last_name": user.last_name}, csrf=False)

        response.set_cookie(auth.config.JWT_ACCESS_COOKIE_NAME, access_token, max_age=10800)

        return {"message": "User updated successfully", "data": user}
