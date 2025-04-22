# app/crud/crud_workstation.py
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.workstation import Workstation # Модель таблицы
from app.schemas.workstation import WorkstationCreate, WorkstationUpdate # Схемы

class CRUDWorkstation(CRUDBase[Workstation, WorkstationCreate, WorkstationUpdate]):
    async def get_multi_by_point(
        self, db: AsyncSession, *, point_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Workstation]:
        """Получить рабочие станции для конкретной точки."""
        statement = (
            select(self.model)
            .where(self.model.point_id == point_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()

    # Можно добавить другие специфичные методы

workstation = CRUDWorkstation(Workstation)