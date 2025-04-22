# app/api/v1/endpoints/points.py
import uuid
from typing import List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas # Используем schemas
from app.api import deps

router = APIRouter()

# --- Эндпоинты для Точек ---

@router.post(
    "/",
    response_model=schemas.PointRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(deps.ensure_token_is_valid)]
)
async def create_point(
    *,
    db: AsyncSession = Depends(deps.get_db),
    point_in: schemas.PointCreate,
) -> Any:
    """Создать новую точку."""
    # Доп. проверки: существует ли company_id, server_id (если указан)?
    company = await crud.company.get(db, id=point_in.company_id)
    if not company:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Company {point_in.company_id} not found")
    if point_in.server_id:
        server = await crud.server.get(db, id=point_in.server_id)
        if not server:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Server {point_in.server_id} not found")

    point = await crud.point.create(db=db, obj_in=point_in)
    return point

@router.get(
    "/",
    response_model=List[schemas.PointRead],
    dependencies=[Depends(deps.ensure_token_is_valid)]
)
async def read_points(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    company_id: Optional[uuid.UUID] = Query(None, description="Filter by company ID"),
) -> Any:
    """Получить список точек (опционально фильтр по компании)."""
    if company_id:
        points = await crud.point.get_multi_by_company(db, company_id=company_id, skip=skip, limit=limit)
    else:
        points = await crud.point.get_multi(db, skip=skip, limit=limit)
    return points

@router.get(
    "/{point_id}",
    response_model=schemas.PointRead,
    dependencies=[Depends(deps.ensure_token_is_valid)]
)
async def read_point(
    *,
    db: AsyncSession = Depends(deps.get_db),
    point_id: uuid.UUID,
) -> Any:
    """Получить точку по ID."""
    point = await crud.point.get(db=db, id=point_id)
    if not point:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Point not found")
    return point

@router.put(
    "/{point_id}",
    response_model=schemas.PointRead,
    dependencies=[Depends(deps.ensure_token_is_valid)]
)
async def update_point(
    *,
    db: AsyncSession = Depends(deps.get_db),
    point_id: uuid.UUID,
    point_in: schemas.PointUpdate,
) -> Any:
    """Обновить точку по ID."""
    point = await crud.point.get(db=db, id=point_id)
    if not point:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Point not found")

    # Проверка server_id при обновлении
    if point_in.server_id and point_in.server_id != point.server_id:
         server = await crud.server.get(db, id=point_in.server_id)
         if not server:
             raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Server {point_in.server_id} not found")

    updated_point = await crud.point.update(db=db, db_obj=point, obj_in=point_in)
    return updated_point

@router.delete(
    "/{point_id}",
    response_model=schemas.PointRead,
    dependencies=[Depends(deps.ensure_token_is_valid)]
)
async def delete_point(
    *,
    db: AsyncSession = Depends(deps.get_db),
    point_id: uuid.UUID,
) -> Any:
    """Удалить точку по ID."""
    point = await crud.point.get(db=db, id=point_id)
    if not point:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Point not found")
    # Добавить проверку на связанные workstations/fiscal_registrars?
    deleted_point = await crud.point.remove(db=db, id=point_id)
    return deleted_point