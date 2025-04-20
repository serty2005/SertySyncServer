# app/models/server.py
import uuid
import re # Для валидации iiko_uid
from datetime import datetime
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from pydantic import field_validator, ValidationInfo, AnyHttpUrl

from .base import BaseUUIDModel
from .enums import ServerType, LicenseType, ConnectionType

if TYPE_CHECKING:
    from .point import Point
    from .workstation import Workstation

# Регулярное выражение для iiko-UID (3 блока по 3 цифры через дефис)
IIKO_UID_REGEX = re.compile(r"^\d{3}-\d{3}-\d{3}$")

class ServerBase(SQLModel):
    name: str = Field(index=True)
    server_type: ServerType = Field(default=ServerType.RMS)
    iiko_uid: str = Field(unique=True, index=True, max_length=11) # Формат XXX-XXX-XXX
    license_type: LicenseType = Field(default=LicenseType.CLOUD)
    address: Optional[str] = Field(default=None, index=True) # URL для Cloud, IP/Hostname для Lifetime
    # Используем JSON для хранения деталей подключений (более гибко)
    # Пример: {"type": "Teamviewer", "id": "123456789"} или [{"type": "RDP", "host": "192.168.1.100", "port": 3389}]
    connection_details: Optional[Dict[str, Any] | List[Dict[str, Any]]] = Field(default=None, sa_column=Column(JSON))
    partner_portal_id: Optional[str] = Field(default=None, index=True)

    # Валидация iiko_uid
    @field_validator('iiko_uid', mode='after')
    @classmethod
    def validate_iiko_uid(cls, v: str) -> str:
        if not IIKO_UID_REGEX.match(v):
            raise ValueError('Invalid iiko-UID format. Expected XXX-XXX-XXX')
        return v

    # Валидация адреса и подключения в зависимости от типа лицензии
    @field_validator('address', mode='after')
    @classmethod
    def validate_address(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        license_type = info.data.get('license_type')
        if license_type == LicenseType.CLOUD and v:
            # Простая проверка на ожидаемые домены (можно усложнить)
            if not (v.endswith('.iiko.it') or v.endswith('.syrve.online')):
                 # Позволим и другие URL через AnyHttpUrl
                try:
                    AnyHttpUrl(v) # Проверяем, что это валидный URL
                except ValueError:
                     raise ValueError('Cloud server address should be a valid URL (e.g., *.iiko.it or *.syrve.online)')
        elif license_type == LicenseType.LIFETIME and not v:
             # Для Lifetime адрес не обязателен, но желателен
             pass # Можно добавить предупреждение или требование
        return v

    @field_validator('connection_details', mode='after')
    @classmethod
    def validate_connection_details(
            cls,
            v: Optional[Dict[str, Any] | List[Dict[str, Any]]],
            info: ValidationInfo
    ) -> Optional[Dict[str, Any] | List[Dict[str, Any]]]:
        license_type = info.data.get('license_type')
        if license_type == LicenseType.LIFETIME and not v:
            raise ValueError('Connection details (Teamviewer, RDP, Anydesk, etc.) are required for Lifetime license servers')
        if license_type == LicenseType.CLOUD and v:
             # Для Cloud подключение обычно не нужно
             # Можно выдать предупреждение или очистить поле
             print(f"Warning: Connection details provided for Cloud server. They might not be applicable.")
             # return None # Раскомментировать, если хотим принудительно очищать
        return v

class Server(BaseUUIDModel, ServerBase, table=True):
    # Связь один-ко-многим: один RMS-сервер может обслуживать несколько точек
    # Для Chain-серверов этот список будет пустым
    points: List["Point"] = Relationship(back_populates="server")

    # Связь один-ко-многим: один RMS-сервер может иметь много рабочих станций
    # Для Chain-серверов этот список будет пустым
    workstations: List["Workstation"] = Relationship(back_populates="server")

# --- Схемы API ---
class ServerCreate(ServerBase):
    pass

class ServerRead(ServerBase):
    id: uuid.UUID
    revision: int
    created_at: datetime
    updated_at: datetime
    # Можно добавить вывод связанных объектов, если нужно
    # points: List["PointRead"] = []
    # workstations: List["WorkstationRead"] = []

class ServerUpdate(SQLModel):
    name: Optional[str] = None
    server_type: Optional[ServerType] = None
    # iiko_uid обычно не меняется, но можно разрешить
    # iiko_uid: Optional[str] = None
    license_type: Optional[LicenseType] = None
    address: Optional[str] = None
    connection_details: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None
    partner_portal_id: Optional[str] = None
    # Добавим валидаторы и сюда, если нужно проверять при обновлении
    # (SQLModel/Pydantic автоматически вызовет их, если поля присутствуют)