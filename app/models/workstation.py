# app/models/workstation.py
import uuid
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from sqlmodel import Field, Relationship, Column, JSON # Убираем SQLModel
from .base import BaseUUIDModel

if TYPE_CHECKING:
    from .point import Point
    from .server import Server
    from .fiscal_registrar import FiscalRegistrar

# Модель таблицы Workstation
class Workstation(BaseUUIDModel, table=True):
    # Явно определяем поля
    name: Optional[str] = Field(default=None, index=True)
    connection_details: Optional[List[Dict[str, Any]]] = Field(default=None, sa_column=Column(JSON))
    extra_equipment: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    # Внешние ключи и связи
    point_id: uuid.UUID = Field(foreign_key="point.id", index=True)
    server_id: uuid.UUID = Field(foreign_key="server.id", index=True)

    point: "Point" = Relationship(back_populates="workstations")
    server: "Server" = Relationship(back_populates="workstations")
    fiscal_registrars: List["FiscalRegistrar"] = Relationship(back_populates="workstation")