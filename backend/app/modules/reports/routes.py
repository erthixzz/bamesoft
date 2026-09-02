from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import SATISFACTION_MAX, SATISFACTION_MIN, TecnovigilanciaStage
from app.db.session import get_session
from app.modules.auth.deps import clinic_scope, require_authenticated
from app.modules.reports import service
from app.modules.reports.schemas import (
    BreakdownReport,
    ComplianceReport,
    DashboardKPIs,
    EquipmentReport,
    OperationsReport,
    ProductivityReport,
    ServicesReport,
    TecnovigilanciaReport,
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
    satisfaction_min: int | None = Query(default=None, ge=SATISFACTION_MIN, le=SATISFACTION_MAX),
    satisfaction_max: int | None = Query(default=None, ge=SATISFACTION_MIN, le=SATISFACTION_MAX),
    tecnovigilancia: bool | None = Query(default=None),
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
):
    """Detalle servicio a servicio: qué se hizo, quién y cuánto se demoró."""
    return await service.services_report(
        db,
        date_from,
        date_to,
        clinic_scope(current),
        engineer_id,
        equipment_id,
        satisfaction_min,
        satisfaction_max,
        tecnovigilancia,
    )


@router.get("/tecnovigilancia", response_model=TecnovigilanciaReport)
async def tecnovigilancia_report(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    stage: TecnovigilanciaStage | None = Query(default=None),
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
):
    """Casos de tecnovigilancia del rango, con su distribución por etapa."""
    return await service.tecnovigilancia_report(
        db, date_from, date_to, clinic_scope(current), stage
    )


@router.get("/breakdown", response_model=BreakdownReport)
async def breakdown(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
):
    """Distribuciones para gráficas (estado, tipo, prioridad, unidad, mes)."""
    return await service.breakdown(db, date_from, date_to, clinic_scope(current))
