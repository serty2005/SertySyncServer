# app/models/workstation.py
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, JSON

from .base import BaseUUIDModel
#from .enums import ConnectionType # Если будем типизировать connection_details

if TYPE_CHECKING:
    from .point import Point
    from .server import Server
    from .fiscal_registrar import FiscalRegistrar

class WorkstationBase(SQLModel):
    name: Optional[str] = Field(default=None, index=True) # Имя хоста или описание
    # Можно хранить несколько подключений в списке JSON
    # Пример: [{"type": "Anydesk", "id": "111222333"}, {"type": "Teamviewer", "id": "987654321"}]
    connection_details: Optional[List[Dict[str, Any]]] = Field(default=None, sa_column=Column(JSON))
    # Доп. оборудование можно тоже хранить в JSON
    # Пример: {"scanner": "Honeywell Voyager", "scales": "CAS AP-15"}
    extra_equipment: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

class Workstation(BaseUUIDModel, WorkstationBase, table=True):
    # Внешний ключ к точке
    point_id: uuid.UUID = Field(foreign_key="point.id", index=True)
    # Внешний ключ к RMS-серверу (может быть Null, если точка еще не настроена?)
    # Или всегда должен быть? Зависит от бизнес-логики. Сделаем обязательным.
    server_id: uuid.UUID = Field(foreign_key="server.id", index=True)

    # Связь многие-к-одному: много станций принадлежат одной точке
    point: "Point" = Relationship(back_populates="workstations")
    # Связь многие-к-одному: много станций подключаются к одному RMS-серверу
    server: "Server" = Relationship(back_populates="workstations")

    # Связь один-ко-многим: одна станция может иметь несколько ФР (обычно 1 или 2)
    fiscal_registrars: List["FiscalRegistrar"] = Relationship(back_populates="workstation")

# --- Схемы API ---
class WorkstationCreate(WorkstationBase):
    point_id: uuid.UUID
    server_id: uuid.UUID # Сервер должен быть известен при создании станции

class WorkstationRead(WorkstationBase):
    id: uuid.UUID
    point_id: uuid.UUID
    server_id: uuid.UUID
    revision: int
    created_at: datetime
    updated_at: datetime
    # fiscal_registrars: List["FiscalRegistrarRead"] = [] # Можно добавить

class WorkstationUpdate(SQLModel):
    name: Optional[str] = None
    connection_details: Optional[List[Dict[str, Any]]] = None
    extra_equipment: Optional[Dict[str, Any]] = None
    # point_id и server_id обычно не меняются, но можно добавить