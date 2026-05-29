"""Endpoints públicos (sin auth) para la ficha del equipo escaneada por QR."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy import nullslast, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import CaseStatus
from app.db.session import get_session
from app.modules.calibrations.models import Calibration
from app.modules.cases.models import Case
from app.modules.clinics.models import Clinic, Location
from app.modules.equipment import qr, service
from app.modules.equipment.models import EquipmentCategory
from app.modules.maintenance.models import MaintenanceSchedule
from app.modules.public.schemas import (
    PublicCalibrationBrief,
    PublicCaseBrief,
    PublicEquipmentOut,
    PublicMaintenanceBrief,
)

router = APIRouter(prefix="/public", tags=["public"])

_CLOSED_STATES = {CaseStatus.CLOSED, CaseStatus.CANCELLED}


@router.get("/equipment/{code}", response_model=PublicEquipmentOut)
async def public_equipment(
    code: str,
    token: str = Query(..., description="Token del QR"),
    db: AsyncSession = Depends(get_session),
) -> PublicEquipmentOut:
    """Ficha pública del equipo. El token del QR actúa como credencial."""
    eq = await service.get_by_qr(db, code, token)

    category_name: str | None = None
    if eq.category_id:
        cat = await db.get(EquipmentCategory, eq.category_id)
        category_name = cat.name if cat else None

    clinic = await db.get(Clinic, eq.clinic_id)
    location_name: str | None = None
    if eq.location_id:
        loc = await db.get(Location, eq.location_id)
        location_name = loc.name if loc else None

    cases = list(
        (
            await db.execute(
                select(Case)
                .where(Case.equipment_id == eq.id)
                .order_by(nullslast(Case.opened_at.desc()))
            )
        )
        .scalars()
        .all()
    )
    schedules = list(
        (
            await db.execute(
                select(MaintenanceSchedule)
                .where(MaintenanceSchedule.equipment_id == eq.id)
                .order_by(nullslast(MaintenanceSchedule.next_due_at.asc()))
            )
        )
        .scalars()
        .all()
    )
    calibrations = list(
        (
            await db.execute(
                select(Calibration)
                .where(Calibration.equipment_id == eq.id)
                .order_by(Calibration.performed_at.desc())
            )
        )
        .scalars()
        .all()
    )

    cases_open = sum(1 for c in cases if c.status not in _CLOSED_STATES)

    return PublicEquipmentOut(
        id=eq.id,
        code=eq.code,
        name=eq.name,
        brand=eq.brand,
        model=eq.model,
        serial_number=eq.serial_number,
        manufacturer=eq.manufacturer,
        status=str(eq.status),
        risk_class=str(eq.risk_class) if eq.risk_class else None,
        category_name=category_name,
        clinic_name=clinic.name if clinic else None,
        location_name=location_name,
        acquisition_date=eq.acquisition_date,
        warranty_until=eq.warranty_until,
        image_url=eq.image_url,
        notes=eq.notes,
        cases_open=cases_open,
        cases_total=len(cases),
        cases=[
            PublicCaseBrief(
                code=c.code,
                title=c.title,
                type=str(c.type),
                status=str(c.status),
                priority=str(c.priority),
                opened_at=c.opened_at,
                closed_at=c.closed_at,
            )
            for c in cases[:25]
        ],
        maintenance=[
            PublicMaintenanceBrief(
                name=m.name,
                frequency_days=m.frequency_days,
                last_done_at=m.last_done_at,
                next_due_at=m.next_due_at,
            )
            for m in schedules
        ],
        calibrations=[
            PublicCalibrationBrief(
                performed_at=cal.performed_at,
                expires_at=cal.expires_at,
                passed=cal.passed,
                standard=cal.standard,
            )
            for cal in calibrations[:25]
        ],
    )


@router.get(
    "/equipment/{code}/qr.png",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def public_equipment_qr(
    code: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_session),
) -> Response:
    """PNG del QR (codifica la URL pública). Sin auth: sirve para <img> e impresión."""
    eq = await service.get_by_qr(db, code, token)
    url = qr.build_url(eq.code, eq.qr_token)
    return Response(content=qr.render_png(url), media_type="image/png")
