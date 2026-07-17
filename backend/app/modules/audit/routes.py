"""Endpoints de la bitácora de auditoría (solo admins)."""
from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.audit import service
from app.modules.audit.schemas import AuditLogOut, AuditSummary
from app.modules.auth.deps import clinic_scope, require_clinic_admin
from app.modules.users.models import User

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs", response_model=list[AuditLogOut])
async def list_logs(
    actor_id: uuid.UUID | None = None,
    entity: str | None = None,
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_clinic_admin),
):
    return list(
        await service.list_logs(
            db,
            scope=clinic_scope(current),
            actor_id=actor_id,
            entity=entity,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
    )


@router.get("/summary", response_model=AuditSummary)
async def summary(
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_clinic_admin),
):
    return await service.summary(
        db, scope=clinic_scope(current), date_from=date_from, date_to=date_to
    )
