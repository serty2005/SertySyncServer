# app/crud/crud_server.py
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.server import Server # Модель таблицы
from app.schemas.server import ServerCreate, ServerUpdate # Схемы

class CRUDServer(CRUDBase[Server, ServerCreate, ServerUpdate]):
    async def get_by_iiko_uid(self, db: AsyncSession, *, iiko_uid: str) -> Optional[Server]:
        """Найти сервер по iiko_uid."""
        statement = select(self.model).where(self.model.iiko_uid == iiko_uid)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    # Можно добавить другие специфичные методы

server = CRUDServer(Server)