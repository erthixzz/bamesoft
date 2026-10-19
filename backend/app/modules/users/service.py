"""Lógica de negocio de Users."""
from __future__ import annotations

import contextlib
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
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


def _auth_admin():
    """Cliente admin de Supabase Auth, o un error legible si falta configuración."""
    try:
        return supabase_admin()
    except RuntimeError as exc:  # falta URL / SERVICE_KEY en el entorno
        raise BadRequest(
            "El servidor no tiene configurado Supabase (URL / SERVICE_KEY); "
            "no se pueden gestionar las credenciales."
        ) from exc


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
            # Quien no eligió su contraseña (se quedó con la por defecto) tiene
            # que cambiarla antes de poder usar la aplicación.
            must_change_password=payload.password == settings.DEFAULT_USER_PASSWORD,
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

    # El email es la credencial de acceso: vive en Supabase Auth y en nuestra
    # tabla. Cambiar solo una de las dos deja al usuario sin poder entrar (Auth)
    # o invisible para la app (perfil), así que se cambian las dos o ninguna.
    new_email = (data.pop("email", None) or "").strip().lower() or None
    if new_email and new_email != user.email:
        existing = await get_by_email(db, new_email)
        if existing is not None and existing.id != user.id:
            raise Conflict("El email ya está registrado")
        _auth_admin().auth.admin.update_user_by_id(
            str(user.id), {"email": new_email, "email_confirm": True}
        )
        user.email = new_email

    for k, v in data.items():
        setattr(user, k, v)
    await db.flush()
    await db.refresh(user)
    return user


async def set_user_password(
    db: AsyncSession, user_id: uuid.UUID, new_password: str, scope: uuid.UUID | None = None
) -> User:
    """Un administrador asigna una contraseña nueva a otro usuario.

    Es la salida cuando alguien no puede entrar y no hay forma de recuperar su
    contraseña. Si se le deja la provisional, vuelve a quedar obligado a
    cambiarla en el siguiente acceso.
    """
    user = await get_user(db, user_id, scope)
    try:
        _auth_admin().auth.admin.update_user_by_id(str(user.id), {"password": new_password})
    except Exception as exc:  # no cumple la política del proyecto, etc.
        raise BadRequest(f"No se pudo cambiar la contraseña: {exc}") from exc

    user.must_change_password = new_password == settings.DEFAULT_USER_PASSWORD
    await db.flush()
    await db.refresh(user)
    return user


async def change_own_password(db: AsyncSession, user: User, new_password: str) -> User:
    """Cambia la contraseña del propio usuario y levanta la bandera de cambio.

    Se hace con la service key contra GoTrue (no con el token del usuario) para
    que el flujo funcione igual tanto en el cambio obligatorio del primer acceso
    como en un cambio voluntario posterior.
    """
    if new_password == settings.DEFAULT_USER_PASSWORD:
        raise BadRequest("Elige una contraseña distinta de la provisional.")

    try:
        _auth_admin().auth.admin.update_user_by_id(str(user.id), {"password": new_password})
    except Exception as exc:  # p. ej. no cumple la política del proyecto
        raise BadRequest(f"No se pudo cambiar la contraseña: {exc}") from exc

    user.must_change_password = False
    await db.flush()
    await db.refresh(user)
    return user


async def _history_counts(db: AsyncSession, user_id: uuid.UUID) -> dict[str, int]:
    """Rastro de trabajo del usuario que se perdería si se borra la fila.

    Las FK a `users` son todas ON DELETE SET NULL: Postgres borraría sin
    protestar y dejaría casos, calibraciones y documentos sin responsable. En un
    contexto clínico ese rastro es justo lo que no se puede perder, así que se
    cuenta antes y se bloquea. `audit_logs` no entra: guarda el nombre y el rol
    desnormalizados, así que sobrevive al borrado.
    """
    # Import local: estos módulos importan `users` y a nivel de módulo habría ciclo.
    from app.modules.calibrations.models import Calibration
    from app.modules.cases.models import Case, CaseActivity
    from app.modules.documents.models import Document

    async def count(stmt) -> int:
        return int((await db.execute(select(func.count()).select_from(stmt))).scalar_one())

    return {
        "casos reportados": await count(
            select(Case.id).where(Case.reported_by == user_id).subquery()
        ),
        "casos atendidos": await count(
            select(Case.id).where(Case.assigned_to == user_id).subquery()
        ),
        "notas en casos": await count(
            select(CaseActivity.id).where(CaseActivity.author_id == user_id).subquery()
        ),
        "documentos subidos": await count(
            select(Document.id).where(Document.uploaded_by == user_id).subquery()
        ),
        "calibraciones": await count(
            select(Calibration.id).where(Calibration.performed_by == user_id).subquery()
        ),
    }


async def delete_user_permanently(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    actor_id: uuid.UUID,
    scope: uuid.UUID | None = None,
) -> None:
    """Borra de verdad: perfil, cuenta de acceso y hoja de vida.

    Solo si el usuario no dejó rastro de trabajo. Para quien sí lo dejó, la
    desactivación es la operación correcta: corta el acceso en cada petición y
    conserva la trazabilidad.
    """
    user = await get_user(db, user_id, scope)
    if user.id == actor_id:
        raise BadRequest("No puedes eliminar tu propia cuenta.")

    counts = await _history_counts(db, user_id)
    rastro = [f"{n} {etiqueta}" for etiqueta, n in counts.items() if n]
    if rastro:
        raise Conflict(
            f"{user.full_name} tiene historial en el sistema ({', '.join(rastro)}). "
            "Borrarlo dejaría esos registros sin responsable. Desactívalo en su lugar: "
            "pierde el acceso de inmediato y la trazabilidad se conserva."
        )

    # La unidad de servicio que lo tuviera como ingeniero por defecto quedaría
    # sin asignación automática y en silencio; mejor dejarlo explícito.
    from app.modules.sectors.models import Sector

    for sector in (
        (await db.execute(select(Sector).where(Sector.default_engineer_id == user_id)))
        .scalars()
        .all()
    ):
        sector.default_engineer_id = None

    # La hoja de vida lleva datos personales: se va con el usuario. Si Storage
    # falla, el borrado continúa (el archivo quedaría huérfano, no al revés).
    if user.cv_path:
        with contextlib.suppress(Exception):
            sb.delete_file(user.cv_path)

    # Auth primero: mientras la fila siga viva esto se puede reintentar. Al
    # revés no — la cuenta quedaría viva bloqueando el email para siempre.
    _auth_admin().auth.admin.delete_user(str(user.id))

    await db.delete(user)
    await db.flush()


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
