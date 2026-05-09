from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.auth.deps import require_authenticated, require_engineer
from app.modules.calibrations import service
from app.modules.calibrations.schemas import CalibrationCreate, CalibrationOut
from app.modules.users.models import User

router = APIRouter(prefix="/calibrations", tags=["calibrations"])


@router.get("/equipment/{equipment_id}", response_model=list[CalibrationOut])
async def list_calibrations(
    equipment_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    return list(await service.list_for_equipment(db, equipment_id))


@router.post("", response_model=CalibrationOut, status_code=status.HTTP_201_CREATED)
async def create_calibration(
    payload: CalibrationCreate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_engineer),
):
    return await service.create(db, payload)
