# app/schemas/workstations.py
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import SQLModel, Field

# Базовая схема Workstation
class WorkstationBase(SQLModel):
    name: Optional[str] = Field(default=None, max_length=255)
    connection_details: Optional[List[Dict[str, Any]]] = None
    extra_equipment: Optional[Dict[str, Any]] = None

# Схема для создания Workstation
class WorkstationCreate(WorkstationBase):
    point_id: uuid.UUID
    server_id: uuid.UUID

# Схема для чтения Workstation
class WorkstationRead(WorkstationBase):
    id: uuid.UUID
    point_id: uuid.UUID
    server_id: uuid.UUID
    revision: int
    created_at: datetime
    updated_at: datetime
    # fiscal_registrars: List["FiscalRegistrarRead"] = [] # Если нужно

# Схема для обновления Workstation
class WorkstationUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=255)
    connection_details: Optional[List[Dict[str, Any]]] = None
    extra_equipment: Optional[Dict[str, Any]] = None
    # point_id и server_id обычно не меняются