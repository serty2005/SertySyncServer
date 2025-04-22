# app/api/v1/endpoints/workstations.py
import uuid
from typing import List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.WorkstationRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(deps.ensure_token_is_valid)])
async def create_workstation(*, db: AsyncSession = Depends(deps.get_db), workstation_in: schemas.WorkstationCreate) -> Any:
    """Создать новую рабочую станцию."""
    # Проверка существования point_id и server_id
    point = await crud.point.get(db, id=workstation_in.point_id)
    if not point:
         raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Point {workstation_in.point_id} not found")
    server = await crud.server.get(db, id=workstation_in.server_id)
    if not server:
         raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Server {workstation_in.server_id} not found")

    workstation = await crud.workstation.create(db=db, obj_in=workstation_in)
    return workstation

@router.get("/", response_model=List[schemas.WorkstationRead], dependencies=[Depends(deps.ensure_token_is_valid)])
async def read_workstations(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    point_id: Optional[uuid.UUID] = Query(None, description="Filter by point ID"),
) -> Any:
    """Получить список рабочих станций (опционально фильтр по точке)."""
    if point_id:
        workstations = await crud.workstation.get_multi_by_point(db, point_id=point_id, skip=skip, limit=limit)
    else:
        workstations = await crud.workstation.get_multi(db, skip=skip, limit=limit)
    return workstations

@router.get("/{workstation_id}", response_model=schemas.WorkstationRead, dependencies=[Depends(deps.ensure_token_is_valid)])
async def read_workstation(*, db: AsyncSession = Depends(deps.get_db), workstation_id: uuid.UUID) -> Any:
    """Получить рабочую станцию по ID."""
    workstation = await crud.workstation.get(db=db, id=workstation_id)
    if not workstation:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Workstation not found")
    return workstation

@router.put("/{workstation_id}", response_model=schemas.WorkstationRead, dependencies=[Depends(deps.ensure_token_is_valid)])
async def update_workstation(*, db: AsyncSession = Depends(deps.get_db), workstation_id: uuid.UUID, workstation_in: schemas.WorkstationUpdate) -> Any:
    """Обновить рабочую станцию по ID."""
    workstation = await crud.workstation.get(db=db, id=workstation_id)
    if not workstation:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Workstation not found")
    # Добавить проверки при смене point_id/server_id, если разрешено
    updated_workstation = await crud.workstation.update(db=db, db_obj=workstation, obj_in=workstation_in)
    return updated_workstation

@router.delete("/{workstation_id}", response_model=schemas.WorkstationRead, dependencies=[Depends(deps.ensure_token_is_valid)])
async def delete_workstation(*, db: AsyncSession = Depends(deps.get_db), workstation_id: uuid.UUID) -> Any:
    """Удалить рабочую станцию по ID."""
    workstation = await crud.workstation.get(db=db, id=workstation_id)
    if not workstation:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Workstation not found")
    # Добавить проверку на связанные fiscal_registrars?
    deleted_workstation = await crud.workstation.remove(db=db, id=workstation_id)
    return deleted_workstation