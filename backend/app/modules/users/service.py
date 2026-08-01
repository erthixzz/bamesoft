"""Lógica de negocio de Users."""
from __future__ import annotations

import contextlib
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


def _find_auth_user_id(admin, email: str) -> str | None:
    """Busca en Supabase Auth un usuario por email. `None` si no existe.

    Sirve para recuperar cuentas huérfanas: si un intento anterior creó la
    cuenta en Auth pero falló al guardar el perfil, el email quedaría bloqueado
    para siempre. Al encontrarla, la adoptamos en vez de rechazar el alta.
    """
    try:
        listed = admin.auth.admin.list_users()
    except Exception:
        return None
    # supabase-py ha devuelto tanto una lista como un objeto con `.users`.
    users = getattr(listed, "users", listed) or []
    target = email.strip().lower()
    for u in users:
        if (getattr(u, "email", "") or "").strip().lower() == target:
            return getattr(u, "id", None)
    return None


async def invite_user(
    db: AsyncSession, payload: UserInvite, scope: uuid.UUID | None = None
) -> User:
    """Alta completa desde la UI: crea la cuenta en Supabase Auth y el perfil.

    Son dos sistemas distintos (GoTrue + Postgres) y no comparten transacción.
    El orden es: crear en Auth → guardar perfil → confirmar. Si el perfil falla,
    se **compensa** borrando la cuenta de Auth recién creada; de lo contrario
    quedaría huérfana y el email sería inusable para siempre.
    """
    if await get_by_email(db, payload.email):
        raise Conflict("El email ya está registrado")
    _guard_scope(payload.role, scope)

    try:
        admin = supabase_admin()
    except RuntimeError as exc:  # falta URL / SERVICE_KEY en el entorno
        raise BadRequest(
            "El servidor no tiene configurado Supabase (URL / SERVICE_KEY); "
            "no se pueden crear cuentas."
        ) from exc

    # 1) Cuenta en Supabase Auth.
    created_here = False
    try:
        res = admin.auth.admin.create_user(
            {
                "email": payload.email,
                "password": payload.password,
                "email_confirm": True,  # entra directo con email + contraseña
                "user_metadata": {"full_name": payload.full_name},
            }
        )
        auth_id = res.user.id
        created_here = True
    except Exception as exc:  # supabase-py lanza errores genéricos
        msg = str(exc)
        if "already" not in msg.lower():
            raise BadRequest(f"No se pudo crear la cuenta: {msg}") from exc
        # Existe en Auth pero no en nuestra BD (lo comprobamos arriba): es una
        # cuenta huérfana de un intento fallido. La adoptamos.
        auth_id = _find_auth_user_id(admin, payload.email)
        if auth_id is None:
            raise Conflict(
                "El email ya existe en el sistema de autenticación y no se pudo "
                "recuperar. Elimínalo desde Supabase Auth e inténtalo de nuevo."
            ) from exc

    # 2) Perfil en Postgres. Si falla, deshacemos la cuenta de Auth.
    try:
        user = User(
            id=uuid.UUID(auth_id),
            email=payload.email,
            full_name=payload.full_name,
            role=payload.role,
            phone=payload.phone,
            license_number=payload.license_number,
            clinic_id=scope if scope is not None else payload.clinic_id,
        )
        db.add(user)
        await db.flush()
        # Commit explícito: cierra la ventana en la que el perfil podría fallar
        # después de que esta función retorne, cuando ya no podríamos compensar.
        await db.commit()
        await db.refresh(user)
    except Exception as exc:
        await db.rollback()
        if created_here:  # solo borramos lo que creamos nosotros
            # Si la compensación falla no hay nada más que hacer: el error que
            # le importa al usuario es el de abajo.
            with contextlib.suppress(Exception):
                admin.auth.admin.delete_user(auth_id)
        raise BadRequest(f"No se pudo guardar el perfil del usuario: {exc}") from exc

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
