# app/schemas/fiscal_registrar.py
import uuid
from datetime import datetime, date
from typing import Optional
from sqlmodel import SQLModel, Field

# Базовая схема FiscalRegistrar
class FiscalRegistrarBase(SQLModel):
    model: str = Field(..., max_length=100)
    serial_number: str = Field(..., max_length=50) # Уникальность в БД/CRUD
    registration_number: Optional[str] = Field(default=None, max_length=30) # Уникальность в БД/CRUD
    registered_entity_name: Optional[str] = Field(default=None, max_length=255)
    fiscal_drive_number: Optional[str] = Field(default=None, max_length=30) # Уникальность в БД/CRUD
    last_registration_date: Optional[datetime] = None # Валидация формата Pydantic
    fiscal_drive_expiry_date: Optional[date] = None # Валидация формата Pydantic

# Схема для создания FiscalRegistrar
class FiscalRegistrarCreate(FiscalRegistrarBase):
    workstation_id: uuid.UUID

# Схема для чтения FiscalRegistrar
class FiscalRegistrarRead(FiscalRegistrarBase):
    id: uuid.UUID
    workstation_id: uuid.UUID
    revision: int
    created_at: datetime
    updated_at: datetime

# Схема для обновления FiscalRegistrar
class FiscalRegistrarUpdate(SQLModel):
    model: Optional[str] = Field(default=None, max_length=100)
    # serial_number обычно не меняется
    registration_number: Optional[str] = Field(default=None, max_length=30)
    registered_entity_name: Optional[str] = Field(default=None, max_length=255)
    fiscal_drive_number: Optional[str] = Field(default=None, max_length=30)
    last_registration_date: Optional[datetime] = None
    fiscal_drive_expiry_date: Optional[date] = None
    workstation_id: Optional[uuid.UUID] = None # Можно менять