# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.security import verify_password, create_access_token
from app.schemas.token import Token

router = APIRouter()

@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    Использует стандартную форму `application/x-www-form-urlencoded`.
    Поля: `username` и `password`.
    """
    # В нашем случае "username" - это API логин
    api_login = form_data.username
    # "password" - это API пароль/ключ
    api_password = form_data.password

    # Проверяем совпадение логина
    if api_login != settings.INITIAL_API_LOGIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect API login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Проверяем совпадение пароля (с хешем)
    # Убедитесь, что HASHED_INITIAL_API_PASSWORD настроен в config и .env
    if not verify_password(api_password, settings.HASHED_INITIAL_API_PASSWORD):
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect API login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Логин и пароль верны, генерируем токен
    access_token = create_access_token(
        subject=api_login # В качестве subject используем API логин
    )

    return {"access_token": access_token, "token_type": "bearer"}