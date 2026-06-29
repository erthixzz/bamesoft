"""Endpoints de equipos."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import EquipmentStatus
from app.db.session import get_session
from app.modules.auth.deps import require_authenticated, require_engineer
from app.modules.equipment import qr, service
from app.modules.equipment.life_sheet_schemas import LifeSheetOut, LifeSheetUpdate
from app.modules.equipment.schemas import (
    EquipmentCategoryOut,
    EquipmentCreate,
    EquipmentOut,
    EquipmentUpdate,
)
from app.modules.users.models import User

router = APIRouter(prefix="/equipment", tags=["equipment"])


@router.get("", response_model=list[EquipmentOut])
async def list_equipment(
    clinic_id: uuid.UUID | None = None,
    sector_id: uuid.UUID | None = None,
    status_: EquipmentStatus | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None, description="Búsqueda libre"),
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    return list(
        await service.list_equipment(
            db,
            clinic_id=clinic_id,
            sector_id=sector_id,
            status=status_,
            q=q,
            limit=limit,
            offset=offset,
        )
    )


@router.post("", response_model=EquipmentOut, status_code=status.HTTP_201_CREATED)
async def create_equipment(
    payload: EquipmentCreate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_engineer),
):
    return await service.create_equipment(db, payload)


@router.get("/categories", response_model=list[EquipmentCategoryOut])
async def list_categories(
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    return list(await service.list_categories(db))


@router.get("/by-code/{code}", response_model=EquipmentOut)
async def get_by_code(
    code: str,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    obj = await service.get_by_code(db, code)
    if obj is None:
        from app.core.errors import NotFound

        raise NotFound("Equipo")
    return obj


@router.get("/scan", response_model=EquipmentOut)
async def scan_qr(
    code: str = Query(...),
    token: str = Query(...),
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    """Resolver un equipo a partir de los datos leídos del QR."""
    return await service.get_by_qr(db, code, token)


@router.get("/{equipment_id}", response_model=EquipmentOut)
async def get_equipment(
    equipment_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    return await service.get_equipment(db, equipment_id)


@router.patch("/{equipment_id}", response_model=EquipmentOut)
async def update_equipment(
    equipment_id: uuid.UUID,
    payload: EquipmentUpdate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_engineer),
):
    return await service.update_equipment(db, equipment_id, payload)


@router.post("/{equipment_id}/regenerate-qr", response_model=EquipmentOut)
async def regenerate_qr_token(
    equipment_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_engineer),
):
    return await service.regenerate_qr(db, equipment_id)


@router.get("/{equipment_id}/life-sheet", response_model=LifeSheetOut)
async def get_life_sheet(
    equipment_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    """Hoja de vida del equipo (consulta). Si no existe, devuelve vacía."""
    return await service.get_life_sheet(db, equipment_id)


@router.put("/{equipment_id}/life-sheet", response_model=LifeSheetOut)
async def save_life_sheet(
    equipment_id: uuid.UUID,
    payload: LifeSheetUpdate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_engineer),
):
    """Crea/actualiza la hoja de vida y sincroniza los campos del equipo."""
    return await service.upsert_life_sheet(db, equipment_id, payload)


@router.get(
    "/{equipment_id}/qr.png",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def qr_png(
    equipment_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    obj = await service.get_equipment(db, equipment_id)
    url = qr.build_url(obj.code, obj.qr_token)
    return Response(content=qr.render_png(url), media_type="image/png")
