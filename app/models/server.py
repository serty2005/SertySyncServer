# app/models/server.py
import re # Для валидации iiko_uid
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from sqlmodel import Field, Relationship, Column, JSON

from .base import BaseUUIDModel
from .enums import ServerType, LicenseType

if TYPE_CHECKING:
    from .point import Point
    from .workstation import Workstation

# Регулярное выражение для iiko-UID (3 блока по 3 цифры через дефис)
IIKO_UID_REGEX = re.compile(r"^\d{3}-\d{3}-\d{3}$")

class Server(BaseUUIDModel, table=True):
    name: str = Field(index=True, max_length=255) # Добавим max_length для консистентности
    server_type: ServerType = Field(default=ServerType.RMS)
    iiko_uid: str = Field(unique=True, index=True, max_length=11)
    license_type: LicenseType = Field(default=LicenseType.CLOUD)
    # Убедимся, что длины достаточно для нормализованного URL
    address: Optional[str] = Field(default=None, index=True, max_length=512)
    connection_details: Optional[Dict[str, Any] | List[Dict[str, Any]]] = Field(default=None, sa_column=Column(JSON))
    # Убедимся, что длины достаточно для ID
    partner_portal_id: Optional[str] = Field(default=None, index=True, max_length=50)

    # Связи остаются
    points: List["Point"] = Relationship(back_populates="server")
    workstations: List["Workstation"] = Relationship(back_populates="server")