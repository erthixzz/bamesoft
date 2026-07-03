"""Lógica de clínicas y ubicaciones."""
from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFound
from app.modules.clinics.models import Clinic, Location
from app.modules.clinics.schemas import (
    ClinicCreate,
    ClinicUpdate,
    LocationCreate,
    LocationUpdate,
)


# Clinics ----------------------------------------------------------------
async def list_clinics(db: AsyncSession, scope: uuid.UUID | None = None) -> Sequence[Clinic]:
    stmt = select(Clinic).order_by(Clinic.name)
    if scope is not None:
        stmt = stmt.where(Clinic.id == scope)  # el admin de clínica solo ve la suya
    return (await db.execute(stmt)).scalars().all()


async def get_clinic(
    db: AsyncSession, clinic_id: uuid.UUID, scope: uuid.UUID | None = None
) -> Clinic:
    obj = await db.get(Clinic, clinic_id)
    if obj is None or (scope is not None and obj.id != scope):
        raise NotFound("Clínica")
    return obj


async def create_clinic(db: AsyncSession, payload: ClinicCreate) -> Clinic:
    obj = Clinic(**payload.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


async def update_clinic(db: AsyncSession, clinic_id: uuid.UUID, payload: ClinicUpdate) -> Clinic:
    obj = await get_clinic(db, clinic_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.flush()
    await db.refresh(obj)
    return obj


# Locations --------------------------------------------------------------
async def list_locations(db: AsyncSession, clinic_id: uuid.UUID) -> Sequence[Location]:
    stmt = select(Location).where(Location.clinic_id == clinic_id).order_by(Location.code)
    return (await db.execute(stmt)).scalars().all()


async def create_location(db: AsyncSession, payload: LocationCreate) -> Location:
    obj = Location(**payload.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


async def update_location(db: AsyncSession, loc_id: uuid.UUID, payload: LocationUpdate) -> Location:
    obj = await db.get(Location, loc_id)
    if obj is None:
        raise NotFound("Ubicación")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.flush()
    await db.refresh(obj)
    return obj
