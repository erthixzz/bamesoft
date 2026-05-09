from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.auth.deps import require_authenticated
from app.modules.reports import service
from app.modules.reports.schemas import ComplianceReport, DashboardKPIs
from app.modules.users.models import User

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/dashboard", response_model=DashboardKPIs)
async def dashboard(
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    return await service.dashboard(db)


@router.get("/compliance", response_model=ComplianceReport)
async def compliance(
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    return await service.compliance(db)
