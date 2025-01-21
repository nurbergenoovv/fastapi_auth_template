import asyncio
import logging
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import API_ROUTER

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log", mode="a", encoding="utf-8"),
        logging.StreamHandler()  # Логирование также в консоль
    ]
)

logger = logging.getLogger(__name__)
logger.name = "Main"


async def on_startup_action():
    logger.info("Starting application")

app = FastAPI(
    title="FastAPI-AUTH",
    root_path="/api/v1",
    version="0.0.1",
    description=(
        "Шаблон проекта на FastAPI c аутентификацией (JWT), который поможет быстро "
        "стартовать разработку веб-приложения. Включает в себя пример структуры папок, "
        "базовую конфигурацию, модели пользователей, эндпоинты для регистрации/входа, а "
        "также примеры интеграции с базой данных и миграциями."
    )
)


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(API_ROUTER)


@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Hello World"}


if __name__ == "__main__":
    logger.info("Starting application")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
