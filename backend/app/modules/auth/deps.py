"""Dependencies de autorización (JWT de Supabase)."""
from __future__ import annotations

import uuid

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import Forbidden, Unauthorized
from app.core.security import TokenError, decode_token
from app.db.enums import UserRole
from app.db.session import get_session
from app.modules.users.models import User


async def _user_from_token(authorization: str | None, db: AsyncSession) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise Unauthorized("Falta token Bearer")
    token = authorization.split(" ", 1)[1].strip()

    try:
        claims = decode_token(token)
    except TokenError as exc:
        raise Unauthorized(f"Token inválido: {exc}") from exc

    sub = claims.get("sub")
    if not sub:
        raise Unauthorized("Token sin subject")

    try:
        user_id = uuid.UUID(sub)
    except ValueError as exc:
        raise Unauthorized("Subject no es UUID") from exc

    user = await db.get(User, user_id)
    if user is None:
        # primer login post-Supabase: crear perfil mínimo
        email = claims.get("email") or ""
        full_name = claims.get("user_metadata", {}).get("full_name") or email.split("@")[0]
        user = User(id=user_id, email=email, full_name=full_name, role=UserRole.CLIENT)
        db.add(user)
        await db.flush()
        await db.refresh(user)

    if not user.active:
        raise Forbidden("Usuario desactivado")

    return user


async def require_authenticated(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_session),
) -> User:
    return await _user_from_token(authorization, db)


def require_role(*roles: UserRole):
    async def _dep(user: User = Depends(require_authenticated)) -> User:
        if user.role not in roles:
            raise Forbidden(f"Requiere uno de los roles: {', '.join(r.value for r in roles)}")
        return user

    return _dep


require_admin = require_role(UserRole.ADMIN)  # super admin (global)
require_clinic_admin = require_role(UserRole.ADMIN, UserRole.CLINIC_ADMIN)
require_engineer = require_role(UserRole.ADMIN, UserRole.CLINIC_ADMIN, UserRole.ENGINEER)
require_staff = require_role(
    UserRole.ADMIN,
    UserRole.CLINIC_ADMIN,
    UserRole.ENGINEER,
    UserRole.SERVICE,
    UserRole.SUPPORT,
)


def clinic_scope(user: User) -> uuid.UUID | None:
    """Clínica a la que se limita el usuario.

    `None` = super admin (ve todas). Cualquier otro rol queda restringido a su
    propia clínica (`user.clinic_id`); si no tiene clínica asignada, se usa un
    UUID imposible para que no vea nada de otras clínicas.
    """
    if user.role == UserRole.ADMIN:
        return None
    return user.clinic_id or uuid.UUID(int=0)


__all__ = [
    "clinic_scope",
    "require_admin",
    "require_authenticated",
    "require_clinic_admin",
    "require_engineer",
    "require_role",
    "require_staff",
]
