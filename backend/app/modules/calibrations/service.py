from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFound
from app.modules.calibrations.models import Calibration
from app.modules.calibrations.schemas import CalibrationCreate
from app.modules.equipment.models import Equipment


async def _equipment_visible(
    db: AsyncSession, equipment_id: uuid.UUID, scope: uuid.UUID | None
) -> bool:
    """El equipo existe y (si hay scope) pertenece a la clínica del usuario."""
    stmt = select(Equipment.id).where(Equipment.id == equipment_id)
    if scope is not None:
        stmt = stmt.where(Equipment.clinic_id == scope)
    return (await db.execute(stmt)).scalar_one_or_none() is not None


async def list_for_equipment(
    db: AsyncSession, equipment_id: uuid.UUID, scope: uuid.UUID | None = None
) -> Sequence[Calibration]:
    if not await _equipment_visible(db, equipment_id, scope):
        raise NotFound("Equipo")  # no revelar existencia fuera de la clínica
    stmt = (
        select(Calibration)
        .where(Calibration.equipment_id == equipment_id)
        .order_by(Calibration.performed_at.desc())
    )
    return (await db.execute(stmt)).scalars().all()


async def create(
    db: AsyncSession, payload: CalibrationCreate, scope: uuid.UUID | None = None
) -> Calibration:
    if not await _equipment_visible(db, payload.equipment_id, scope):
        raise NotFound("Equipo")
    # `certificate_path` no viaja en CalibrationCreate (extra="forbid"): se
    # rellena al subir el certificado por /documents.
    obj = Calibration(**payload.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj
