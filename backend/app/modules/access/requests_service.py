"""Lógica de las solicitudes de acceso."""
from __future__ import annotations

import contextlib
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import BadRequest, Conflict, NotFound
from app.db.enums import UserRole
from app.db.session import AsyncSessionLocal
from app.modules.access.requests_models import AccessRequest
from app.modules.users.models import User

PENDING = "pending"
APPROVED = "approved"
REJECTED = "rejected"


async def record_attempt(claims: dict) -> None:
    """Deja constancia de que alguien autenticado intentó entrar sin perfil.

    Usa una sesión propia a propósito: quien llama a esto está a punto de lanzar
    un 403, y la sesión de la petición se descartará con el rollback. Sin sesión
    aparte, la solicitud nunca se guardaría.

    Nunca propaga errores: registrar la solicitud no debe cambiar la respuesta
    que recibe el usuario (que es, y debe seguir siendo, un 403).
    """
    sub = claims.get("sub")
    email = (claims.get("email") or "").strip()
    if not sub or not email:
        return  # sin identidad utilizable no hay nada que mostrarle al admin

    try:
        user_id = uuid.UUID(str(sub))
    except (ValueError, TypeError):
        return

    meta = claims.get("user_metadata") or {}
    now = datetime.now(UTC)

    with contextlib.suppress(Exception):
        async with AsyncSessionLocal() as db:
            existing = await db.get(AccessRequest, user_id)
            if existing is None:
                db.add(
                    AccessRequest(
                        user_id=user_id,
                        email=email,
                        full_name=meta.get("full_name") or meta.get("name"),
                        avatar_url=meta.get("avatar_url") or meta.get("picture"),
                        provider=(claims.get("app_metadata") or {}).get("provider"),
                        status=PENDING,
                    )
                )
            else:
                # Un reintento actualiza la fila; no resucita una ya rechazada,
                # para que descartar a alguien sea efectivo y no vuelva cada vez.
                existing.attempts += 1
                existing.last_seen_at = now
                if existing.status == PENDING:
                    existing.email = email
                    existing.full_name = meta.get("full_name") or existing.full_name
                    existing.avatar_url = meta.get("avatar_url") or existing.avatar_url
            await db.commit()


async def list_requests(
    db: AsyncSession, *, status: str | None = PENDING, limit: int = 100
) -> Sequence[AccessRequest]:
    stmt = select(AccessRequest).order_by(AccessRequest.last_seen_at.desc()).limit(limit)
    if status:
        stmt = stmt.where(AccessRequest.status == status)
    return (await db.execute(stmt)).scalars().all()


async def count_pending(db: AsyncSession) -> int:
    rows = (
        await db.execute(select(AccessRequest.user_id).where(AccessRequest.status == PENDING))
    ).all()
    return len(rows)


async def _get_pending(db: AsyncSession, user_id: uuid.UUID) -> AccessRequest:
    req = await db.get(AccessRequest, user_id)
    if req is None:
        raise NotFound("Solicitud")
    if req.status != PENDING:
        raise Conflict(f"La solicitud ya está {req.status}")
    return req


async def approve(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    clinic_id: uuid.UUID,
    role: UserRole,
    resolved_by: uuid.UUID,
) -> User:
    """Crea el perfil con el MISMO id de Supabase Auth y cierra la solicitud.

    Que el id coincida es lo que hace que la sesión abierta de esa persona
    empiece a funcionar: al pulsar «Comprobar de nuevo» ya encuentra su perfil.
    """
    req = await _get_pending(db, user_id)

    existing = (
        await db.execute(select(User).where(User.email == req.email))
    ).scalar_one_or_none()
    if existing is not None:
        raise Conflict(f"Ya existe un usuario con el email {req.email}")

    user = User(
        id=req.user_id,
        email=req.email,
        full_name=req.full_name or req.email.split("@")[0],
        role=role,
        clinic_id=clinic_id,
    )
    db.add(user)

    req.status = APPROVED
    req.resolved_at = datetime.now(UTC)
    req.resolved_by = resolved_by

    await db.flush()
    await db.refresh(user)
    return user


async def reject(
    db: AsyncSession, user_id: uuid.UUID, *, resolved_by: uuid.UUID, note: str | None = None
) -> AccessRequest:
    req = await _get_pending(db, user_id)
    req.status = REJECTED
    req.resolved_at = datetime.now(UTC)
    req.resolved_by = resolved_by
    req.note = (note or "").strip() or None
    await db.flush()
    await db.refresh(req)
    return req


async def reopen(db: AsyncSession, user_id: uuid.UUID) -> AccessRequest:
    """Devuelve una solicitud rechazada a pendiente (por si fue un error)."""
    req = await db.get(AccessRequest, user_id)
    if req is None:
        raise NotFound("Solicitud")
    if req.status == APPROVED:
        raise BadRequest("Una solicitud aprobada no se puede reabrir")
    req.status = PENDING
    req.resolved_at = None
    req.resolved_by = None
    req.note = None
    await db.flush()
    await db.refresh(req)
    return req
