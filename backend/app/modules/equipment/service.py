"""Lógica de equipos."""
from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import Conflict, NotFound
from app.db.enums import EquipmentStatus
from app.modules.clinics.models import Clinic
from app.modules.equipment import qr
from app.modules.equipment.life_sheet_schemas import (
    ClinicHeader,
    LifeSheetData,
    LifeSheetOut,
    LifeSheetUpdate,
    SharedFields,
)
from app.modules.equipment.models import (
    Equipment,
    EquipmentCategory,
    EquipmentLifeSheet,
)
from app.modules.equipment.schemas import EquipmentCreate, EquipmentUpdate

# Campos requeridos en `equipment`: no se sobreescriben con None al sincronizar.
_SHARED_REQUIRED = {"name", "status"}


async def list_equipment(
    db: AsyncSession,
    *,
    clinic_id: uuid.UUID | None = None,
    sector_id: uuid.UUID | None = None,
    status: EquipmentStatus | None = None,
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> Sequence[Equipment]:
    stmt = select(Equipment).order_by(Equipment.created_at.desc())
    if clinic_id:
        stmt = stmt.where(Equipment.clinic_id == clinic_id)
    if sector_id:
        stmt = stmt.where(Equipment.sector_id == sector_id)
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


async def _life_sheet_row(
    db: AsyncSession, equipment_id: uuid.UUID
) -> EquipmentLifeSheet | None:
    stmt = select(EquipmentLifeSheet).where(
        EquipmentLifeSheet.equipment_id == equipment_id
    )
    return (await db.execute(stmt)).scalar_one_or_none()


def _shared_from_equipment(eq: Equipment) -> SharedFields:
    return SharedFields(
        name=eq.name,
        brand=eq.brand,
        model=eq.model,
        serial_number=eq.serial_number,
        manufacturer=eq.manufacturer,
        risk_class=eq.risk_class,
        status=eq.status,
        location_id=eq.location_id,
        acquisition_date=eq.acquisition_date,
        warranty_until=eq.warranty_until,
        image_url=eq.image_url,
        notes=eq.notes,
    )


async def _build_life_sheet_out(
    db: AsyncSession, eq: Equipment, row: EquipmentLifeSheet | None
) -> LifeSheetOut:
    clinic = await db.get(Clinic, eq.clinic_id)
    return LifeSheetOut(
        equipment_id=eq.id,
        code=eq.code,
        formato_codigo=row.formato_codigo if row else "MNT-FR-023",
        formato_fecha=row.formato_fecha if row else None,
        clinic=ClinicHeader.model_validate(clinic) if clinic else None,
        shared=_shared_from_equipment(eq),
        data=LifeSheetData.model_validate(row.data) if row else LifeSheetData(),
        created_at=row.created_at if row else None,
        updated_at=row.updated_at if row else None,
    )


async def get_life_sheet(db: AsyncSession, equipment_id: uuid.UUID) -> LifeSheetOut:
    """Devuelve la hoja de vida; si no existe aún, una estructura vacía."""
    eq = await get_equipment(db, equipment_id)
    row = await _life_sheet_row(db, equipment_id)
    return await _build_life_sheet_out(db, eq, row)


async def upsert_life_sheet(
    db: AsyncSession, equipment_id: uuid.UUID, payload: LifeSheetUpdate
) -> LifeSheetOut:
    """Crea o actualiza la hoja de vida y sincroniza los campos compartidos."""
    eq = await get_equipment(db, equipment_id)

    # Sincronizar campos compartidos hacia el equipo (sin nulear requeridos).
    for key, value in payload.shared.model_dump().items():
        if value is None and key in _SHARED_REQUIRED:
            continue
        setattr(eq, key, value)

    row = await _life_sheet_row(db, equipment_id)
    data = payload.data.model_dump(mode="json")
    if row is None:
        row = EquipmentLifeSheet(equipment_id=equipment_id, data=data)
        db.add(row)
    else:
        row.data = data
    if payload.formato_codigo is not None:
        row.formato_codigo = payload.formato_codigo
    if payload.formato_fecha is not None:
        row.formato_fecha = payload.formato_fecha

    await db.flush()
    await db.refresh(row)
    await db.refresh(eq)
    return await _build_life_sheet_out(db, eq, row)


async def list_categories(db: AsyncSession) -> Sequence[EquipmentCategory]:
    return (
        (await db.execute(select(EquipmentCategory).order_by(EquipmentCategory.name)))
        .scalars()
        .all()
    )
