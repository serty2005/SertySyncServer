# app/api/v1/endpoints/fiscal_registrars.py
import uuid
from typing import List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.FiscalRegistrarRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(deps.ensure_token_is_valid)])
async def create_fiscal_registrar(*, db: AsyncSession = Depends(deps.get_db), fr_in: schemas.FiscalRegistrarCreate) -> Any:
    """Создать новый фискальный регистратор."""
    # Проверка существования workstation_id
    workstation = await crud.workstation.get(db, id=fr_in.workstation_id)
    if not workstation:
         raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Workstation {fr_in.workstation_id} not found")
    # Проверка уникальности serial_number
    existing_sn = await crud.fiscal_registrar.get_by_serial_number(db, serial_number=fr_in.serial_number)
    if existing_sn:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Fiscal registrar with serial number {fr_in.serial_number} already exists.")
    # Добавить проверки уникальности для registration_number, fiscal_drive_number?

    fr = await crud.fiscal_registrar.create(db=db, obj_in=fr_in)
    return fr

@router.get("/", response_model=List[schemas.FiscalRegistrarRead], dependencies=[Depends(deps.ensure_token_is_valid)])
async def read_fiscal_registrars(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    workstation_id: Optional[uuid.UUID] = Query(None, description="Filter by workstation ID"),
) -> Any:
    """Получить список ФР (опционально фильтр по рабочей станции)."""
    if workstation_id:
        frs = await crud.fiscal_registrar.get_multi_by_workstation(db, workstation_id=workstation_id, skip=skip, limit=limit)
    else:
        frs = await crud.fiscal_registrar.get_multi(db, skip=skip, limit=limit)
    return frs

@router.get("/{fr_id}", response_model=schemas.FiscalRegistrarRead, dependencies=[Depends(deps.ensure_token_is_valid)])
async def read_fiscal_registrar(*, db: AsyncSession = Depends(deps.get_db), fr_id: uuid.UUID) -> Any:
    """Получить ФР по ID."""
    fr = await crud.fiscal_registrar.get(db=db, id=fr_id)
    if not fr:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Fiscal registrar not found")
    return fr

@router.put("/{fr_id}", response_model=schemas.FiscalRegistrarRead, dependencies=[Depends(deps.ensure_token_is_valid)])
async def update_fiscal_registrar(*, db: AsyncSession = Depends(deps.get_db), fr_id: uuid.UUID, fr_in: schemas.FiscalRegistrarUpdate) -> Any:
    """Обновить ФР по ID."""
    fr = await crud.fiscal_registrar.get(db=db, id=fr_id)
    if not fr:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Fiscal registrar not found")
    # Добавить проверки уникальности при смене номеров?
    # Проверка workstation_id при смене
    if fr_in.workstation_id and fr_in.workstation_id != fr.workstation_id:
         workstation = await crud.workstation.get(db, id=fr_in.workstation_id)
         if not workstation:
              raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Workstation {fr_in.workstation_id} not found")

    updated_fr = await crud.fiscal_registrar.update(db=db, db_obj=fr, obj_in=fr_in)
    return updated_fr

@router.delete("/{fr_id}", response_model=schemas.FiscalRegistrarRead, dependencies=[Depends(deps.ensure_token_is_valid)])
async def delete_fiscal_registrar(*, db: AsyncSession = Depends(deps.get_db), fr_id: uuid.UUID) -> Any:
    """Удалить ФР по ID."""
    fr = await crud.fiscal_registrar.get(db=db, id=fr_id)
    if not fr:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Fiscal registrar not found")
    deleted_fr = await crud.fiscal_registrar.remove(db=db, id=fr_id)
    return deleted_fr