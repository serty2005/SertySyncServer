# app/models/fiscal_registrar.py
import uuid
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship # Убираем SQLModel
from .base import BaseUUIDModel

if TYPE_CHECKING:
    from .workstation import Workstation

# Модель таблицы FiscalRegistrar
class FiscalRegistrar(BaseUUIDModel, table=True):
    # Явно определяем поля
    model: str = Field(index=True)
    serial_number: str = Field(index=True, unique=True)
    registration_number: Optional[str] = Field(default=None, index=True, unique=True)
    registered_entity_name: Optional[str] = Field(default=None)
    fiscal_drive_number: Optional[str] = Field(default=None, index=True, unique=True)
    # Типы DateTime и Date будут унаследованы из аннотаций Python
    last_registration_date: Optional[datetime] = Field(default=None)
    fiscal_drive_expiry_date: Optional[date] = Field(default=None)

    # Внешний ключ и связь
    workstation_id: uuid.UUID = Field(foreign_key="workstation.id", index=True)
    workstation: "Workstation" = Relationship(back_populates="fiscal_registrars")