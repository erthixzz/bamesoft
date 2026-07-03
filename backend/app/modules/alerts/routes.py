from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.alerts import service
from app.modules.alerts.schemas import AlertCreate, AlertOut
from app.modules.auth.deps import (
    clinic_scope,
    require_authenticated,
    require_engineer,
    require_staff,
)
from app.modules.users.models import User

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
async def list_alerts(
    only_active: bool = True,
    limit: int = 100,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
):
    return list(
        await service.list_alerts(
            db, only_active=only_active, scope=clinic_scope(current), limit=limit
        )
    )


@router.post("", response_model=AlertOut, status_code=status.HTTP_201_CREATED)
async def create_alert(
    payload: AlertCreate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_staff),
):
    return await service.create(db, payload)


@router.post("/{alert_id}/ack", response_model=AlertOut)
async def acknowledge(
    alert_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_staff),
):
    return await service.acknowledge(db, alert_id, clinic_scope(current))


@router.post("/{alert_id}/resolve", response_model=AlertOut)
async def resolve(
    alert_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_staff),
):
    return await service.resolve(db, alert_id, clinic_scope(current))


@router.post("/sweep")
async def sweep(
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_engineer),
):
    """Genera alertas automáticas (mantenimientos y calibraciones)."""
    pm = await service.sweep_preventive(db)
    cal = await service.sweep_calibrations(db)
    return {"preventive": pm, "calibrations": cal}
