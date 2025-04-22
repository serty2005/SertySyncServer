# app/models/point.py
import uuid

from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship

from .base import BaseUUIDModel

if TYPE_CHECKING:
    from .company import Company
    from .server import Server
    from .workstation import Workstation

class Point(BaseUUIDModel, table=True):

    name: str = Field(index=True)
    address: str

    # Внешние связаные сущности
    company_id: uuid.UUID = Field(foreign_key="company.id", index=True)
    server_id: Optional[uuid.UUID] = Field(default=None, foreign_key="server.id", index=True)

    # Связь многие-к-одному: много точек могут принадлежать одной компании
    company: "Company" = Relationship(back_populates="points")
    # Связь многие-к-одному: много точек могут подключаться к одному RMS-серверу
    server: Optional["Server"] = Relationship(back_populates="points")
    # Связь один-ко-многим: одна точка может иметь много рабочих станций
    workstations: List["Workstation"] = Relationship(back_populates="point")
