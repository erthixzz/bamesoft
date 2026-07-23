"""Lógica de negocio de Users."""
from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import BadRequest, Conflict, Forbidden, NotFound
from app.db.enums import UserRole
from app.integrations import supabase as sb
from app.integrations.supabase import supabase_admin
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate, UserInvite, UserUpdate


async def list_users(
    db: AsyncSession,
    *,
    scope: uuid.UUID | None = None,
    q: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[User]:
    stmt = select(User).order_by(User.created_at.desc())
    if scope is not None:
        stmt = stmt.where(User.clinic_id == scope)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(User.full_name.ilike(like) | User.email.ilike(like))
    stmt = stmt.limit(limit).offset(offset)
    return (await db.execute(stmt)).scalars().all()


async def get_user(
    db: AsyncSession, user_id: uuid.UUID, scope: uuid.UUID | None = None
) -> User:
    user = await db.get(User, user_id)
    if user is None or (scope is not None and user.clinic_id != scope):
        raise NotFound("Usuario")
    return user


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return (await db.execute(stmt)).scalar_one_or_none()


def _guard_scope(payload_role: UserRole | None, scope: uuid.UUID | None) -> None:
    """El admin de clínica no puede crear/asignar super admins."""
    if scope is not None and payload_role == UserRole.ADMIN:
        raise Forbidden("No puedes asignar el rol de super administrador")


async def create_user(
    db: AsyncSession, payload: UserCreate, scope: uuid.UUID | None = None
) -> User:
    if await get_by_email(db, payload.email):
        raise Conflict("El email ya está registrado")
    _guard_scope(payload.role, scope)
    data = payload.model_dump()
    if scope is not None:
        data["clinic_id"] = scope  # el admin de clínica solo crea en la suya
    user = User(**data)
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def invite_user(
    db: AsyncSession, payload: UserInvite, scope: uuid.UUID | None = None
) -> User:
    """Alta completa desde la UI: crea la cuenta en Supabase Auth y el perfil."""
    if await get_by_email(db, payload.email):
        raise Conflict("El email ya está registrado")
    _guard_scope(payload.role, scope)

    try:
        res = supabase_admin().auth.admin.create_user(
            {
                "email": payload.email,
                "password": payload.password,
                "email_confirm": True,  # entra directo con email + contraseña
                "user_metadata": {"full_name": payload.full_name},
            }
        )
    except Exception as exc:  # supabase-py lanza errores genéricos
        msg = str(exc)
        if "already" in msg.lower():
            raise Conflict("El email ya existe en el sistema de autenticación") from exc
        raise BadRequest(f"No se pudo crear la cuenta: {msg}") from exc

    user = User(
        id=uuid.UUID(res.user.id),
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role,
        phone=payload.phone,
        license_number=payload.license_number,
        clinic_id=scope if scope is not None else payload.clinic_id,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def update_user(
    db: AsyncSession, user_id: uuid.UUID, payload: UserUpdate, scope: uuid.UUID | None = None
) -> User:
    user = await get_user(db, user_id, scope)
    data = payload.model_dump(exclude_unset=True)
    _guard_scope(data.get("role"), scope)
    if scope is not None:
        data.pop("clinic_id", None)  # no puede mover usuarios a otra clínica
    for k, v in data.items():
        setattr(user, k, v)
    await db.flush()
    await db.refresh(user)
    return user


async def deactivate_user(
    db: AsyncSession, user_id: uuid.UUID, scope: uuid.UUID | None = None
) -> None:
    user = await get_user(db, user_id, scope)
    user.active = False
    await db.flush()


async def upload_cv(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    filename: str,
    content: bytes,
    content_type: str,
    scope: uuid.UUID | None = None,
) -> User:
    """Sube (o reemplaza) la hoja de vida del usuario en Supabase Storage."""
    user = await get_user(db, user_id, scope)
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    path = f"cv/{user_id}/{ts}_{sb.safe_filename(filename)}"
    try:
        sb.upload_file(path, content, content_type=content_type)
    except Exception as exc:  # error de Storage → mensaje legible (con CORS)
        raise BadRequest(f"No se pudo subir el archivo: {exc}") from exc
    user.cv_path = path
    await db.flush()
    await db.refresh(user)
    return user


async def cv_signed_url(
    db: AsyncSession, user_id: uuid.UUID, scope: uuid.UUID | None = None
) -> str:
    """Devuelve una URL firmada para ver la hoja de vida del usuario."""
    user = await get_user(db, user_id, scope)
    if not user.cv_path:
        raise NotFound("Hoja de vida")
    return sb.signed_url(user.cv_path)
