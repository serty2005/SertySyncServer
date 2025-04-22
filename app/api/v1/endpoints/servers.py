# app/api/v1/endpoints/servers.py
import uuid
from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.ServerRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(deps.ensure_token_is_valid)])
async def create_server(*, db: AsyncSession = Depends(deps.get_db), server_in: schemas.ServerCreate) -> Any:
    """Создать новый сервер."""
    existing = await crud.server.get_by_iiko_uid(db, iiko_uid=server_in.iiko_uid)
    if existing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Server with iiko_uid {server_in.iiko_uid} already exists.")
    server = await crud.server.create(db=db, obj_in=server_in)
    return server

@router.get("/", response_model=List[schemas.ServerRead], dependencies=[Depends(deps.ensure_token_is_valid)])
async def read_servers(db: AsyncSession = Depends(deps.get_db), skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=200)) -> Any:
    """Получить список серверов."""
    servers = await crud.server.get_multi(db, skip=skip, limit=limit)
    return servers

@router.get("/{server_id}", response_model=schemas.ServerRead, dependencies=[Depends(deps.ensure_token_is_valid)])
async def read_server(*, db: AsyncSession = Depends(deps.get_db), server_id: uuid.UUID) -> Any:
    """Получить сервер по ID."""
    server = await crud.server.get(db=db, id=server_id)
    if not server:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Server not found")
    return server

@router.put("/{server_id}", response_model=schemas.ServerRead, dependencies=[Depends(deps.ensure_token_is_valid)])
async def update_server(*, db: AsyncSession = Depends(deps.get_db), server_id: uuid.UUID, server_in: schemas.ServerUpdate) -> Any:
    """Обновить сервер по ID."""
    server = await crud.server.get(db=db, id=server_id)
    if not server:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Server not found")
    # Проверка уникальности iiko_uid при смене (если разрешено)
    # if server_in.iiko_uid and server_in.iiko_uid != server.iiko_uid:
    #     existing = await crud.server.get_by_iiko_uid(db, iiko_uid=server_in.iiko_uid)
    #     if existing and existing.id != server_id:
    #         raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Server with iiko_uid {server_in.iiko_uid} already exists.")
    updated_server = await crud.server.update(db=db, db_obj=server, obj_in=server_in)
    return updated_server

@router.delete("/{server_id}", response_model=schemas.ServerRead, dependencies=[Depends(deps.ensure_token_is_valid)])
async def delete_server(*, db: AsyncSession = Depends(deps.get_db), server_id: uuid.UUID) -> Any:
    """Удалить сервер по ID."""
    server = await crud.server.get(db=db, id=server_id)
    if not server:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Server not found")
    # Добавить проверку на связанные points/workstations?
    deleted_server = await crud.server.remove(db=db, id=server_id)
    return deleted_server