# app/api/v1/endpoints/companies.py
import uuid
from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api import deps # Импортируем зависимости (сессия БД, проверка токена)

router = APIRouter()

@router.post(
    "/",
    response_model=schemas.CompanyRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(deps.ensure_token_is_valid)] # Требуем валидный токен
)
async def create_company(
    *,
    db: AsyncSession = Depends(deps.get_db),
    company_in: schemas.CompanyCreate,
    # current_user: models.User = Depends(deps.get_current_active_user) # Если нужна информация о пользователе
) -> Any:
    """
    Создать новую компанию. Требуется аутентификация.
    """
    # Проверка на уникальность ИНН перед созданием
    existing_billing = await crud.company.get_by_inn(db, inn=company_in.billing_inn)
    if existing_billing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company with billing INN {company_in.billing_inn} already exists.",
        )
    existing_iiko = await crud.company.get_by_inn(db, inn=company_in.iiko_inn)
    if existing_iiko and existing_iiko.iiko_inn == company_in.iiko_inn:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company with iiko INN {company_in.iiko_inn} already exists.",
        )

    company = await crud.company.create(db=db, obj_in=company_in)
    return company

@router.get(
    "/",
    response_model=List[schemas.CompanyRead],
    dependencies=[Depends(deps.ensure_token_is_valid)] # Требуем валидный токен
)
async def read_companies(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return"),
    # Можно добавить параметры для фильтрации/поиска
) -> Any:
    """
    Получить список компаний с пагинацией. Требуется аутентификация.
    """
    companies = await crud.company.get_multi(db, skip=skip, limit=limit)
    # Можно добавить подсчет общего количества для заголовков пагинации, если нужно
    # total_count = await crud.company.get_count(db)
    return companies

@router.get(
    "/{company_id}",
    response_model=schemas.CompanyRead,
    dependencies=[Depends(deps.ensure_token_is_valid)] # Требуем валидный токен
)
async def read_company(
    *,
    db: AsyncSession = Depends(deps.get_db),
    company_id: uuid.UUID,
) -> Any:
    """
    Получить компанию по ID. Требуется аутентификация.
    """
    company = await crud.company.get(db=db, id=company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )
    return company

@router.put(
    "/{company_id}",
    response_model=schemas.CompanyRead,
    dependencies=[Depends(deps.ensure_token_is_valid)] # Требуем валидный токен
)
async def update_company(
    *,
    db: AsyncSession = Depends(deps.get_db),
    company_id: uuid.UUID,
    company_in: schemas.CompanyUpdate,
) -> Any:
    """
    Обновить компанию по ID. Требуется аутентификация.
    Обновляет только переданные поля. Инкрементирует ревизию.
    """
    company = await crud.company.get(db=db, id=company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    # Проверка на уникальность ИНН при обновлении (если ИНН меняется)
    if company_in.billing_inn and company_in.billing_inn != company.billing_inn:
        existing = await crud.company.get_by_inn(db, inn=company_in.billing_inn)
        if existing and existing.id != company_id:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Company with billing INN {company_in.billing_inn} already exists.",
            )
    if company_in.iiko_inn and company_in.iiko_inn != company.iiko_inn:
        existing = await crud.company.get_by_inn(db, inn=company_in.iiko_inn)
        # Проверяем именно iiko_inn, т.к. get_by_inn ищет по обоим
        if existing and existing.id != company_id and existing.iiko_inn == company_in.iiko_inn:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Company with iiko INN {company_in.iiko_inn} already exists.",
            )

    updated_company = await crud.company.update(db=db, db_obj=company, obj_in=company_in)
    return updated_company

@router.delete(
    "/{company_id}",
    response_model=schemas.CompanyRead, # Возвращаем удаленный объект
    dependencies=[Depends(deps.ensure_token_is_valid)] # Требуем валидный токен
)
async def delete_company(
    *,
    db: AsyncSession = Depends(deps.get_db),
    company_id: uuid.UUID,
) -> Any:
    """
    Удалить компанию по ID. Требуется аутентификация.
    """
    company = await crud.company.get(db=db, id=company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )
    # Добавить проверку на связанные объекты (точки), если нужно запретить удаление
    # if company.points: # Загрузка связей может потребовать доп. настройки или запроса
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Cannot delete company with associated points.",
    #     )

    deleted_company = await crud.company.remove(db=db, id=company_id)
    # Возвращаем удаленный объект для подтверждения
    return deleted_company