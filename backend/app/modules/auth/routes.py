"""Endpoints de autenticación."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.auth import service
from app.modules.auth.deps import require_authenticated
from app.modules.auth.schemas import LoginIn, TokenOut
from app.modules.clinics.models import Clinic
from app.modules.users.models import User
from app.modules.users.schemas import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
async def login(payload: LoginIn) -> TokenOut:
    """Login por contraseña (proxy a Supabase Auth)."""
    return await service.password_login(payload)


@router.get("/whoami", response_model=UserOut)
async def whoami(
    current: User = Depends(require_authenticated),
    db: AsyncSession = Depends(get_session),
) -> UserOut:
    clinic_name: str | None = None
    if current.clinic_id:
        clinic = await db.get(Clinic, current.clinic_id)
        clinic_name = clinic.name if clinic else None
    out = UserOut.model_validate(current)
    return out.model_copy(update={"clinic_name": clinic_name})
