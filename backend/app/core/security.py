"""JWT decoding/encoding (compatible con Supabase Auth: legacy HS256 + JWKS).

Supabase emite tokens firmados con:
- HS256 (legacy JWT secret) — proyectos viejos o clientes anon/service.
- ES256/RS256 (JWT Signing Keys) — proyectos nuevos, sesiones de usuario.

Probamos primero con el secreto compartido y, si falla, caemos al JWKS público.
"""
from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from jose import JWTError, jwt

from app.core.config import settings


class TokenError(Exception):
    """Raised when a token cannot be validated."""


# ---- HS256 (creación local + verificación legacy) ---------------------------
def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, Any] = {"sub": subject, "exp": expire, **(extra or {})}
    return jwt.encode(
        payload,
        settings.SUPABASE_JWT_SECRET or "dev-insecure-secret",
        algorithm=settings.JWT_ALGORITHM,
    )


# ---- JWKS cache -------------------------------------------------------------
_jwks_cache: dict[str, Any] = {"keys": None, "expires": 0.0}
_JWKS_TTL_SECONDS = 5 * 60


def _fetch_jwks() -> dict[str, Any]:
    """Descarga (y cachea) las JWK públicas de Supabase Auth."""
    now = time.time()
    if _jwks_cache["keys"] and _jwks_cache["expires"] > now:
        return _jwks_cache["keys"]

    if not settings.SUPABASE_URL:
        raise TokenError("SUPABASE_URL no configurado para JWKS")

    url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
    try:
        r = httpx.get(url, timeout=5.0)
        r.raise_for_status()
    except httpx.HTTPError as exc:
        raise TokenError(f"No se pudo descargar JWKS: {exc}") from exc

    data = r.json()
    _jwks_cache["keys"] = data
    _jwks_cache["expires"] = now + _JWKS_TTL_SECONDS
    return data


def _decode_with_jwks(token: str) -> dict[str, Any]:
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    alg = header.get("alg") or "ES256"
    if not kid:
        raise TokenError("Token sin 'kid' en el header")

    jwks = _fetch_jwks()
    matching = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
    if matching is None:
        # JWKS pudo haber rotado; refresca y reintenta una vez.
        _jwks_cache["expires"] = 0
        jwks = _fetch_jwks()
        matching = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
    if matching is None:
        raise TokenError(f"No hay JWK con kid={kid}")

    return jwt.decode(
        token,
        matching,
        algorithms=[alg],
        options={"verify_aud": False},
    )


def decode_token(token: str) -> dict[str, Any]:
    """Verifica un JWT contra el secreto legacy y, si falla, contra JWKS."""
    secret = settings.SUPABASE_JWT_SECRET or "dev-insecure-secret"

    # 1) Intento HS256 con el legacy secret.
    try:
        return jwt.decode(
            token,
            secret,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False},
        )
    except JWTError as legacy_exc:
        legacy_msg = str(legacy_exc)

    # 2) Intento JWKS (ES256 / RS256 firmados por Supabase Auth nuevos).
    try:
        return _decode_with_jwks(token)
    except (JWTError, TokenError) as jwks_exc:
        raise TokenError(
            f"Legacy: {legacy_msg} · JWKS: {jwks_exc}"
        ) from jwks_exc
