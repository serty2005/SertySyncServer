# app/models/base.py
import uuid
from datetime import datetime, timezone
from sqlalchemy import func, Column, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import SQLModel, Field # Снова импортируем Field
from sqlalchemy.orm import declared_attr

class BaseUUIDModel(SQLModel):

    # --- Определения колонок SQLAlchemy через @declared_attr ---
    # Они определяют фактическую структуру в БД.
    @declared_attr
    def id(cls) -> Column:
        return Column(
            PG_UUID(as_uuid=True),
            primary_key=True, # Определяем для SQLAlchemy
            server_default=func.gen_random_uuid(),
            index=True,
            nullable=False
        )

    @declared_attr
    def revision(cls) -> Column:
        return Column(
            Integer,
            nullable=False,
            server_default='1'
        )

    @declared_attr
    def created_at(cls) -> Column:
        return Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now()
        )

    @declared_attr
    def updated_at(cls) -> Column:
        return Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now()
        )

    # --- Аннотации типов Python + Подсказки для SQLModel/Pydantic ---
    # Они нужны для валидации, сериализации и для того, чтобы SQLModel
    # правильно настроил маппер.

    id: uuid.UUID = Field(
        default=None, # Значение Python по умолчанию (БД сгенерирует)
        primary_key=True # Добавляем подсказку для SQLModel
        # Не дублируем index, nullable и т.д. здесь
    )
    revision: int = Field(
        default=1 # Значение Python по умолчанию
    )
    created_at: datetime = Field(
        # Значение Python по умолчанию (фабрика)
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        # Значение Python по умолчанию (фабрика)
        default_factory=lambda: datetime.now(timezone.utc)
    )