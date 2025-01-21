from fastapi import APIRouter
from app.api.auth import router as AuthRouter

API_ROUTER = APIRouter()

API_ROUTER.include_router(AuthRouter)
