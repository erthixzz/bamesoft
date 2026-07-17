"""Reportes / KPIs."""
from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import and_, distinct, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import CaseCompletion, CaseStatus, CaseType
from app.modules.cases.models import Case
from app.modules.equipment.models import Equipment
from app.modules.reports.schemas import (
    BreakdownReport,
    ComplianceItem,
    ComplianceReport,
    DailyPoint,
    DashboardKPIs,
    EquipmentReport,
    EquipmentReportRow,
    NamedCount,
    OperationsReport,
    ProductivityReport,
    ProductivityRow,
    ReporterRow,
    ServiceRow,
    ServicesReport,
)
from app.modules.sectors.models import Sector
from app.modules.standards.models import EquipmentStandard, Standard
from app.modules.users.models import User

_WAITING = (CaseStatus.WAITING_PARTS, CaseStatus.WAITING_CLIENT)


def _opened_col():
    """Fecha de referencia del caso (apertura o, en su defecto, creación)."""
    return func.coalesce(Case.opened_at, Case.created_at)


def _range_filters(date_from: date | None, date_to: date | None) -> list:
    conds = []
    col = _opened_col()
    if date_from:
        conds.append(col >= datetime(date_from.year, date_from.month, date_from.day, tzinfo=UTC))
    if date_to:
        end = datetime(date_to.year, date_to.month, date_to.day, tzinfo=UTC) + timedelta(days=1)
        conds.append(col < end)
    return conds


def _hours(seconds: float | None) -> float | None:
    return round(float(seconds) / 3600.0, 2) if seconds else None


# Una sola query SQL que devuelve todos los KPIs en columnas paralelas:
# convertimos 9 roundtrips a Postgres en 1 solo viaje (~150 ms vs ~1.4 s).
# `:scope::uuid is null` → sin filtro (super admin). Si trae un id, todo se
# limita a esa clínica (los casos/mantenimientos/calibraciones vía su equipo).
_DASHBOARD_SQL = text(
    """
    select
      (select count(*) from equipment e where (:scope::uuid is null or e.clinic_id = :scope)) as eq_total,
      (select count(*) from equipment e where e.status = 'operational' and (:scope::uuid is null or e.clinic_id = :scope)) as eq_op,
      (select count(*) from equipment e where e.status = 'out_of_service' and (:scope::uuid is null or e.clinic_id = :scope)) as eq_oos,
      (select count(*) from cases c join equipment e on e.id = c.equipment_id
        where c.status = 'open' and (:scope::uuid is null or e.clinic_id = :scope)) as cases_open,
      (select count(*) from cases c join equipment e on e.id = c.equipment_id
        where c.status = 'in_progress' and (:scope::uuid is null or e.clinic_id = :scope)) as cases_ip,
      (select count(*) from cases c join equipment e on e.id = c.equipment_id
        where c.status = 'closed' and c.closed_at >= :last_30 and (:scope::uuid is null or e.clinic_id = :scope)) as cases_closed_30,
      (select count(*) from maintenance_schedules ms join equipment e on e.id = ms.equipment_id
        where ms.next_due_at is not null and ms.next_due_at <= :horizon and (:scope::uuid is null or e.clinic_id = :scope)) as pm_due,
      (select count(*) from calibrations cal join equipment e on e.id = cal.equipment_id
        where cal.expires_at is not null and cal.expires_at <= :horizon and (:scope::uuid is null or e.clinic_id = :scope)) as cal_due,
      (select avg(extract(epoch from c.closed_at - c.opened_at)) from cases c join equipment e on e.id = c.equipment_id
        where c.closed_at is not null and c.opened_at is not null and (:scope::uuid is null or e.clinic_id = :scope)) as avg_close_seconds
    """
)


async def dashboard(db: AsyncSession, scope: uuid.UUID | None = None) -> DashboardKPIs:
    now = datetime.now(UTC)
    horizon = (now + timedelta(days=30)).date()
    last_30 = now - timedelta(days=30)

    sp = str(scope) if scope is not None else None
    row = (
        await db.execute(
            _DASHBOARD_SQL, {"horizon": horizon, "last_30": last_30, "scope": sp}
        )
    ).one()

    avg_seconds = row.avg_close_seconds
    avg_hours = float(avg_seconds) / 3600.0 if avg_seconds else None

    # Desglose de casos por estado (todos los estados, con 0 si no hay).
    status_stmt = select(Case.status, func.count())
    if scope is not None:
        status_stmt = status_stmt.join(Equipment, Equipment.id == Case.equipment_id).where(
            Equipment.clinic_id == scope
        )
    status_rows = (await db.execute(status_stmt.group_by(Case.status))).all()
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


async def compliance(db: AsyncSession, scope: uuid.UUID | None = None) -> ComplianceReport:
    total_stmt = select(func.count(Equipment.id))
    if scope is not None:
        total_stmt = total_stmt.where(Equipment.clinic_id == scope)
    total_eq = await db.scalar(total_stmt) or 0

    if scope is None:
        with_col = func.count(distinct(EquipmentStandard.equipment_id))
        stmt = (
            select(Standard.code, Standard.name, with_col.label("with_eq"))
            .join(EquipmentStandard, EquipmentStandard.standard_id == Standard.id, isouter=True)
            .group_by(Standard.id)
            .order_by(Standard.code)
        )
    else:
        with_col = func.count(distinct(Equipment.id))
        stmt = (
            select(Standard.code, Standard.name, with_col.label("with_eq"))
            .join(EquipmentStandard, EquipmentStandard.standard_id == Standard.id, isouter=True)
            .join(
                Equipment,
                and_(
                    Equipment.id == EquipmentStandard.equipment_id,
                    Equipment.clinic_id == scope,
                ),
                isouter=True,
            )
            .group_by(Standard.id)
            .order_by(Standard.code)
        )
    rows = (await db.execute(stmt)).all()

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


def _scope_case(stmt, scope: uuid.UUID | None):
    """Añade el aislamiento por clínica (vía el equipo del caso) a un select sobre Case."""
    if scope is None:
        return stmt
    return stmt.join(Equipment, Equipment.id == Case.equipment_id).where(
        Equipment.clinic_id == scope
    )


async def productivity(
    db: AsyncSession,
    date_from: date | None = None,
    date_to: date | None = None,
    scope: uuid.UUID | None = None,
) -> ProductivityReport:
    """Productividad por ingeniero: atendidos, completados/incompletos, tiempos de
    respuesta de cada tramo del flujo y FCR (resueltos completos a la primera)."""
    rng = _range_filters(date_from, date_to)

    def avg_secs(a, b):
        return func.avg(func.extract("epoch", b - a))

    # Completo/Incompleto solo cuenta en casos ya cerrados (servicio terminado).
    completed = func.count().filter(
        (Case.status == CaseStatus.CLOSED) & (Case.completion == CaseCompletion.COMPLETE)
    )
    incomplete = func.count().filter(
        (Case.status == CaseStatus.CLOSED) & (Case.completion == CaseCompletion.INCOMPLETE)
    )
    closed = func.count().filter(Case.status == CaseStatus.CLOSED)
    fcr = func.count().filter(
        (Case.status == CaseStatus.CLOSED) & (Case.completion == CaseCompletion.COMPLETE)
    )

    stmt = (
        select(
            Case.assigned_to.label("eid"),
            User.full_name.label("name"),
            func.count().label("attended"),
            completed.label("completed"),
            incomplete.label("incomplete"),
            closed.label("closed"),
            avg_secs(Case.assigned_at, Case.accepted_at).label("resp"),
            avg_secs(Case.accepted_at, Case.work_started_at).label("to_start"),
            avg_secs(Case.work_started_at, Case.finished_at).label("work"),
            fcr.label("fcr"),
        )
        .join(User, User.id == Case.assigned_to, isouter=True)
        .where(Case.assigned_to.is_not(None), *rng)
        .group_by(Case.assigned_to, User.full_name)
        .order_by(func.count().desc())
    )
    stmt = _scope_case(stmt, scope)
    rows = (await db.execute(stmt)).all()

    items: list[ProductivityRow] = []
    tot_att = tot_comp = tot_inc = tot_fcr = 0
    for r in rows:
        att = r.attended or 0
        items.append(
            ProductivityRow(
                engineer_id=str(r.eid) if r.eid else None,
                engineer_name=r.name or "Sin nombre",
                attended=att,
                completed=r.completed or 0,
                incomplete=r.incomplete or 0,
                closed=r.closed or 0,
                avg_response_hours=_hours(r.resp),
                avg_to_start_hours=_hours(r.to_start),
                avg_work_hours=_hours(r.work),
                fcr_count=r.fcr or 0,
                fcr_pct=round((r.fcr or 0) / att * 100.0, 1) if att else 0.0,
            )
        )
        tot_att += att
        tot_comp += r.completed or 0
        tot_inc += r.incomplete or 0
        tot_fcr += r.fcr or 0

    return ProductivityReport(
        items=items,
        attended=tot_att,
        completed=tot_comp,
        incomplete=tot_inc,
        fcr_count=tot_fcr,
        fcr_pct=round(tot_fcr / tot_att * 100.0, 1) if tot_att else 0.0,
    )


async def operations(
    db: AsyncSession,
    date_from: date | None = None,
    date_to: date | None = None,
    scope: uuid.UUID | None = None,
) -> OperationsReport:
    """Operación: llamadas reportadas/cerradas por día, incompletos, en espera y
    desglose por quién reportó (atendió la llamada)."""
    rng = _range_filters(date_from, date_to)

    totals = (
        await db.execute(
            _scope_case(
                select(
                    func.count().label("reported"),
                    func.count().filter(Case.status == CaseStatus.CLOSED).label("closed"),
                    # "Completas/Incompletas" solo tienen sentido en casos CERRADOS
                    # (el servicio ya terminó). Un caso en progreso nunca cuenta,
                    # aunque tenga `completion` de una edición previa.
                    func.count()
                    .filter(
                        (Case.status == CaseStatus.CLOSED)
                        & (Case.completion == CaseCompletion.COMPLETE)
                    )
                    .label("complete"),
                    func.count()
                    .filter(
                        (Case.status == CaseStatus.CLOSED)
                        & (Case.completion == CaseCompletion.INCOMPLETE)
                    )
                    .label("incomplete"),
                ).where(*rng),
                scope,
            )
        )
    ).one()

    waiting_now = await db.scalar(
        _scope_case(select(func.count()).select_from(Case).where(Case.status.in_(_WAITING)), scope)
    )

    # Reportados por día.
    day = func.date(_opened_col())
    rep_rows = (
        await db.execute(
            _scope_case(select(day.label("d"), func.count().label("n")).where(*rng), scope).group_by(day)
        )
    ).all()
    # Cerrados por día (sobre la fecha de cierre, dentro del mismo rango).
    cday = func.date(Case.closed_at)
    cl_conds = [Case.closed_at.is_not(None)]
    if date_from:
        cl_conds.append(cday >= date_from)
    if date_to:
        cl_conds.append(cday <= date_to)
    cl_rows = (
        await db.execute(
            _scope_case(select(cday.label("d"), func.count().label("n")).where(*cl_conds), scope).group_by(cday)
        )
    ).all()

    daily_map: dict[str, DailyPoint] = {}
    for r in rep_rows:
        k = str(r.d)
        daily_map.setdefault(k, DailyPoint(day=k)).reported = r.n
    for r in cl_rows:
        k = str(r.d)
        daily_map.setdefault(k, DailyPoint(day=k)).closed = r.n
    daily = [daily_map[k] for k in sorted(daily_map)]

    rep_by_base = _scope_case(
        select(
            Case.reported_by.label("uid"),
            User.full_name.label("name"),
            func.count().label("n"),
        )
        .join(User, User.id == Case.reported_by, isouter=True)
        .where(*rng),
        scope,
    )
    rep_by = (
        await db.execute(
            rep_by_base.group_by(Case.reported_by, User.full_name)
            .order_by(func.count().desc())
            .limit(20)
        )
    ).all()
    by_reporter = [
        ReporterRow(
            user_id=str(r.uid) if r.uid else None,
            name=r.name or "Desconocido",
            count=r.n or 0,
        )
        for r in rep_by
    ]

    return OperationsReport(
        reported_total=totals.reported or 0,
        closed_total=totals.closed or 0,
        complete_total=totals.complete or 0,
        incomplete_total=totals.incomplete or 0,
        waiting_now=waiting_now or 0,
        daily=daily,
        by_reporter=by_reporter,
    )


async def equipment_report(
    db: AsyncSession,
    date_from: date | None = None,
    date_to: date | None = None,
    scope: uuid.UUID | None = None,
) -> EquipmentReport:
    """Servicio agregado por equipo: cuántos casos tuvo, cuántos quedaron
    completos/incompletos, tipo de trabajo y cuánto se demoró en promedio."""
    rng = _range_filters(date_from, date_to)

    # Completo/Incompleto solo cuenta en casos ya cerrados (servicio terminado).
    completed = func.count().filter(
        (Case.status == CaseStatus.CLOSED) & (Case.completion == CaseCompletion.COMPLETE)
    )
    incomplete = func.count().filter(
        (Case.status == CaseStatus.CLOSED) & (Case.completion == CaseCompletion.INCOMPLETE)
    )
    corrective = func.count().filter(Case.type == CaseType.CORRECTIVE)
    preventive = func.count().filter(Case.type == CaseType.PREVENTIVE)

    stmt = (
        select(
            Equipment.id.label("eid"),
            Equipment.code,
            Equipment.name,
            Sector.name.label("sector_name"),
            func.count().label("cases_total"),
            completed.label("completed"),
            incomplete.label("incomplete"),
            corrective.label("corrective"),
            preventive.label("preventive"),
            func.avg(func.extract("epoch", Case.finished_at - Case.work_started_at)).label("work"),
            func.coalesce(func.sum(Case.operation_minutes), 0).label("op_min"),
            func.max(_opened_col()).label("last_at"),
        )
        .select_from(Case)
        .join(Equipment, Equipment.id == Case.equipment_id)
        .join(Sector, Sector.id == Equipment.sector_id, isouter=True)
        .where(*rng)
        .group_by(Equipment.id, Equipment.code, Equipment.name, Sector.name)
        .order_by(func.count().desc())
    )
    if scope is not None:
        stmt = stmt.where(Equipment.clinic_id == scope)
    rows = (await db.execute(stmt)).all()

    items = [
        EquipmentReportRow(
            equipment_id=str(r.eid),
            code=r.code,
            name=r.name,
            sector_name=r.sector_name,
            cases_total=r.cases_total or 0,
            completed=r.completed or 0,
            incomplete=r.incomplete or 0,
            corrective=r.corrective or 0,
            preventive=r.preventive or 0,
            avg_work_hours=_hours(r.work),
            total_operation_minutes=int(r.op_min or 0),
            last_service_at=r.last_at,
        )
        for r in rows
    ]
    return EquipmentReport(items=items, total=len(items))


async def services_report(
    db: AsyncSession,
    date_from: date | None = None,
    date_to: date | None = None,
    scope: uuid.UUID | None = None,
    engineer_id: uuid.UUID | None = None,
    equipment_id: uuid.UUID | None = None,
    limit: int = 300,
) -> ServicesReport:
    """Detalle servicio a servicio: qué se hizo, quién atendió y los tiempos."""
    rng = _range_filters(date_from, date_to)

    stmt = (
        select(
            Case,
            Equipment.code.label("eq_code"),
            Equipment.name.label("eq_name"),
            User.full_name.label("engineer"),
        )
        .join(Equipment, Equipment.id == Case.equipment_id)
        .join(User, User.id == Case.assigned_to, isouter=True)
        .where(*rng)
        .order_by(_opened_col().desc())
        .limit(limit)
    )
    if scope is not None:
        stmt = stmt.where(Equipment.clinic_id == scope)
    if engineer_id:
        stmt = stmt.where(Case.assigned_to == engineer_id)
    if equipment_id:
        stmt = stmt.where(Case.equipment_id == equipment_id)
    rows = (await db.execute(stmt)).all()

    items = [
        ServiceRow(
            case_id=str(c.id),
            code=c.code,
            title=c.title,
            equipment_label=f"{eq_code} · {eq_name}",
            engineer_name=engineer,
            type=c.type,
            status=c.status,
            completion=c.completion,
            work_performed=c.work_performed,
            operation_minutes=c.operation_minutes,
            opened_at=c.opened_at,
            assigned_at=c.assigned_at,
            accepted_at=c.accepted_at,
            work_started_at=c.work_started_at,
            finished_at=c.finished_at,
            closed_at=c.closed_at,
        )
        for c, eq_code, eq_name, engineer in rows
    ]
    return ServicesReport(items=items, total=len(items))


async def breakdown(
    db: AsyncSession,
    date_from: date | None = None,
    date_to: date | None = None,
    scope: uuid.UUID | None = None,
) -> BreakdownReport:
    """Distribuciones para gráficas: por estado, tipo, prioridad, unidad y mes."""
    rng = _range_filters(date_from, date_to)

    async def grouped(col) -> list[NamedCount]:
        stmt = _scope_case(select(col, func.count()).where(*rng), scope).group_by(col)
        rows = (await db.execute(stmt)).all()
        return [NamedCount(label=str(k), value=n) for k, n in rows if k is not None]

    by_status = await grouped(Case.status)
    by_type = await grouped(Case.type)
    by_priority = await grouped(Case.priority)

    # Por unidad de servicio (vía equipo → sector).
    sec_stmt = (
        select(func.coalesce(Sector.name, "Sin unidad"), func.count())
        .select_from(Case)
        .join(Equipment, Equipment.id == Case.equipment_id)
        .join(Sector, Sector.id == Equipment.sector_id, isouter=True)
        .where(*rng)
    )
    if scope is not None:
        sec_stmt = sec_stmt.where(Equipment.clinic_id == scope)
    sec_stmt = sec_stmt.group_by(Sector.name).order_by(func.count().desc())
    by_sector = [NamedCount(label=str(k), value=n) for k, n in (await db.execute(sec_stmt)).all()]

    # Tendencia mensual (YYYY-MM).
    month = func.to_char(_opened_col(), "YYYY-MM")
    m_stmt = _scope_case(select(month, func.count()).where(*rng), scope).group_by(month).order_by(month)
    monthly = [NamedCount(label=str(k), value=n) for k, n in (await db.execute(m_stmt)).all() if k]

    return BreakdownReport(
        by_status=by_status,
        by_type=by_type,
        by_priority=by_priority,
        by_sector=by_sector,
        monthly=monthly,
    )
