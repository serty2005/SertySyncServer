# app/schemas/point.py
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel

# Базовая схема Point
class PointBase(SQLModel):
    name: str
    address: str

# Схема для создания Point
class PointCreate(PointBase):
    company_id: uuid.UUID # Обязательно при создании
    server_id: Optional[uuid.UUID] = None # Необязательно

# Схема для чтения Point
class PointRead(PointBase):
    id: uuid.UUID
    company_id: uuid.UUID
    server_id: Optional[uuid.UUID]
    revision: int
    created_at: datetime # Будет timezone-aware из БД
    updated_at: datetime # Будет timezone-aware из БД
    # Если захотим возвращать вложенные объекты:
    # company: Optional["CompanyRead"] = None # Потребует импорта CompanyRead
    # server: Optional["ServerRead"] = None   # Потребует импорта ServerRead

# Схема для обновления Point
class PointUpdate(SQLModel):
    name: Optional[str] = None
    address: Optional[str] = None
    server_id: Optional[uuid.UUID] = None
    # company_id обычно не меняется