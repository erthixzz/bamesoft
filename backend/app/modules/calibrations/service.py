from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.calibrations.models import Calibration
from app.modules.calibrations.schemas import CalibrationCreate


async def list_for_equipment(
    db: AsyncSession, equipment_id: uuid.UUID
) -> Sequence[Calibration]:
    stmt = (
        select(Calibration)
        .where(Calibration.equipment_id == equipment_id)
        .order_by(Calibration.performed_at.desc())
    )
    return (await db.execute(stmt)).scalars().all()


async def create(db: AsyncSession, payload: CalibrationCreate) -> Calibration:
    obj = Calibration(**payload.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj
