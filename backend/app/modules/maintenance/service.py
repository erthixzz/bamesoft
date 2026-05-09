from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFound
from app.modules.maintenance.models import MaintenanceSchedule
from app.modules.maintenance.schemas import (
    MaintenanceScheduleCreate,
    MaintenanceScheduleUpdate,
)


async def list_for_equipment(
    db: AsyncSession, equipment_id: uuid.UUID
) -> Sequence[MaintenanceSchedule]:
    stmt = select(MaintenanceSchedule).where(
        MaintenanceSchedule.equipment_id == equipment_id
    )
    return (await db.execute(stmt)).scalars().all()


async def list_due(
    db: AsyncSession, *, on: date | None = None
) -> Sequence[MaintenanceSchedule]:
    """Mantenimientos vencidos o por vencer al día indicado (default: hoy)."""
    on = on or date.today()
    stmt = (
        select(MaintenanceSchedule)
        .where(MaintenanceSchedule.next_due_at.is_not(None))
        .where(MaintenanceSchedule.next_due_at <= on)
        .order_by(MaintenanceSchedule.next_due_at)
    )
    return (await db.execute(stmt)).scalars().all()


async def create(
    db: AsyncSession, payload: MaintenanceScheduleCreate
) -> MaintenanceSchedule:
    data = payload.model_dump()
    if data.get("last_done_at") and not data.get("next_due_at"):
        data["next_due_at"] = data["last_done_at"] + timedelta(days=data["frequency_days"])
    obj = MaintenanceSchedule(**data)
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


async def update(
    db: AsyncSession, schedule_id: uuid.UUID, payload: MaintenanceScheduleUpdate
) -> MaintenanceSchedule:
    obj = await db.get(MaintenanceSchedule, schedule_id)
    if obj is None:
        raise NotFound("Cronograma de mantenimiento")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)
    if "last_done_at" in data and obj.last_done_at:
        obj.next_due_at = obj.last_done_at + timedelta(days=obj.frequency_days)
    await db.flush()
    await db.refresh(obj)
    return obj


async def mark_done(
    db: AsyncSession, schedule_id: uuid.UUID, on: date | None = None
) -> MaintenanceSchedule:
    obj = await db.get(MaintenanceSchedule, schedule_id)
    if obj is None:
        raise NotFound("Cronograma de mantenimiento")
    obj.last_done_at = on or date.today()
    obj.next_due_at = obj.last_done_at + timedelta(days=obj.frequency_days)
    await db.flush()
    await db.refresh(obj)
    return obj
