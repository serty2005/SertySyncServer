# alembic/env.py
import asyncio
from logging.config import fileConfig
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine # Используем асинхронный движок
from sqlalchemy import pool

from alembic import context

# --- Добавляем путь к нашему проекту ---
# Это нужно, чтобы Alembic мог найти модули 'app.core', 'app.models' и т.д.
# Определяем путь к корневой папке проекта (на уровень выше папки alembic)
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)
# ----------------------------------------

# --- Импортируем наши настройки и метаданные ---
from app.core.config import settings # Импортируем настройки приложения
# Импортируем базовый класс или все модели, чтобы метаданные были загружены
# Достаточно импортировать __init__.py из models, если он импортирует все модели
from app.models import * # Это загрузит все модели и их метаданные
from app.models.base import BaseUUIDModel # Убедимся, что базовая модель тоже импортирована
from sqlmodel import SQLModel # Импортируем SQLModel для доступа к metadata
# ---------------------------------------------

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Устанавливаем метаданные для Alembic ---
# target_metadata = None # Комментируем или удаляем эту строку
# Указываем Alembic использовать метаданные из наших SQLModel моделей
target_metadata = SQLModel.metadata
# ------------------------------------------

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# --- Функция для запуска миграций ---
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Используем DATABASE_URL из наших настроек
    url = str(settings.DATABASE_URL) # Преобразуем Pydantic DSN в строку
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Добавляем render_as_batch для поддержки SQLite и некоторых ограничений ALTER TABLE
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()

# --- Асинхронная функция для запуска миграций онлайн ---
async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Используем DATABASE_URL из наших настроек
    connectable = create_async_engine(
        str(settings.DATABASE_URL), # Преобразуем Pydantic DSN в строку
        poolclass=pool.NullPool, # Рекомендуется для Alembic онлайн миграций
        future=True # Используем SQLAlchemy 2.0 стиль
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose() # Закрываем движок

def do_run_migrations(connection):
    """Helper function to run migrations within the sync context of run_sync."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # Добавляем render_as_batch для поддержки ограничений ALTER TABLE
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()
# ----------------------------------------------------

# --- Выбор режима запуска ---
if context.is_offline_mode():
    run_migrations_offline()
else:
    # Запускаем асинхронную функцию в event loop
    asyncio.run(run_migrations_online())
# --------------------------