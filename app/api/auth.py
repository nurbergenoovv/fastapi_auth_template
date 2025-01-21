import logging
from typing import Annotated

from fastapi import APIRouter, Response, Request, BackgroundTasks
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

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

# Получение логгера для текущего модуля
logger = logging.getLogger(__name__)
logger.name = "Auth-Router"


@router.get("/")
async def get_all(
        users_service: Annotated[AuthService, Depends(auth_service)],
        request: Request
):
    logger.info(f"{request.client.host} | Получение всех пользователей")
    users = await users_service.get_users()
    return users


@router.post("/")
async def create_user(
        crds: UserCreate,
        users_service: Annotated[AuthService, Depends(auth_service)],
        response: Response,
        request: Request
):
    user_id = await users_service.add_user(crds, response)
    logger.info(f"{request.client.host} | Создан пользователь с email {crds.email}")
    return {"user_id": user_id}


@router.post("/login")
async def login(
        crds: UserLogin,
        users_service: Annotated[AuthService, Depends(auth_service)],
        response: Response,
        request: Request
):
    try:
        user_id = await users_service.user_login(crds, response)
        logger.info(f"{request.client.host} | Вход пользователя с email {crds.email}")
        return {"user_id": user_id}
    except Exception as e:
        logger.error(f"{request.client.host} | Ошибка при входе пользователя с email {crds.email}: {e}")
        raise e  # Или верните соответствующий ответ


@router.get("/logout")
async def logout(
        users_service: Annotated[AuthService, Depends(auth_service)],
        response: Response,
        request: Request
):
    logger.info(f"{request.client.host} | Выход пользователя")
    return await users_service.logout(response)


@router.post("/current_user")
async def me(
        users_service: Annotated[AuthService, Depends(auth_service)],
        request: Request,
):
    user = await users_service.get_current_user(request)
    logger.info(f"{request.client.host} | Получение информации о пользователе с id {user['id']}")
    return user


@router.put('/{user_id}')
async def update_user(
        users_service: Annotated[AuthService, Depends(auth_service)],
        user_id: int,
        crds: UserUpdate,
        response: Response,
        request: Request
):
    result = await users_service.update_user(user_id, crds, response)
    logger.info(f"{request.client.host} | Обновление информации пользователя с email {crds.email}")
    return result


@router.post("/forgot_password")
async def forget_password(
        users_service: Annotated[AuthService, Depends(auth_service)],
        crds: ForgetPasswordRequest,
        request: Request,
        backtask: BackgroundTasks
):
    result = await users_service.forgot_pass(crds, backtask)
    logger.info(f"{request.client.host} | Запрос сброса пароля для пользователя с email {crds.email}")
    return result


@router.post("/reset_password")
async def reset_password(
        users_service: Annotated[AuthService, Depends(auth_service)],
        crds: ResetPasswordRequest,
        request: Request
):
    result = await users_service.reset_password(crds)
    logger.info(f"{request.client.host} | Сброс пароля для пользователя с email {crds.email}")
    return result


@router.delete("/{user_id}")
async def delete_user(
        users_service: Annotated[AuthService, Depends(auth_service)],
        user_id: int,
        request: Request
):
    result = await users_service.delete_user(user_id)
    logger.info(f"{request.client.host} | Удаление пользователя с id {user_id}")
    return result
