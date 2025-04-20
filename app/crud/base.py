# app/crud/base.py
import uuid
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, func # Добавляем func для count
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel # Используем SQLModel

# Определяем типовые переменные для моделей SQLAlchemy/SQLModel и схем Pydantic
ModelType = TypeVar("ModelType", bound=SQLModel) # Модель таблицы (наследуется от SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel) # Схема для создания
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel) # Схема для обновления

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        Базовый CRUD класс с асинхронными методами.

        **Параметры**

        * `model`: Класс модели SQLModel, например, `Company`.
        """
        self.model = model

    async def get(self, db: AsyncSession, id: uuid.UUID) -> Optional[ModelType]:
        """Получить одну запись по ID."""
        statement = select(self.model).where(self.model.id == id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Получить список записей с пагинацией."""
        statement = select(self.model).offset(skip).limit(limit)
        result = await db.execute(statement)
        return result.scalars().all() # Возвращает список объектов модели

    async def get_count(self, db: AsyncSession) -> int:
        """Получить общее количество записей."""
        statement = select(func.count()).select_from(self.model)
        result = await db.execute(statement)
        return result.scalar_one()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """Создать новую запись."""
        # Преобразуем Pydantic схему в словарь
        obj_in_data = jsonable_encoder(obj_in)
        # Создаем экземпляр модели SQLAlchemy/SQLModel
        db_obj = self.model(**obj_in_data)
        # Добавляем в сессию и коммитим
        db.add(db_obj)
        await db.commit()
        # Обновляем объект из БД, чтобы получить сгенерированные значения (id, created_at и т.д.)
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Обновить существующую запись."""
        # Получаем данные для обновления (либо из схемы Pydantic, либо из словаря)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # exclude_unset=True - обновляем только переданные поля
            update_data = obj_in.model_dump(exclude_unset=True)

        # Обновляем поля объекта модели
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        # --- Логика инкремента ревизии ---
        if hasattr(db_obj, "revision"):
             # Проверяем, были ли реальные изменения (кроме updated_at, revision)
             # Это важно, чтобы не инкрементировать ревизию при пустом апдейте
             # Note: SQLAlchemy отслеживает изменения, можно проверить db.is_modified(db_obj)
             # Но простой инкремент при любом вызове update тоже допустим, если не критично
             if db.is_modified(db_obj):
                 db_obj.revision += 1 # type: ignore
        # ---------------------------------

        db.add(db_obj) # Добавляем объект в сессию (даже если он уже там, это пометит его как измененный)
        await db.commit()
        await db.refresh(db_obj) # Обновляем объект из БД
        return db_obj

    async def remove(self, db: AsyncSession, *, id: uuid.UUID) -> Optional[ModelType]:
        """Удалить запись по ID."""
        statement = select(self.model).where(self.model.id == id)
        result = await db.execute(statement)
        obj = result.scalar_one_or_none()
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj # Возвращаем удаленный объект или None