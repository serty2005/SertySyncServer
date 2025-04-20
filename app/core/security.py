# app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.token import TokenPayload # Создадим этот файл следующим

# Контекст для хеширования паролей/ключей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Алгоритм подписи JWT
ALGORITHM = "HS256"

def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Генерирует новый JWT access token.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет обычный пароль/ключ API против хешированного.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Генерирует хеш для пароля/ключа API.
    """
    return pwd_context.hash(password)

def decode_token(token: str) -> Optional[TokenPayload]:
    """
    Декодирует токен и валидирует его содержимое.
    Возвращает payload или None в случае ошибки.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        # Валидируем содержимое payload с помощью Pydantic схемы
        token_data = TokenPayload(**payload)
        # Дополнительная проверка времени жизни (хотя jwt.decode это тоже делает)
        if token_data.exp < datetime.now(timezone.utc):
            print("Token expired") # Или логирование
            return None
        return token_data
    except (JWTError, ValidationError, KeyError) as e:
        # Логируем ошибку или обрабатываем иначе
        print(f"Token validation error: {e}")
        return None

# --- Хеш для нашего "начального" пароля ---
# Этот хеш можно сгенерировать один раз и вставить в .env или хранить где-то
# Либо генерировать при старте, если пароль меняется только через .env
# Пример генерации:
# from app.core.security import get_password_hash
# print(get_password_hash(settings.INITIAL_API_PASSWORD))
# Замените 'hashed_initial_password_here' на результат выполнения print() выше
# Важно: Не храните сам пароль в коде после генерации хеша!
# Лучше читать хеш из переменной окружения или конфигурации.
# Добавим переменную HASHED_INITIAL_API_PASSWORD в .env и config.py

# --- Обновим config.py и .env ---
# 1. Сгенерируйте хеш:
#    python -c "from app.core.security import get_password_hash; from app.core.config import settings; print(get_password_hash(settings.INITIAL_API_PASSWORD))"
# 2. Добавьте результат в .env:
#    HASHED_INITIAL_API_PASSWORD="результат_хеширования_bcrypt_здесь"
# 3. Добавьте поле в Settings в config.py:
#    HASHED_INITIAL_API_PASSWORD: str