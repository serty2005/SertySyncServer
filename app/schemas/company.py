# app/schemas/company.py
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel # Используем SQLModel для Base, чтобы не дублировать поля

# Базовая схема с общими полями для Company
# Наследуем от SQLModel, т.к. от нее наследуется и модель таблицы Company
class CompanyBase(SQLModel):
    name: str
    billing_inn: str # Уникальность проверяется в API/CRUD
    iiko_inn: str    # Уникальность проверяется в API/CRUD

# Схема для создания компании (данные из запроса)
class CompanyCreate(CompanyBase):
    pass # Поля те же, что в CompanyBase

# Схема для чтения компании (данные в ответе)
class CompanyRead(CompanyBase):
    id: uuid.UUID
    revision: int
    created_at: datetime
    updated_at: datetime

# Схема для обновления компании (частичные данные в запросе)
class CompanyUpdate(SQLModel): # Можно от SQLModel или BaseModel
    name: Optional[str] = None
    billing_inn: Optional[str] = None
    iiko_inn: Optional[str] = None
    # revision не обновляется напрямую через API