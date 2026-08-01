from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFound
from app.modules.equipment.models import Equipment
from app.modules.maintenance.models import MaintenanceSchedule
from app.modules.maintenance.schemas import (
    MaintenanceScheduleCreate,
    MaintenanceScheduleUpdate,
)

_NOT_FOUND = "Cronograma de mantenimiento"


async def _equipment_visible(
    db: AsyncSession, equipment_id: uuid.UUID, scope: uuid.UUID | None
) -> bool:
    """El equipo existe y (si hay scope) pertenece a la clínica del usuario."""
    stmt = select(Equipment.id).where(Equipment.id == equipment_id)
    if scope is not None:
        stmt = stmt.where(Equipment.clinic_id == scope)
    return (await db.execute(stmt)).scalar_one_or_none() is not None


async def _get_in_scope(
    db: AsyncSession, schedule_id: uuid.UUID, scope: uuid.UUID | None
) -> MaintenanceSchedule:
    """Cronograma dentro del alcance del usuario, o 404 (no revela existencia)."""
    obj = await db.get(MaintenanceSchedule, schedule_id)
    if obj is None or not await _equipment_visible(db, obj.equipment_id, scope):
        raise NotFound(_NOT_FOUND)
    return obj


async def list_for_equipment(
    db: AsyncSession, equipment_id: uuid.UUID, scope: uuid.UUID | None = None
) -> Sequence[MaintenanceSchedule]:
    if not await _equipment_visible(db, equipment_id, scope):
        raise NotFound("Equipo")
    stmt = select(MaintenanceSchedule).where(
        MaintenanceSchedule.equipment_id == equipment_id
    )
    return (await db.execute(stmt)).scalars().all()


async def list_due(
    db: AsyncSession, *, on: date | None = None, scope: uuid.UUID | None = None
) -> Sequence[MaintenanceSchedule]:
    """Mantenimientos vencidos o por vencer al día indicado (default: hoy)."""
    on = on or date.today()
    stmt = (
        select(MaintenanceSchedule)
        .where(MaintenanceSchedule.next_due_at.is_not(None))
        .where(MaintenanceSchedule.next_due_at <= on)
        .order_by(MaintenanceSchedule.next_due_at)
    )
    if scope is not None:
        # Join al equipo: el cronograma hereda la clínica de su equipo.
        stmt = stmt.join(Equipment, Equipment.id == MaintenanceSchedule.equipment_id).where(
            Equipment.clinic_id == scope
        )
    return (await db.execute(stmt)).scalars().all()


async def create(
    db: AsyncSession, payload: MaintenanceScheduleCreate, scope: uuid.UUID | None = None
) -> MaintenanceSchedule:
    if not await _equipment_visible(db, payload.equipment_id, scope):
        raise NotFound("Equipo")
    data = payload.model_dump()
    if data.get("last_done_at") and not data.get("next_due_at"):
        data["next_due_at"] = data["last_done_at"] + timedelta(days=data["frequency_days"])
    obj = MaintenanceSchedule(**data)
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


async def update(
    db: AsyncSession,
    schedule_id: uuid.UUID,
    payload: MaintenanceScheduleUpdate,
    scope: uuid.UUID | None = None,
) -> MaintenanceSchedule:
    obj = await _get_in_scope(db, schedule_id, scope)
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)
    if "last_done_at" in data and obj.last_done_at:
        obj.next_due_at = obj.last_done_at + timedelta(days=obj.frequency_days)
    await db.flush()
    await db.refresh(obj)
    return obj


async def mark_done(
    db: AsyncSession,
    schedule_id: uuid.UUID,
    on: date | None = None,
    scope: uuid.UUID | None = None,
) -> MaintenanceSchedule:
    obj = await _get_in_scope(db, schedule_id, scope)
    obj.last_done_at = on or date.today()
    obj.next_due_at = obj.last_done_at + timedelta(days=obj.frequency_days)
    await db.flush()
    await db.refresh(obj)
    return obj
