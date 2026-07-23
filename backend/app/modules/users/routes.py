"""Endpoints HTTP de Users."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.auth.deps import clinic_scope, require_authenticated, require_clinic_admin
from app.modules.documents.schemas import SignedUrlOut
from app.modules.users import service
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate, UserInvite, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
async def list_users(
    q: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_clinic_admin),
) -> list[User]:
    return list(
        await service.list_users(db, scope=clinic_scope(current), q=q, limit=limit, offset=offset)
    )


@router.get("/me", response_model=UserOut)
async def me(current: User = Depends(require_authenticated)) -> User:
    return current


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
) -> User:
    return await service.get_user(db, user_id, clinic_scope(current))


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_clinic_admin),
) -> User:
    return await service.create_user(db, payload, clinic_scope(current))


@router.post("/invite", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def invite_user(
    payload: UserInvite,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_clinic_admin),
) -> User:
    """Alta completa: crea la cuenta (Supabase Auth) y el perfil en un paso."""
    return await service.invite_user(db, payload, clinic_scope(current))


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_clinic_admin),
) -> User:
    return await service.update_user(db, user_id, payload, clinic_scope(current))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_clinic_admin),
) -> None:
    await service.deactivate_user(db, user_id, clinic_scope(current))


@router.post("/{user_id}/cv", response_model=UserOut)
async def upload_cv(
    user_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_clinic_admin),
) -> User:
    """Sube (o reemplaza) la hoja de vida (CV) del usuario."""
    body = await file.read()
    return await service.upload_cv(
        db,
        user_id,
        filename=file.filename or "cv",
        content=body,
        content_type=file.content_type or "application/octet-stream",
        scope=clinic_scope(current),
    )


@router.get("/{user_id}/cv-url", response_model=SignedUrlOut)
async def get_cv_url(
    user_id: uuid.UUID,
    expires_in: int = 3600,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
) -> SignedUrlOut:
    """URL firmada para ver la hoja de vida del usuario."""
    url = await service.cv_signed_url(db, user_id, clinic_scope(current))
    return SignedUrlOut(url=url, expires_in=expires_in)
