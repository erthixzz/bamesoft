from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.auth.deps import require_admin, require_authenticated
from app.modules.standards import service
from app.modules.standards.schemas import EquipmentStandardLink, StandardCreate, StandardOut
from app.modules.users.models import User

router = APIRouter(prefix="/standards", tags=["standards"])


@router.get("", response_model=list[StandardOut])
async def list_standards(
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    return list(await service.list_standards(db))


@router.post("", response_model=StandardOut, status_code=status.HTTP_201_CREATED)
async def create_standard(
    payload: StandardCreate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),
):
    return await service.create(db, payload)


@router.post("/link", status_code=status.HTTP_201_CREATED)
async def link_standard(
    payload: EquipmentStandardLink,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),
):
    obj = await service.link_to_equipment(db, payload.equipment_id, payload.standard_id)
    return {"id": str(obj.id)}


@router.get("/equipment/{equipment_id}", response_model=list[StandardOut])
async def list_for_equipment(
    equipment_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    return list(await service.list_for_equipment(db, equipment_id))
