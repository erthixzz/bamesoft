"""Dependencies de autorización (JWT de Supabase)."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import Forbidden, NoProfile, Unauthorized
from app.core.security import TokenError, decode_token
from app.db.enums import UserRole
from app.db.session import get_session
from app.modules.access import requests_service
from app.modules.access import service as access_service
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
        # Antes se creaba aquí un perfil CLIENT automáticamente. Con el inicio de
        # sesión por Google eso significaba que CUALQUIERA con una cuenta de
        # Google se convertía en usuario de Bamesoft con solo entrar.
        #
        # Autenticarse (demostrar quién eres ante Google o Supabase) y estar
        # autorizado (existir en Bamesoft, dentro de una clínica) son cosas
        # distintas. El alta la hace un administrador desde /users.
        #
        # Antes de cerrar la puerta, dejamos la solicitud en la bandeja del
        # admin: si no, esta persona tendría que escribirle por fuera y no
        # quedaría rastro de que intentó entrar.
        await requests_service.record_attempt(claims)
        raise NoProfile()

    if not user.active:
        raise Forbidden("Usuario desactivado")

    # Marca de "última conexión" (throttled: como máximo un write cada 2 min por
    # usuario, para no escribir en cada request).
    now = datetime.now(UTC)
    if user.last_seen_at is None or (now - user.last_seen_at) > timedelta(minutes=2):
        user.last_seen_at = now

    return user


async def require_authenticated(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_session),
) -> User:
    return await _user_from_token(authorization, db)


# El guard más permisivo: exige sesión válida y usuario activo, sin filtrar rol.
# Se marca igual que los demás para que el gate de cobertura lo reconozca.
require_authenticated.__guard_roles__ = frozenset(UserRole)  # type: ignore[attr-defined]


def require_role(*roles: UserRole):
    async def _dep(user: User = Depends(require_authenticated)) -> User:
        if user.role not in roles:
            raise Forbidden(f"Requiere uno de los roles: {', '.join(r.value for r in roles)}")
        return user

    # Marca introspectable: `tests/test_authz_coverage.py` recorre las rutas y
    # exige que toda mutación tenga guard de rol + capacidad.
    _dep.__guard_roles__ = frozenset(roles)  # type: ignore[attr-defined]
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


async def assert_capability(
    db: AsyncSession, user: User, capability: str, feature: str | None = None
) -> None:
    """Versión imperativa de `requires(...)`, para comprobaciones que dependen
    del cuerpo de la petición (p. ej. cerrar un caso exige la capacidad `close`,
    pero se decide mirando el `status` que llega en el payload).

    Mismas reglas que `requires`: el super admin siempre pasa.
    """
    if user.role == UserRole.ADMIN:
        return
    if not await access_service.role_has_capability(db, user.role.value, capability):
        raise Forbidden(f"Tu rol no tiene permitida la acción «{capability}»")
    if feature is not None and not await access_service.feature_enabled(
        db, user.clinic_id, feature
    ):
        raise Forbidden(f"El módulo «{feature}» no está habilitado para tu compañía")


def requires(capability: str, feature: str | None = None):
    """Exige una capacidad de la matriz **Roles** y, si se indica, que el módulo
    esté habilitado para la compañía (matriz **Permisos**).

    Se usa en las MUTACIONES, junto al guard de rol correspondiente: el rol es
    la defensa base (hardcodeada, no editable desde la UI) y la matriz es la
    capa configurable encima. Ambas deben pasar.

    No se aplica a las lecturas: las capacidades son permisos de *navegación* y
    una página compone datos de varios módulos (p. ej. `/cases` lee equipos,
    usuarios y sectores). Exigirlas en los GET rompería esas páginas. Las
    lecturas quedan protegidas por rol + `clinic_scope`.

    El super admin siempre pasa: si la matriz pudiera dejarlo fuera, un cambio
    desafortunado dejaría la plataforma sin quien la administre.
    """

    async def _dep(
        user: User = Depends(require_authenticated),
        db: AsyncSession = Depends(get_session),
    ) -> User:
        await assert_capability(db, user, capability, feature)
        return user

    # Marca introspectable para el gate de cobertura (ver require_role).
    _dep.__capability__ = capability  # type: ignore[attr-defined]
    _dep.__feature__ = feature  # type: ignore[attr-defined]
    return _dep


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
    "assert_capability",
    "clinic_scope",
    "require_admin",
    "require_authenticated",
    "require_clinic_admin",
    "require_engineer",
    "require_role",
    "require_staff",
    "requires",
]
