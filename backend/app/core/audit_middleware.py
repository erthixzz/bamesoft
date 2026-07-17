"""Middleware que registra en la bitácora cada acción de mutación exitosa.

Captura automáticamente POST/PUT/PATCH/DELETE sobre /api/v1 (excepto auth y la
propia bitácora), identificando al actor por su token y resumiendo qué cambió.
Nunca rompe la petición: cualquier fallo al auditar se ignora silenciosamente.
"""
from __future__ import annotations

import json
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.security import TokenError, decode_token
from app.db.session import AsyncSessionLocal
from app.modules.audit import service
from app.modules.audit.describe import describe, summarize_case
from app.modules.cases.models import Case
from app.modules.users.models import User

_MUTATING = {"POST", "PUT", "PATCH", "DELETE"}
_SKIP_PREFIXES = ("/api/v1/audit", "/api/v1/auth")


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Capturamos el cuerpo JSON (solo mutaciones) y lo re-inyectamos para que
        # la ruta lo pueda leer normalmente.
        body_bytes = b""
        ct = request.headers.get("content-type", "")
        if (
            request.method in _MUTATING
            and request.url.path.startswith("/api/v1/")
            and "application/json" in ct
        ):
            try:
                body_bytes = await request.body()

                async def receive():
                    return {"type": "http.request", "body": body_bytes, "more_body": False}

                request._receive = receive  # type: ignore[attr-defined]
            except Exception:
                body_bytes = b""

        response = await call_next(request)
        try:
            await self._maybe_log(request, response.status_code, body_bytes)
        except Exception:  # la auditoría jamás debe afectar la respuesta
            pass
        return response

    async def _maybe_log(self, request: Request, status_code: int, body_bytes: bytes) -> None:
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

        payload: dict = {}
        if body_bytes:
            try:
                parsed = json.loads(body_bytes)
                if isinstance(parsed, dict):
                    payload = parsed
            except Exception:
                payload = {}

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

            detail = await self._detail(db, entity, request.method, payload, entity_id)

            await service.record(
                db,
                actor_id=actor_id,
                actor_name=actor_name,
                actor_role=actor_role,
                clinic_id=clinic_id,
                method=request.method,
                action=action,
                detail=detail,
                entity=entity,
                entity_id=entity_id,
                path=path,
                status_code=status_code,
            )
            await db.commit()

    async def _detail(
        self, db, entity: str, method: str, body: dict, entity_id: str | None
    ) -> str | None:
        """Resumen legible de lo que cambió (resuelve código de caso e ingeniero)."""
        if entity != "cases":
            return None

        parts = summarize_case(body)

        # Asignación (resuelve el nombre del ingeniero).
        if "assigned_to" in body:
            target = body["assigned_to"]
            if target:
                try:
                    eng = await db.get(User, uuid.UUID(str(target)))
                    parts.append(f"asignado a {eng.full_name}" if eng else "asignado")
                except (ValueError, TypeError):
                    parts.append("asignado")
            else:
                parts.append("sin asignar")

        # Título del caso nuevo (POST sin id todavía).
        if method == "POST" and body.get("title"):
            parts.insert(0, f"«{body['title']}»")

        # Prefijo con el código del caso si lo conocemos.
        code = None
        if entity_id:
            try:
                case = await db.get(Case, uuid.UUID(entity_id))
                code = case.code if case else None
            except (ValueError, TypeError):
                code = None

        if not parts and not code:
            return None
        text = " · ".join(parts) if parts else "actualización"
        return f"{code} · {text}" if code else text
