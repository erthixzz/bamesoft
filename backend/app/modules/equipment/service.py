"""Lógica de equipos."""
from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import Conflict, NotFound
from app.db.enums import EquipmentStatus
from app.modules.equipment import qr
from app.modules.equipment.models import Equipment, EquipmentCategory
from app.modules.equipment.schemas import EquipmentCreate, EquipmentUpdate


async def list_equipment(
    db: AsyncSession,
    *,
    clinic_id: uuid.UUID | None = None,
    status: EquipmentStatus | None = None,
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> Sequence[Equipment]:
    stmt = select(Equipment).order_by(Equipment.created_at.desc())
    if clinic_id:
        stmt = stmt.where(Equipment.clinic_id == clinic_id)
    if status:
        stmt = stmt.where(Equipment.status == status)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                Equipment.code.ilike(like),
                Equipment.name.ilike(like),
                Equipment.serial_number.ilike(like),
                Equipment.brand.ilike(like),
                Equipment.model.ilike(like),
            )
        )
    stmt = stmt.limit(limit).offset(offset)
    return (await db.execute(stmt)).scalars().all()


async def get_equipment(db: AsyncSession, equipment_id: uuid.UUID) -> Equipment:
    obj = await db.get(Equipment, equipment_id)
    if obj is None:
        raise NotFound("Equipo")
    return obj


async def get_by_code(db: AsyncSession, code: str) -> Equipment | None:
    stmt = select(Equipment).where(Equipment.code == code)
    return (await db.execute(stmt)).scalar_one_or_none()


async def get_by_qr(db: AsyncSession, code: str, token: str) -> Equipment:
    stmt = select(Equipment).where(Equipment.code == code, Equipment.qr_token == token)
    obj = (await db.execute(stmt)).scalar_one_or_none()
    if obj is None:
        raise NotFound("Equipo (QR no coincide)")
    return obj


async def create_equipment(db: AsyncSession, payload: EquipmentCreate) -> Equipment:
    if await get_by_code(db, payload.code):
        raise Conflict("Ya existe un equipo con ese código")
    obj = Equipment(**payload.model_dump(), qr_token=qr.new_token())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


async def update_equipment(
    db: AsyncSession, equipment_id: uuid.UUID, payload: EquipmentUpdate
) -> Equipment:
    obj = await get_equipment(db, equipment_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.flush()
    await db.refresh(obj)
    return obj


async def regenerate_qr(db: AsyncSession, equipment_id: uuid.UUID) -> Equipment:
    obj = await get_equipment(db, equipment_id)
    obj.qr_token = qr.new_token()
    await db.flush()
    await db.refresh(obj)
    return obj


async def list_categories(db: AsyncSession) -> Sequence[EquipmentCategory]:
    return (
        (await db.execute(select(EquipmentCategory).order_by(EquipmentCategory.name)))
        .scalars()
        .all()
    )
