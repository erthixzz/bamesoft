from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import Conflict
from app.modules.standards.models import EquipmentStandard, Standard
from app.modules.standards.schemas import StandardCreate


async def list_standards(db: AsyncSession) -> Sequence[Standard]:
    return (await db.execute(select(Standard).order_by(Standard.code))).scalars().all()


async def create(db: AsyncSession, payload: StandardCreate) -> Standard:
    existing = await db.execute(select(Standard).where(Standard.code == payload.code))
    if existing.scalar_one_or_none():
        raise Conflict("Ya existe una norma con ese código")
    obj = Standard(**payload.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


async def link_to_equipment(
    db: AsyncSession, equipment_id: uuid.UUID, standard_id: uuid.UUID
) -> EquipmentStandard:
    obj = EquipmentStandard(equipment_id=equipment_id, standard_id=standard_id)
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


async def list_for_equipment(
    db: AsyncSession, equipment_id: uuid.UUID
) -> Sequence[Standard]:
    stmt = (
        select(Standard)
        .join(EquipmentStandard, EquipmentStandard.standard_id == Standard.id)
        .where(EquipmentStandard.equipment_id == equipment_id)
        .order_by(Standard.code)
    )
    return (await db.execute(stmt)).scalars().all()
