from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.repositories.auth import AuthRepository
from app.services.auth import AuthService




def auth_service(session: AsyncSession = Depends(get_async_session)):
    return AuthService(AuthRepository, session)