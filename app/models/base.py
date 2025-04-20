# app/models/base.py
import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import func, DateTime  # Для серверных значений по умолчанию

class BaseUUIDModel(SQLModel):
    # Используем UUID как первичный ключ
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        sa_column_kwargs={"server_default": func.gen_random_uuid()} # Генерировать UUID на стороне БД
    )
    revision: int = Field(default=1, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()} # Использовать время БД
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": func.now(), # Использовать время БД
            "onupdate": func.now()        # Обновлять время БД при апдейте записи
        }
    )