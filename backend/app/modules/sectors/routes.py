from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.auth.deps import require_authenticated, require_engineer
from app.modules.sectors import service
from app.modules.sectors.schemas import SectorCreate, SectorOut, SectorUpdate
from app.modules.users.models import User

router = APIRouter(prefix="/sectors", tags=["sectors"])


@router.get("", response_model=list[SectorOut])
async def list_sectors(
    clinic_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    return list(await service.list_sectors(db, clinic_id))


@router.get("/{sector_id}", response_model=SectorOut)
async def get_sector(
    sector_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    return await service.get_sector(db, sector_id)


@router.post("", response_model=SectorOut, status_code=status.HTTP_201_CREATED)
async def create_sector(
    payload: SectorCreate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_engineer),
):
    return await service.create(db, payload)


@router.patch("/{sector_id}", response_model=SectorOut)
async def update_sector(
    sector_id: uuid.UUID,
    payload: SectorUpdate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_engineer),
):
    return await service.update(db, sector_id, payload)
