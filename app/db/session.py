# app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel # Импортируем SQLModel для метаданных
from typing import AsyncGenerator

from app.core.config import settings

# Проверяем, что DATABASE_URL точно задан
if settings.DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in the environment variables")

# Создаем асинхронный движок SQLAlchemy
# echo=True полезно для отладки, показывает генерируемые SQL-запросы. В продакшене лучше убрать.
engine = create_async_engine(str(settings.DATABASE_URL), echo=False, future=True)

# Создаем фабрику асинхронных сессий
AsyncSessionFactory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False, # Важно для FastAPI, чтобы объекты были доступны после коммита
)

# Функция-генератор для получения сессии в зависимостях FastAPI
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields an async session.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            # Пока не делаем автоматический коммит здесь,
            # лучше делать его явно в CRUD операциях или роутах
            # await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Функция для инициализации базы данных (создания таблиц)
# В реальном приложении лучше использовать Alembic миграции
async def init_db():
    async with engine.begin() as conn:
        # Включите эту строку, если хотите удалять все таблицы при каждом запуске (для разработки)
        await conn.run_sync(SQLModel.metadata.drop_all)
        # Создает таблицы на основе метаданных из ваших SQLModel моделей
        await conn.run_sync(SQLModel.metadata.create_all)