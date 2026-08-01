"""Endpoints de la bitácora de auditoría (solo admins)."""
from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.audit import service
from app.modules.audit.schemas import AuditActor, AuditPage, AuditSummary
from app.modules.auth.deps import clinic_scope, require_clinic_admin
from app.modules.users.models import User

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs", response_model=AuditPage)
async def list_logs(
    actor_id: uuid.UUID | None = None,
    entity: str | None = None,
    method: str | None = Query(default=None, description="POST, PATCH, PUT o DELETE"),
    q: str | None = Query(default=None, max_length=120, description="Búsqueda libre"),
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
    limit: int = Query(default=100, le=500),
    offset: int = 0,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_clinic_admin),
):
    """Bitácora filtrable por persona, operación, módulo, fecha y texto libre."""
    scope = clinic_scope(current)
    filters = {
        "actor_id": actor_id,
        "entity": entity,
        "method": method,
        "q": q,
        "date_from": date_from,
        "date_to": date_to,
    }
    items = await service.list_logs(db, scope=scope, limit=limit, offset=offset, **filters)
    total = await service.count_logs(db, scope=scope, **filters)
    return AuditPage(items=list(items), total=total, limit=limit, offset=offset)


@router.get("/actors", response_model=list[AuditActor])
async def list_actors(
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_clinic_admin),
):
    """Personas que aparecen en la bitácora, para poblar el filtro."""
    return await service.list_actors(db, scope=clinic_scope(current))


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
