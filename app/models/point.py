# app/models/point.py
import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from .base import BaseUUIDModel

if TYPE_CHECKING:
    from .company import Company
    from .server import Server
    from .workstation import Workstation

class PointBase(SQLModel):
    name: str = Field(index=True)
    address: str

class Point(BaseUUIDModel, PointBase, table=True):
    # Внешний ключ к таблице Company
    company_id: uuid.UUID = Field(foreign_key="company.id", index=True)

    # Внешний ключ к RMS-серверу точки. Может быть NULL, если сервер не назначен
    # или если точка работает через Chain (хотя станции все равно к RMS подключаются).
    # Сделаем Optional.
    server_id: Optional[uuid.UUID] = Field(default=None, foreign_key="server.id", index=True)

    # Связь многие-к-одному: много точек могут принадлежать одной компании
    company: "Company" = Relationship(back_populates="points")

    # Связь многие-к-одному: много точек могут подключаться к одному RMS-серверу
    server: Optional["Server"] = Relationship(back_populates="points")

    # Связь один-ко-многим: одна точка может иметь много рабочих станций
    workstations: List["Workstation"] = Relationship(back_populates="point")

# Схемы API
class PointCreate(PointBase):
    company_id: uuid.UUID # Нужно указать компанию при создании
    server_id: Optional[uuid.UUID] = None

class PointRead(PointBase):
    id: uuid.UUID
    company_id: uuid.UUID
    server_id: Optional[uuid.UUID]
    revision: int
    created_at: datetime
    updated_at: datetime
    # Можно добавить вложенное чтение компании, если нужно
    # company: Optional["CompanyRead"] = None

class PointUpdate(SQLModel):
    name: Optional[str] = None
    address: Optional[str] = None
    server_id: Optional[uuid.UUID] = None
    # company_id обычно не меняют, но можно добавить, если нужно