"""Endpoints HTTP de Users."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.auth.deps import require_admin, require_authenticated
from app.modules.users import service
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
async def list_users(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),
) -> list[User]:
    return list(await service.list_users(db, limit=limit, offset=offset))


@router.get("/me", response_model=UserOut)
async def me(current: User = Depends(require_authenticated)) -> User:
    return current


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
) -> User:
    return await service.get_user(db, user_id)


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),
) -> User:
    return await service.create_user(db, payload)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),
) -> User:
    return await service.update_user(db, user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),
) -> None:
    await service.deactivate_user(db, user_id)
