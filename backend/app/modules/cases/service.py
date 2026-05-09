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


def _new_case_code() -> str:
    return f"BMS-{datetime.now(UTC):%Y%m}-{secrets.token_hex(2).upper()}"


async def list_cases(
    db: AsyncSession,
    *,
    status: CaseStatus | None = None,
    assigned_to: uuid.UUID | None = None,
    equipment_id: uuid.UUID | None = None,
    limit: int = 50,
    offset: int = 0,
) -> Sequence[Case]:
    stmt = select(Case).order_by(Case.created_at.desc())
    if status:
        stmt = stmt.where(Case.status == status)
    if assigned_to:
        stmt = stmt.where(Case.assigned_to == assigned_to)
    if equipment_id:
        stmt = stmt.where(Case.equipment_id == equipment_id)
    stmt = stmt.limit(limit).offset(offset)
    return (await db.execute(stmt)).scalars().all()


async def get_case(db: AsyncSession, case_id: uuid.UUID) -> Case:
    obj = await db.get(Case, case_id)
    if obj is None:
        raise NotFound("Caso")
    return obj


async def create_case(db: AsyncSession, payload: CaseCreate, reporter_id: uuid.UUID) -> Case:
    obj = Case(
        code=_new_case_code(),
        reported_by=reporter_id,
        opened_at=datetime.now(UTC),
        status=CaseStatus.ASSIGNED if payload.assigned_to else CaseStatus.OPEN,
        **payload.model_dump(),
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
) -> Case:
    obj = await get_case(db, case_id)
    data = payload.model_dump(exclude_unset=True)

    # Transiciones especiales
    if data.get("status") == CaseStatus.CLOSED and obj.status != CaseStatus.CLOSED:
        obj.closed_at = datetime.now(UTC)
    if data.get("assigned_to") and obj.status == CaseStatus.OPEN:
        obj.status = CaseStatus.ASSIGNED

    for k, v in data.items():
        setattr(obj, k, v)

    db.add(
        CaseActivity(
            case_id=obj.id,
            author_id=actor_id,
            action="updated",
            notes=", ".join(f"{k}={v}" for k, v in data.items()),
        )
    )
    await db.flush()
    await db.refresh(obj)
    return obj


async def list_activities(db: AsyncSession, case_id: uuid.UUID) -> Sequence[CaseActivity]:
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
) -> CaseActivity:
    case = await get_case(db, case_id)
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
