"""Reportes / KPIs."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import CaseStatus, EquipmentStatus
from app.modules.calibrations.models import Calibration
from app.modules.cases.models import Case
from app.modules.equipment.models import Equipment
from app.modules.maintenance.models import MaintenanceSchedule
from app.modules.reports.schemas import ComplianceItem, ComplianceReport, DashboardKPIs
from app.modules.standards.models import EquipmentStandard, Standard


async def dashboard(db: AsyncSession) -> DashboardKPIs:
    now = datetime.now(UTC)
    horizon = now + timedelta(days=30)
    last_30 = now - timedelta(days=30)

    eq_total = await db.scalar(select(func.count(Equipment.id)))
    eq_op = await db.scalar(
        select(func.count(Equipment.id)).where(Equipment.status == EquipmentStatus.OPERATIONAL)
    )
    eq_oos = await db.scalar(
        select(func.count(Equipment.id)).where(
            Equipment.status == EquipmentStatus.OUT_OF_SERVICE
        )
    )

    cases_open = await db.scalar(
        select(func.count(Case.id)).where(Case.status == CaseStatus.OPEN)
    )
    cases_ip = await db.scalar(
        select(func.count(Case.id)).where(Case.status == CaseStatus.IN_PROGRESS)
    )
    cases_closed_30 = await db.scalar(
        select(func.count(Case.id)).where(
            Case.status == CaseStatus.CLOSED, Case.closed_at >= last_30
        )
    )

    pm_due = await db.scalar(
        select(func.count(MaintenanceSchedule.id)).where(
            MaintenanceSchedule.next_due_at.is_not(None),
            MaintenanceSchedule.next_due_at <= horizon.date(),
        )
    )
    cal_due = await db.scalar(
        select(func.count(Calibration.id)).where(
            Calibration.expires_at.is_not(None),
            Calibration.expires_at <= horizon.date(),
        )
    )

    avg_close_seconds = await db.scalar(
        select(
            func.avg(
                func.extract("epoch", Case.closed_at - Case.opened_at)
            )
        ).where(Case.closed_at.is_not(None), Case.opened_at.is_not(None))
    )
    avg_hours = (avg_close_seconds / 3600.0) if avg_close_seconds else None

    return DashboardKPIs(
        equipment_total=eq_total or 0,
        equipment_operational=eq_op or 0,
        equipment_out_of_service=eq_oos or 0,
        cases_open=cases_open or 0,
        cases_in_progress=cases_ip or 0,
        cases_closed_30d=cases_closed_30 or 0,
        preventive_due_30d=pm_due or 0,
        calibrations_due_30d=cal_due or 0,
        avg_close_time_hours=avg_hours,
    )


async def compliance(db: AsyncSession) -> ComplianceReport:
    total_eq = await db.scalar(select(func.count(Equipment.id))) or 0
    rows = (
        await db.execute(
            select(
                Standard.code,
                Standard.name,
                func.count(distinct(EquipmentStandard.equipment_id)).label("with_eq"),
            )
            .join(EquipmentStandard, EquipmentStandard.standard_id == Standard.id, isouter=True)
            .group_by(Standard.id)
            .order_by(Standard.code)
        )
    ).all()

    items = [
        ComplianceItem(
            standard_code=r.code,
            standard_name=r.name,
            coverage_pct=(r.with_eq / total_eq * 100.0) if total_eq else 0.0,
            equipment_with=r.with_eq or 0,
            equipment_total=total_eq,
        )
        for r in rows
    ]
    return ComplianceReport(items=items, total=len(items))
