"""Lógica y generación automática de alertas."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFound
from app.db.enums import AlertSeverity, AlertType
from app.modules.alerts.models import Alert
from app.modules.alerts.schemas import AlertCreate
from app.modules.calibrations.models import Calibration
from app.modules.equipment.models import Equipment
from app.modules.maintenance.models import MaintenanceSchedule


async def list_alerts(
    db: AsyncSession, *, only_active: bool = True, scope: uuid.UUID | None = None, limit: int = 100
) -> Sequence[Alert]:
    stmt = select(Alert).order_by(Alert.created_at.desc())
    if scope is not None:
        stmt = stmt.join(Equipment, Equipment.id == Alert.equipment_id).where(
            Equipment.clinic_id == scope
        )
    if only_active:
        stmt = stmt.where(Alert.resolved_at.is_(None))
    return (await db.execute(stmt.limit(limit))).scalars().all()


async def _get_scoped(db: AsyncSession, alert_id: uuid.UUID, scope: uuid.UUID | None) -> Alert:
    obj = await db.get(Alert, alert_id)
    if obj is None:
        raise NotFound("Alerta")
    if scope is not None:
        eq = await db.get(Equipment, obj.equipment_id) if obj.equipment_id else None
        if eq is None or eq.clinic_id != scope:
            raise NotFound("Alerta")
    return obj


async def create(db: AsyncSession, payload: AlertCreate) -> Alert:
    obj = Alert(**payload.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


async def acknowledge(
    db: AsyncSession, alert_id: uuid.UUID, scope: uuid.UUID | None = None
) -> Alert:
    obj = await _get_scoped(db, alert_id, scope)
    obj.acknowledged_at = datetime.now(UTC)
    await db.flush()
    await db.refresh(obj)
    return obj


async def resolve(db: AsyncSession, alert_id: uuid.UUID, scope: uuid.UUID | None = None) -> Alert:
    obj = await _get_scoped(db, alert_id, scope)
    obj.resolved_at = datetime.now(UTC)
    await db.flush()
    await db.refresh(obj)
    return obj


# ---- Generación automática ------------------------------------------------
async def sweep_preventive(db: AsyncSession, *, horizon_days: int = 14) -> int:
    """Crea alertas para mantenimientos próximos a vencer."""
    today = datetime.now(UTC).date()
    upper = today + timedelta(days=horizon_days)

    stmt = select(MaintenanceSchedule).where(
        MaintenanceSchedule.next_due_at.is_not(None),
        MaintenanceSchedule.next_due_at <= upper,
    )
    schedules = (await db.execute(stmt)).scalars().all()

    created = 0
    for s in schedules:
        sev = AlertSeverity.CRITICAL if s.next_due_at < today else AlertSeverity.WARNING
        db.add(
            Alert(
                type=AlertType.PREVENTIVE_DUE,
                severity=sev,
                title=f"Preventivo {s.name}",
                message=f"Vence {s.next_due_at}",
                equipment_id=s.equipment_id,
                due_at=datetime.combine(s.next_due_at, datetime.min.time(), UTC),
            )
        )
        created += 1
    await db.flush()
    return created


async def sweep_calibrations(db: AsyncSession, *, horizon_days: int = 30) -> int:
    today = datetime.now(UTC).date()
    upper = today + timedelta(days=horizon_days)

    stmt = select(Calibration).where(
        Calibration.expires_at.is_not(None),
        Calibration.expires_at <= upper,
    )
    rows = (await db.execute(stmt)).scalars().all()
    created = 0
    for c in rows:
        sev = AlertSeverity.CRITICAL if c.expires_at < today else AlertSeverity.WARNING
        db.add(
            Alert(
                type=AlertType.CALIBRATION_DUE,
                severity=sev,
                title="Calibración por vencer",
                message=f"Calibración del equipo expira {c.expires_at}",
                equipment_id=c.equipment_id,
                due_at=datetime.combine(c.expires_at, datetime.min.time(), UTC),
            )
        )
        created += 1
    await db.flush()
    return created
