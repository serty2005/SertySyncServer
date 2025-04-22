# app/crud/crud_fiscal_registrar.py
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.fiscal_registrar import FiscalRegistrar # Модель таблицы
from app.schemas.fiscal_registrar import FiscalRegistrarCreate, FiscalRegistrarUpdate # Схемы

class CRUDFiscalRegistrar(CRUDBase[FiscalRegistrar, FiscalRegistrarCreate, FiscalRegistrarUpdate]):
    async def get_by_serial_number(
        self, db: AsyncSession, *, serial_number: str
    ) -> Optional[FiscalRegistrar]:
        """Найти ФР по серийному номеру."""
        statement = select(self.model).where(self.model.serial_number == serial_number)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_multi_by_workstation(
        self, db: AsyncSession, *, workstation_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[FiscalRegistrar]:
        """Получить ФР для конкретной рабочей станции."""
        statement = (
            select(self.model)
            .where(self.model.workstation_id == workstation_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()

    # Можно добавить другие специфичные методы

fiscal_registrar = CRUDFiscalRegistrar(FiscalRegistrar)