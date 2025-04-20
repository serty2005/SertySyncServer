# app/models/company.py
from typing import List, TYPE_CHECKING
from sqlmodel import Field, Relationship

from .base import BaseUUIDModel

# Предотвращение циклических импортов для type hints
if TYPE_CHECKING:
    from .point import Point

class Company(BaseUUIDModel, table=True):
    # __tablename__ генерируется автоматически SQLModel как 'company'
    # Связь один-ко-многим: одна компания может иметь много точек
    name: str = Field(index=True)
    billing_inn: str = Field(index=True, unique=True, max_length=12) # ИНН ЮЛ = 10, ИП = 12
    iiko_inn: str = Field(index=True, unique=True, max_length=12)
    points: List["Point"] = Relationship(back_populates="company")

