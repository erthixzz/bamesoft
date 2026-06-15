"""Reportes / KPIs."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import distinct, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import CaseStatus
from app.modules.cases.models import Case
from app.modules.equipment.models import Equipment
from app.modules.reports.schemas import ComplianceItem, ComplianceReport, DashboardKPIs
from app.modules.standards.models import EquipmentStandard, Standard


# Una sola query SQL que devuelve todos los KPIs en columnas paralelas:
# convertimos 9 roundtrips a Postgres en 1 solo viaje (~150 ms vs ~1.4 s).
_DASHBOARD_SQL = text(
    """
    select
      (select count(*) from equipment) as eq_total,
      (select count(*) from equipment where status = 'operational') as eq_op,
      (select count(*) from equipment where status = 'out_of_service') as eq_oos,
      (select count(*) from cases where status = 'open') as cases_open,
      (select count(*) from cases where status = 'in_progress') as cases_ip,
      (select count(*) from cases
        where status = 'closed' and closed_at >= :last_30) as cases_closed_30,
      (select count(*) from maintenance_schedules
        where next_due_at is not null and next_due_at <= :horizon) as pm_due,
      (select count(*) from calibrations
        where expires_at is not null and expires_at <= :horizon) as cal_due,
      (select avg(extract(epoch from closed_at - opened_at)) from cases
        where closed_at is not null and opened_at is not null) as avg_close_seconds
    """
)


async def dashboard(db: AsyncSession) -> DashboardKPIs:
    now = datetime.now(UTC)
    horizon = (now + timedelta(days=30)).date()
    last_30 = now - timedelta(days=30)

    row = (
        await db.execute(_DASHBOARD_SQL, {"horizon": horizon, "last_30": last_30})
    ).one()

    avg_seconds = row.avg_close_seconds
    avg_hours = float(avg_seconds) / 3600.0 if avg_seconds else None

    # Desglose de casos por estado (todos los estados, con 0 si no hay).
    status_rows = (
        await db.execute(select(Case.status, func.count()).group_by(Case.status))
    ).all()
    cases_by_status = {s.value: 0 for s in CaseStatus}
    for st, cnt in status_rows:
        key = st.value if isinstance(st, CaseStatus) else str(st)
        cases_by_status[key] = cnt

    return DashboardKPIs(
        equipment_total=row.eq_total or 0,
        equipment_operational=row.eq_op or 0,
        equipment_out_of_service=row.eq_oos or 0,
        cases_open=row.cases_open or 0,
        cases_in_progress=row.cases_ip or 0,
        cases_closed_30d=row.cases_closed_30 or 0,
        preventive_due_30d=row.pm_due or 0,
        calibrations_due_30d=row.cal_due or 0,
        avg_close_time_hours=avg_hours,
        cases_by_status=cases_by_status,
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
