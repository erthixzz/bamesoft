"""Endpoints de casos."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import CaseStatus
from app.db.session import get_session
from app.modules.auth.deps import clinic_scope, require_authenticated, require_engineer
from app.modules.cases import service
from app.modules.cases.schemas import (
    CaseActivityIn,
    CaseActivityOut,
    CaseCreate,
    CaseOut,
    CaseUpdate,
)
from app.modules.users.models import User

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("", response_model=list[CaseOut])
async def list_cases(
    status_: CaseStatus | None = Query(default=None, alias="status"),
    assigned_to: uuid.UUID | None = None,
    equipment_id: uuid.UUID | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
):
    return list(
        await service.list_cases(
            db,
            status=status_,
            assigned_to=assigned_to,
            equipment_id=equipment_id,
            scope=clinic_scope(current),
            limit=limit,
            offset=offset,
        )
    )


@router.post("", response_model=CaseOut, status_code=status.HTTP_201_CREATED)
async def create_case(
    payload: CaseCreate,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
):
    return await service.create_case(db, payload, current.id, clinic_scope(current))


@router.get("/by-code/{code}", response_model=CaseOut)
async def get_case_by_code(
    code: str,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
):
    return await service.get_case_by_code(db, code, clinic_scope(current))


@router.get("/{case_id}", response_model=CaseOut)
async def get_case(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
):
    return await service.get_case(db, case_id, clinic_scope(current))


@router.patch("/{case_id}", response_model=CaseOut)
async def update_case(
    case_id: uuid.UUID,
    payload: CaseUpdate,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_engineer),
):
    return await service.update_case(db, case_id, payload, current.id, clinic_scope(current))


@router.post("/{case_id}/accept", response_model=CaseOut)
async def accept_case(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_engineer),
):
    return await service.accept_case(db, case_id, current.id, clinic_scope(current))


@router.get("/{case_id}/activities", response_model=list[CaseActivityOut])
async def list_activities(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
):
    return list(await service.list_activities(db, case_id, clinic_scope(current)))


@router.post(
    "/{case_id}/activities",
    response_model=CaseActivityOut,
    status_code=status.HTTP_201_CREATED,
)
async def add_activity(
    case_id: uuid.UUID,
    payload: CaseActivityIn,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
):
    return await service.add_activity(db, case_id, payload, current.id, clinic_scope(current))
