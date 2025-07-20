from typing import Annotated

from fastapi import APIRouter, Response, Request
from fastapi.params import Depends

from app.api.dependencies import auth_service
from app.schemas.auth import (
    UserCreate,
    UserLogin,
    ForgetPasswordRequest,
    ResetPasswordRequest,
    UserUpdate
)
from app.services.auth import AuthService
from fastapi.security import OAuth2PasswordBearer
from app.extensions.rate_limiter import limiter


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/")
async def get_all(
        users_service: Annotated[AuthService, Depends(auth_service)],
        token: Annotated[str, Depends(oauth2_scheme)]
):
    users = await users_service.get_users(token)
    return users

@router.post("/")
async def create_user(
        crds: UserCreate,
        users_service: Annotated[AuthService, Depends(auth_service)],
        response: Response
):
    access_token = await users_service.add_user(crds, response)
    return {"access_token": access_token}

@router.post("/login")
@limiter.limit("1/2 second")
async def login(
        crds: UserLogin,
        users_service: Annotated[AuthService, Depends(auth_service)],
        response: Response,
        request: Request
):
    try:
        token = await users_service.user_login(crds, response)
        return {"access_token": token}
    except Exception as e:
        raise e

@router.post("/me")
async def me(
        users_service: Annotated[AuthService, Depends(auth_service)],
        token: Annotated[str, Depends(oauth2_scheme)]
):
    user = await users_service.get_current_user(token)
    return user

@router.get("/activate/{user_id}")
async def activate_user(
        users_service: Annotated[AuthService, Depends(auth_service)],
        user_id: int
):
    return await users_service.activate_user(user_id)

@router.put('/{user_id}')
async def update_user(
        users_service: Annotated[AuthService, Depends(auth_service)],
        user_id: int,
        crds: UserUpdate,
        response: Response,
):
    result = await users_service.update_user(user_id, crds, response)
    return result

@router.post("/forgot_password")
async def forget_password(
        users_service: Annotated[AuthService, Depends(auth_service)],
        crds: ForgetPasswordRequest,
):
    result = await users_service.forgot_pass(crds)
    return result

@router.post("/reset_password")
async def reset_password(
        users_service: Annotated[AuthService, Depends(auth_service)],
        crds: ResetPasswordRequest,
):
    result = await users_service.reset_password(crds)
    return result

@router.delete("/{user_id}")
async def delete_user(
        users_service: Annotated[AuthService, Depends(auth_service)],
        user_id: int,
):
    result = await users_service.delete_user(user_id)
    return result

