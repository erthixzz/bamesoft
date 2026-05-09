from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.auth.deps import require_authenticated, require_engineer
from app.modules.maintenance import service
from app.modules.maintenance.schemas import (
    MaintenanceScheduleCreate,
    MaintenanceScheduleOut,
    MaintenanceScheduleUpdate,
)
from app.modules.users.models import User

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


@router.get("/due", response_model=list[MaintenanceScheduleOut])
async def list_due(
    on: date | None = None,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    return list(await service.list_due(db, on=on))


@router.get("/equipment/{equipment_id}", response_model=list[MaintenanceScheduleOut])
async def list_for_equipment(
    equipment_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    return list(await service.list_for_equipment(db, equipment_id))


@router.post("", response_model=MaintenanceScheduleOut, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    payload: MaintenanceScheduleCreate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_engineer),
):
    return await service.create(db, payload)


@router.patch("/{schedule_id}", response_model=MaintenanceScheduleOut)
async def update_schedule(
    schedule_id: uuid.UUID,
    payload: MaintenanceScheduleUpdate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_engineer),
):
    return await service.update(db, schedule_id, payload)


@router.post("/{schedule_id}/mark-done", response_model=MaintenanceScheduleOut)
async def mark_done(
    schedule_id: uuid.UUID,
    on: date | None = None,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_engineer),
):
    return await service.mark_done(db, schedule_id, on)
