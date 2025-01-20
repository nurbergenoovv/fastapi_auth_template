from typing import Annotated

from fastapi import APIRouter, Response, Request
from fastapi.params import Depends

from app.api.dependencies import auth_service
from app.schemas.auth import UserCreate, UserLogin, ForgetPasswordRequest, ResetPasswordRequest, UserUpdate
from app.services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_all(
    users_service: Annotated[AuthService, Depends(auth_service)],
):
    users = await users_service.get_users()
    return users

@router.post("/")
async def create_user(
    crds: UserCreate,
    users_service: Annotated[AuthService, Depends(auth_service)],
    response: Response
):
    user_id = await users_service.add_user(crds, response)
    return {"user_id": user_id}

@router.post("/login")
async def login(
    crds: UserLogin,
    users_service: Annotated[AuthService, Depends(auth_service)],
    response: Response
):
    user_id = await users_service.user_login(crds, response)
    return {"user_id": user_id}

@router.get("/logout")
async def logout(
    users_service: Annotated[AuthService, Depends(auth_service)],
    response: Response
):
    return await users_service.logout(response)

@router.post("/current_user")
async def me(
    users_service: Annotated[AuthService, Depends(auth_service)],
    request: Request,
):
    user = await users_service.get_current_user(request)
    return user

@router.put('/{user_id}')
async def update_user(
        users_service: Annotated[AuthService, Depends(auth_service)],
        user_id: int,
        crds: UserUpdate,
        response: Response
):
    result = await users_service.update_user(user_id, crds, response)
    return result

@router.post("/forgot_password")
async def forget_password(
        users_service: Annotated[AuthService, Depends(auth_service)],
        crds: ForgetPasswordRequest
):
    result = await users_service.forgot_pass(crds)
    return result

@router.post("/reset_password")
async def reset_password(
        users_service: Annotated[AuthService, Depends(auth_service)],
        crds: ResetPasswordRequest
):
    result = await users_service.reset_password(crds)
    return result