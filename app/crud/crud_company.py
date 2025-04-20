# app/crud/crud_company.py
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# 1. Импортируем базовый CRUD класс
from app.crud.base import CRUDBase

# 2. Импортируем МОДЕЛЬ ТАБЛИЦЫ из app.models
from app.models.company import Company

# 3. Импортируем СХЕМЫ Pydantic из app.schemas
#    Можно импортировать конкретные схемы напрямую:
from app.schemas.company import CompanyCreate, CompanyUpdate
#    Или импортировать весь модуль schemas и использовать префикс:
#    from app import schemas # Тогда ниже будет schemas.CompanyCreate

class CRUDCompany(CRUDBase[Company, CompanyCreate, CompanyUpdate]):
    """
    CRUD операции для модели Company.
    Наследует общие методы от CRUDBase и добавляет специфичные.
    Типы Company, CompanyCreate, CompanyUpdate используются как type hints
    для Generic-класса CRUDBase.
    """
    async def get_by_inn(self, db: AsyncSession, *, inn: str) -> Optional[Company]:
        """
        Найти компанию по ИНН (billing_inn или iiko_inn).
        Возвращает объект модели Company (из app.models).
        """
        statement = select(self.model).where(
            (self.model.billing_inn == inn) | (self.model.iiko_inn == inn)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    # Здесь можно добавить другие специфичные для компаний методы поиска или обработки
    # Например, поиск по имени, подсчет точек компании и т.д.

# Создаем единственный экземпляр CRUDCompany для использования в API.
# Передаем класс модели Company (из app.models) в конструктор.
company = CRUDCompany(Company)