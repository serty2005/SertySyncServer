# app/models/fiscal_registrar.py
import uuid
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from .base import BaseUUIDModel

if TYPE_CHECKING:
    from .workstation import Workstation

class FiscalRegistrarBase(SQLModel):
    model: str = Field(index=True)
    # Уникальность номеров лучше обеспечивать на уровне БД или логики приложения
    serial_number: str = Field(index=True, unique=True)
    registration_number: Optional[str] = Field(default=None, index=True, unique=True) # РНМ ККТ
    registered_entity_name: Optional[str] = Field(default=None) # Юрлицо/ИП регистрации
    fiscal_drive_number: Optional[str] = Field(default=None, index=True, unique=True) # Номер ФН
    last_registration_date: Optional[datetime] = Field(default=None) # Дата и время регистрации/перерегистрации
    fiscal_drive_expiry_date: Optional[date] = Field(default=None) # Дата окончания срока действия ФН

class FiscalRegistrar(BaseUUIDModel, FiscalRegistrarBase, table=True):
    # Внешний ключ к рабочей станции
    workstation_id: uuid.UUID = Field(foreign_key="workstation.id", index=True)

    # Связь многие-к-одному: много ФР могут быть подключены к одной станции (хотя обычно 1-2)
    workstation: "Workstation" = Relationship(back_populates="fiscal_registrars")

# --- Схемы API ---
class FiscalRegistrarCreate(FiscalRegistrarBase):
    workstation_id: uuid.UUID

class FiscalRegistrarRead(FiscalRegistrarBase):
    id: uuid.UUID
    workstation_id: uuid.UUID
    revision: int
    created_at: datetime
    updated_at: datetime

class FiscalRegistrarUpdate(SQLModel):
    model: Optional[str] = None
    # serial_number обычно не меняется
    registration_number: Optional[str] = None
    registered_entity_name: Optional[str] = None
    fiscal_drive_number: Optional[str] = None
    last_registration_date: Optional[datetime] = None
    fiscal_drive_expiry_date: Optional[date] = None
    # workstation_id можно менять, если ФР переподключили к другой станции
    workstation_id: Optional[uuid.UUID] = None