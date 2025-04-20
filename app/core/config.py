# app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, PostgresDsn, validator, field_validator
from typing import List, Union, Optional, Dict, Any

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sync Service API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    HASHED_INITIAL_API_PASSWORD: str

    # Данные для первичной авторизации (загружаются из .env)
    INITIAL_API_LOGIN: str
    INITIAL_API_PASSWORD: str

    # Настройки CORS (Cross-Origin Resource Sharing) - разрешаем все для простоты
    # В продакшене лучше указать конкретные домены фронтенда
    BACKEND_CORS_ORIGINS: List[Union[AnyHttpUrl, str]] = ["*"] # Или ["http://localhost:3000", "https://yourfrontend.com"]

    # Настройки базы данных
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    DATABASE_URL: Optional[PostgresDsn] = None

    @validator("DATABASE_URL", pre=True, always=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            # Если DATABASE_URL уже задан явно, используем его
            return v
        # Если DATABASE_URL не задан, пытаемся собрать из отдельных компонентов
        # (Это может быть полезно для некоторых сред развертывания)
        server = values.get("POSTGRES_SERVER")
        user = values.get("POSTGRES_USER")
        password = values.get("POSTGRES_PASSWORD")
        db = values.get("POSTGRES_DB")
        if all([server, user, password, db]):
            return PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=user,
                password=password,
                host=server,
                path=f"/{db}",
            )
        raise ValueError("Database connection details are missing. Provide DATABASE_URL or POSTGRES_SERVER, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB.")


    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() # type: ignore

# Проверка, что секретный ключ не остался дефолтным (простая)
if settings.SECRET_KEY == "your_super_secret_random_key_here":
    print("WARNING: Default SECRET_KEY is used. Please generate and set a secure key in the .env file.")
# Проверка, что пароль не остался дефолтным
if settings.INITIAL_API_PASSWORD == "changeme":
    print("WARNING: Default INITIAL_API_PASSWORD is used. Please change it in the .env file.")
if not settings.DATABASE_URL:
     print("ERROR: DATABASE_URL is not configured in the .env file.")