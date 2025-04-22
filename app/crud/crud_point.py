# app/crud/crud_point.py
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.point import Point # Модель таблицы
from app.schemas.point import PointCreate, PointUpdate # Схемы

class CRUDPoint(CRUDBase[Point, PointCreate, PointUpdate]):
    async def get_multi_by_company(
        self, db: AsyncSession, *, company_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Point]:
        """Получить точки для конкретной компании."""
        statement = (
            select(self.model)
            .where(self.model.company_id == company_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()

    # Можно добавить другие специфичные методы

point = CRUDPoint(Point)