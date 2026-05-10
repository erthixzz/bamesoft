from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFound
from app.modules.sectors.models import Sector
from app.modules.sectors.schemas import SectorCreate, SectorUpdate


async def list_sectors(
    db: AsyncSession, clinic_id: uuid.UUID | None = None
) -> Sequence[Sector]:
    stmt = select(Sector).order_by(Sector.code)
    if clinic_id:
        stmt = stmt.where(Sector.clinic_id == clinic_id)
    return (await db.execute(stmt)).scalars().all()


async def get_sector(db: AsyncSession, sector_id: uuid.UUID) -> Sector:
    obj = await db.get(Sector, sector_id)
    if obj is None:
        raise NotFound("Sector")
    return obj


async def create(db: AsyncSession, payload: SectorCreate) -> Sector:
    obj = Sector(**payload.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


async def update(
    db: AsyncSession, sector_id: uuid.UUID, payload: SectorUpdate
) -> Sector:
    obj = await get_sector(db, sector_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.flush()
    await db.refresh(obj)
    return obj
