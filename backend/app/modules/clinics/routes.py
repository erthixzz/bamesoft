"""Endpoints de clínicas y ubicaciones."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.auth.deps import require_admin, require_authenticated
from app.modules.clinics import service
from app.modules.clinics.schemas import (
    ClinicCreate,
    ClinicOut,
    ClinicUpdate,
    LocationCreate,
    LocationOut,
    LocationUpdate,
)
from app.modules.users.models import User

router = APIRouter(prefix="/clinics", tags=["clinics"])


@router.get("", response_model=list[ClinicOut])
async def list_clinics(
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    return list(await service.list_clinics(db))


@router.post("", response_model=ClinicOut, status_code=status.HTTP_201_CREATED)
async def create_clinic(
    payload: ClinicCreate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),
):
    return await service.create_clinic(db, payload)


@router.get("/{clinic_id}", response_model=ClinicOut)
async def get_clinic(
    clinic_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    return await service.get_clinic(db, clinic_id)


@router.patch("/{clinic_id}", response_model=ClinicOut)
async def update_clinic(
    clinic_id: uuid.UUID,
    payload: ClinicUpdate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),
):
    return await service.update_clinic(db, clinic_id, payload)


# Locations -------------------------------------------------------------
@router.get("/{clinic_id}/locations", response_model=list[LocationOut])
async def list_locations(
    clinic_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    return list(await service.list_locations(db, clinic_id))


@router.post(
    "/{clinic_id}/locations",
    response_model=LocationOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_location(
    clinic_id: uuid.UUID,
    payload: LocationCreate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),
):
    payload = payload.model_copy(update={"clinic_id": clinic_id})
    return await service.create_location(db, payload)


@router.patch("/locations/{location_id}", response_model=LocationOut)
async def update_location(
    location_id: uuid.UUID,
    payload: LocationUpdate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),
):
    return await service.update_location(db, location_id, payload)
