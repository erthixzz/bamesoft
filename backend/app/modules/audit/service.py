"""Consultas de la bitácora: listado y agregados para el dashboard."""
from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.models import AuditLog

_ENTITY_LABELS = {
    "cases": "Casos",
    "equipment": "Equipos",
    "users": "Usuarios",
    "sectors": "Unidades",
    "clinics": "Compañías",
    "documents": "Documentos",
    "alerts": "Alertas",
    "calibrations": "Calibraciones",
    "maintenance": "Mantenimiento",
    "standards": "Normas",
    "access": "Control de acceso",
    "reports": "Reportes",
}


def _scoped(stmt, scope: uuid.UUID | None):
    return stmt.where(AuditLog.clinic_id == scope) if scope is not None else stmt


def _range(date_from: date | None, date_to: date | None) -> list:
    conds = []
    if date_from:
        conds.append(func.date(AuditLog.created_at) >= date_from)
    if date_to:
        conds.append(func.date(AuditLog.created_at) <= date_to)
    return conds


async def list_logs(
    db: AsyncSession,
    *,
    scope: uuid.UUID | None = None,
    actor_id: uuid.UUID | None = None,
    entity: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[AuditLog]:
    stmt = _scoped(select(AuditLog), scope).where(*_range(date_from, date_to))
    if actor_id:
        stmt = stmt.where(AuditLog.actor_id == actor_id)
    if entity:
        stmt = stmt.where(AuditLog.entity == entity)
    stmt = stmt.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
    return (await db.execute(stmt)).scalars().all()


async def summary(
    db: AsyncSession,
    *,
    scope: uuid.UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> dict:
    rng = _range(date_from, date_to)

    total = await db.scalar(
        _scoped(select(func.count()).select_from(AuditLog), scope).where(*rng)
    )

    # Por actor (quién hizo más).
    a_rows = (
        await db.execute(
            _scoped(
                select(
                    AuditLog.actor_id,
                    func.coalesce(AuditLog.actor_name, "Desconocido").label("name"),
                    func.count().label("n"),
                ),
                scope,
            )
            .where(*rng)
            .group_by(AuditLog.actor_id, AuditLog.actor_name)
            .order_by(func.count().desc())
            .limit(12)
        )
    ).all()
    by_actor = [
        {"key": str(r.actor_id) if r.actor_id else "none", "label": r.name, "count": r.n}
        for r in a_rows
    ]

    # Por acción (qué se hizo más).
    ac_rows = (
        await db.execute(
            _scoped(select(AuditLog.action, func.count().label("n")), scope)
            .where(*rng)
            .group_by(AuditLog.action)
            .order_by(func.count().desc())
            .limit(12)
        )
    ).all()
    by_action = [{"key": r.action, "label": r.action, "count": r.n} for r in ac_rows]

    # Por módulo/entidad.
    e_rows = (
        await db.execute(
            _scoped(select(AuditLog.entity, func.count().label("n")), scope)
            .where(*rng)
            .group_by(AuditLog.entity)
            .order_by(func.count().desc())
        )
    ).all()
    by_entity = [
        {
            "key": r.entity or "otro",
            "label": _ENTITY_LABELS.get(r.entity or "", (r.entity or "Otro").capitalize()),
            "count": r.n,
        }
        for r in e_rows
    ]

    # Actividad por día.
    d_rows = (
        await db.execute(
            _scoped(
                select(func.date(AuditLog.created_at).label("d"), func.count().label("n")),
                scope,
            )
            .where(*rng)
            .group_by(func.date(AuditLog.created_at))
            .order_by(func.date(AuditLog.created_at))
        )
    ).all()
    by_day = [{"day": str(r.d), "count": r.n} for r in d_rows]

    return {
        "total": total or 0,
        "actors": len([a for a in by_actor if a["key"] != "none"]),
        "by_actor": by_actor,
        "by_action": by_action,
        "by_entity": by_entity,
        "by_day": by_day,
    }


async def record(
    db: AsyncSession,
    *,
    actor_id: uuid.UUID | None,
    actor_name: str | None,
    actor_role: str | None,
    clinic_id: uuid.UUID | None,
    method: str,
    action: str,
    entity: str | None,
    entity_id: str | None,
    path: str | None,
    status_code: int | None,
    detail: str | None = None,
) -> None:
    db.add(
        AuditLog(
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role=actor_role,
            clinic_id=clinic_id,
            method=method,
            action=action,
            detail=detail,
            entity=entity,
            entity_id=entity_id,
            path=path,
            status_code=status_code,
        )
    )
    await db.flush()
