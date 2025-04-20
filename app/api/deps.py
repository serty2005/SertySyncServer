# app/api/deps.py
from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_token
from app.schemas.token import TokenPayload
from app.db.session import get_async_session # Импортируем зависимость сессии БД

# Определяем схему OAuth2: URL для получения токена
# Этот URL должен совпадать с путем к вашему эндпоинту логина
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/access-token"
)

async def get_db() -> Generator[AsyncSession, None, None]:
    """
    Зависимость для получения сессии базы данных.
    Переименовали из get_async_session для краткости в Depends().
    """
    async for session in get_async_session():
        yield session

async def verify_token(token: str = Depends(reusable_oauth2)) -> TokenPayload:
    """
    Зависимость для проверки Bearer токена.
    Декодирует токен и возвращает его payload, если он валиден.
    Выбрасывает HTTPException 401 или 403 в случае ошибки.
    """
    token_data = decode_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, # Или 403 Forbidden, если токен есть, но невалиден
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Можно добавить проверку прав доступа на основе token_data.sub, если нужно
    # Например, если у нас будут разные API логины с разными правами
    # if token_data.sub != settings.INITIAL_API_LOGIN: # Простой пример
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")

    return token_data

# Можно создать зависимость, которая просто проверяет токен, не возвращая payload,
# если payload не нужен в самом эндпоинте
async def ensure_token_is_valid(token_payload: TokenPayload = Depends(verify_token)):
    """
    Простая зависимость, которая удостоверяется, что токен валиден.
    Использует verify_token, но ничего не возвращает явно.
    Удобно использовать в Depends([...]), когда payload не нужен.
    """
    pass # Если verify_token не выбросил исключение, значит токен валиден