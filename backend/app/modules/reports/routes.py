from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.auth.deps import clinic_scope, require_authenticated
from app.modules.reports import service
from app.modules.reports.schemas import (
    ComplianceReport,
    DashboardKPIs,
    EquipmentReport,
    OperationsReport,
    ProductivityReport,
    ServicesReport,
)
from app.modules.users.models import User

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/dashboard", response_model=DashboardKPIs)
async def dashboard(
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
):
    return await service.dashboard(db, clinic_scope(current))


@router.get("/compliance", response_model=ComplianceReport)
async def compliance(
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
):
    return await service.compliance(db, clinic_scope(current))


@router.get("/productivity", response_model=ProductivityReport)
async def productivity(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
):
    return await service.productivity(db, date_from, date_to, clinic_scope(current))


@router.get("/operations", response_model=OperationsReport)
async def operations(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
):
    return await service.operations(db, date_from, date_to, clinic_scope(current))


@router.get("/equipment", response_model=EquipmentReport)
async def equipment_report(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
):
    """Servicio agregado por equipo (casos, completitud y tiempos promedio)."""
    return await service.equipment_report(db, date_from, date_to, clinic_scope(current))


@router.get("/services", response_model=ServicesReport)
async def services_report(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    engineer_id: uuid.UUID | None = Query(default=None),
    equipment_id: uuid.UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
):
    """Detalle servicio a servicio: qué se hizo, quién y cuánto se demoró."""
    return await service.services_report(
        db, date_from, date_to, clinic_scope(current), engineer_id, equipment_id
    )
