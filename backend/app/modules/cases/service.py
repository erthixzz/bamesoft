"""Lógica de casos y bitácora."""
from __future__ import annotations

import secrets
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import BadRequest, NotFound
from app.db.enums import CaseStatus
from app.modules.cases.models import Case, CaseActivity
from app.modules.cases.schemas import CaseActivityIn, CaseCreate, CaseUpdate
from app.modules.equipment.models import Equipment


def _new_case_code() -> str:
    return f"BMS-{datetime.now(UTC):%Y%m}-{secrets.token_hex(2).upper()}"


async def list_cases(
    db: AsyncSession,
    *,
    status: CaseStatus | None = None,
    assigned_to: uuid.UUID | None = None,
    equipment_id: uuid.UUID | None = None,
    scope: uuid.UUID | None = None,
    limit: int = 50,
    offset: int = 0,
) -> Sequence[Case]:
    stmt = select(Case).order_by(Case.created_at.desc())
    if scope is not None:
        # Aislar por clínica a través del equipo del caso.
        stmt = stmt.join(Equipment, Equipment.id == Case.equipment_id).where(
            Equipment.clinic_id == scope
        )
    if status:
        stmt = stmt.where(Case.status == status)
    if assigned_to:
        stmt = stmt.where(Case.assigned_to == assigned_to)
    if equipment_id:
        stmt = stmt.where(Case.equipment_id == equipment_id)
    stmt = stmt.limit(limit).offset(offset)
    return (await db.execute(stmt)).scalars().all()


async def get_case(db: AsyncSession, case_id: uuid.UUID, scope: uuid.UUID | None = None) -> Case:
    obj = await db.get(Case, case_id)
    if obj is None:
        raise NotFound("Caso")
    if scope is not None:
        eq = await db.get(Equipment, obj.equipment_id)
        if eq is None or eq.clinic_id != scope:
            raise NotFound("Caso")
    return obj


async def get_case_by_code(
    db: AsyncSession, code: str, scope: uuid.UUID | None = None
) -> Case:
    stmt = select(Case).where(Case.code == code)
    obj = (await db.execute(stmt)).scalar_one_or_none()
    if obj is None:
        raise NotFound("Caso")
    if scope is not None:
        eq = await db.get(Equipment, obj.equipment_id)
        if eq is None or eq.clinic_id != scope:
            raise NotFound("Caso")
    return obj


async def create_case(
    db: AsyncSession, payload: CaseCreate, reporter_id: uuid.UUID, scope: uuid.UUID | None = None
) -> Case:
    data = payload.model_dump()

    # El equipo elegido debe pertenecer a la clínica del usuario (si está scoped).
    if scope is not None:
        eq = await db.get(Equipment, data["equipment_id"])
        if eq is None or eq.clinic_id != scope:
            raise NotFound("Equipo")

    # Si llega un sector pero no hay asignado, usar el ingeniero por defecto.
    if data.get("sector_id") and not data.get("assigned_to"):
        from app.modules.sectors.models import Sector  # import tardío para evitar ciclos

        sector = await db.get(Sector, data["sector_id"])
        if sector and sector.default_engineer_id:
            data["assigned_to"] = sector.default_engineer_id

    now = datetime.now(UTC)
    assigned = bool(data.get("assigned_to"))
    obj = Case(
        code=_new_case_code(),
        reported_by=reporter_id,
        opened_at=now,
        status=CaseStatus.ASSIGNED if assigned else CaseStatus.OPEN,
        assigned_at=now if assigned else None,
        **data,
    )
    db.add(obj)
    await db.flush()

    db.add(
        CaseActivity(
            case_id=obj.id, author_id=reporter_id, action="created", notes="Caso creado"
        )
    )
    await db.flush()
    await db.refresh(obj)
    return obj


async def update_case(
    db: AsyncSession,
    case_id: uuid.UUID,
    payload: CaseUpdate,
    actor_id: uuid.UUID,
    scope: uuid.UUID | None = None,
) -> Case:
    obj = await get_case(db, case_id, scope)
    data = payload.model_dump(exclude_unset=True)
    now = datetime.now(UTC)

    # Transiciones especiales: auto-sellado de tiempos del flujo de servicio.
    new_status = data.get("status")
    if new_status == CaseStatus.CLOSED and obj.status != CaseStatus.CLOSED:
        obj.closed_at = now
        if obj.finished_at is None:
            obj.finished_at = now
    if new_status == CaseStatus.IN_PROGRESS and obj.work_started_at is None:
        obj.work_started_at = now
    if data.get("assigned_to") and obj.status == CaseStatus.OPEN:
        obj.status = CaseStatus.ASSIGNED
        if obj.assigned_at is None:
            obj.assigned_at = now

    for k, v in data.items():
        setattr(obj, k, v)

    # No registrar rutas internas (p. ej. la ruta de almacenamiento de la firma);
    # el frontend traduce las claves restantes a etiquetas legibles.
    _hidden = {"signature_path"}
    db.add(
        CaseActivity(
            case_id=obj.id,
            author_id=actor_id,
            action="updated",
            notes=", ".join(f"{k}={v}" for k, v in data.items() if k not in _hidden),
        )
    )
    await db.flush()
    await db.refresh(obj)
    return obj


async def accept_case(
    db: AsyncSession, case_id: uuid.UUID, engineer_id: uuid.UUID, scope: uuid.UUID | None = None
) -> Case:
    """El ingeniero toma el caso (sella `accepted_at`)."""
    obj = await get_case(db, case_id, scope)
    if obj.status in (CaseStatus.CLOSED, CaseStatus.CANCELLED):
        raise BadRequest("No se puede tomar un caso cerrado o cancelado")

    now = datetime.now(UTC)
    if obj.assigned_to is None:
        obj.assigned_to = engineer_id
    if obj.assigned_at is None:
        obj.assigned_at = now
    if obj.status == CaseStatus.OPEN:
        obj.status = CaseStatus.ASSIGNED
    if obj.accepted_at is None:
        obj.accepted_at = now

    db.add(
        CaseActivity(
            case_id=obj.id, author_id=engineer_id, action="accepted", notes="Caso tomado por el ingeniero"
        )
    )
    await db.flush()
    await db.refresh(obj)
    return obj


async def list_activities(
    db: AsyncSession, case_id: uuid.UUID, scope: uuid.UUID | None = None
) -> Sequence[CaseActivity]:
    await get_case(db, case_id, scope)  # valida pertenencia a la clínica
    stmt = (
        select(CaseActivity)
        .where(CaseActivity.case_id == case_id)
        .order_by(CaseActivity.created_at)
    )
    return (await db.execute(stmt)).scalars().all()


async def add_activity(
    db: AsyncSession,
    case_id: uuid.UUID,
    payload: CaseActivityIn,
    author_id: uuid.UUID,
    scope: uuid.UUID | None = None,
) -> CaseActivity:
    case = await get_case(db, case_id, scope)
    if case.status in (CaseStatus.CLOSED, CaseStatus.CANCELLED):
        raise BadRequest("No se puede añadir actividad a un caso cerrado")
    activity = CaseActivity(
        case_id=case_id,
        author_id=author_id,
        action=payload.action,
        notes=payload.notes,
    )
    db.add(activity)
    await db.flush()
    await db.refresh(activity)
    return activity
