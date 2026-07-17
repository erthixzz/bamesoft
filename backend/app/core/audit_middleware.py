"""Middleware que registra en la bitácora cada acción de mutación exitosa.

Captura automáticamente POST/PUT/PATCH/DELETE sobre /api/v1 (excepto auth y la
propia bitácora), identificando al actor por su token. Nunca rompe la petición:
cualquier fallo al auditar se ignora silenciosamente.
"""
from __future__ import annotations

import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.security import TokenError, decode_token
from app.db.session import AsyncSessionLocal
from app.modules.audit import service
from app.modules.audit.describe import describe
from app.modules.users.models import User

_MUTATING = {"POST", "PUT", "PATCH", "DELETE"}
_SKIP_PREFIXES = ("/api/v1/audit", "/api/v1/auth")


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        try:
            await self._maybe_log(request, response.status_code)
        except Exception:  # la auditoría jamás debe afectar la respuesta
            pass
        return response

    async def _maybe_log(self, request: Request, status_code: int) -> None:
        if request.method not in _MUTATING:
            return
        path = request.url.path
        if not path.startswith("/api/v1/") or any(path.startswith(p) for p in _SKIP_PREFIXES):
            return
        if status_code >= 400:
            return

        auth = request.headers.get("authorization")
        if not auth or not auth.lower().startswith("bearer "):
            return
        try:
            claims = decode_token(auth.split(" ", 1)[1].strip())
        except TokenError:
            return

        sub = claims.get("sub")
        try:
            actor_id = uuid.UUID(sub) if sub else None
        except (ValueError, TypeError):
            actor_id = None

        entity, action, entity_id = describe(request.method, path)

        async with AsyncSessionLocal() as db:
            actor_name = claims.get("email")
            actor_role = None
            clinic_id = None
            if actor_id is not None:
                user = await db.get(User, actor_id)
                if user is not None:
                    actor_name = user.full_name
                    actor_role = user.role.value
                    clinic_id = user.clinic_id
            await service.record(
                db,
                actor_id=actor_id,
                actor_name=actor_name,
                actor_role=actor_role,
                clinic_id=clinic_id,
                method=request.method,
                action=action,
                entity=entity,
                entity_id=entity_id,
                path=path,
                status_code=status_code,
            )
            await db.commit()
