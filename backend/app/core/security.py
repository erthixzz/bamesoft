"""JWT decoding/encoding (compatible con Supabase Auth: legacy HS256 + JWKS).

Supabase emite tokens firmados con:
- HS256 (legacy JWT secret) — proyectos viejos o clientes anon/service.
- ES256/RS256 (JWT Signing Keys) — proyectos nuevos, sesiones de usuario.

Probamos primero con el secreto compartido y, si falla, caemos al JWKS público.
"""
from __future__ import annotations

import time
from typing import Any

import httpx
from jose import JWTError, jwt

from app.core.config import settings


class TokenError(Exception):
    """Raised when a token cannot be validated."""


# Este módulo solo VERIFICA tokens; no los emite. Los emite Supabase Auth
# (GoTrue) y el login del backend es un proxy a su endpoint (`auth/service.py`).


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


def _check_claims(claims: dict[str, Any]) -> dict[str, Any]:
    """Valida emisor y audiencia *si el token los trae*.

    La firma ya se verificó, así que un atacante no puede alterar estos campos;
    el objetivo es rechazar tokens legítimos de OTRO proyecto o de otro público
    (p. ej. una anon key usada como Bearer). Se validan solo cuando están
    presentes para no romper tokens legacy que no los incluyen.
    """
    issuer = claims.get("iss")
    if issuer and settings.SUPABASE_URL:
        expected = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1"
        if issuer != expected:
            raise TokenError(f"Emisor no esperado: {issuer}")

    audience = claims.get("aud")
    if audience:
        allowed = {"authenticated"}
        got = set(audience) if isinstance(audience, list) else {audience}
        if not (got & allowed):
            raise TokenError(f"Audiencia no esperada: {audience}")

    return claims


def decode_token(token: str) -> dict[str, Any]:
    """Verifica un JWT contra el secreto legacy y, si falla, contra JWKS."""
    legacy_msg = "sin SUPABASE_JWT_SECRET configurado"

    # 1) Intento HS256 con el legacy secret. Sin secreto no se intenta: antes
    #    había un fallback a "dev-insecure-secret" que en un entorno mal
    #    configurado habría aceptado tokens firmados con esa cadena pública.
    if settings.SUPABASE_JWT_SECRET:
        try:
            return _check_claims(
                jwt.decode(
                    token,
                    settings.SUPABASE_JWT_SECRET,
                    algorithms=[settings.JWT_ALGORITHM],
                    options={"verify_aud": False},  # la audiencia la revisa _check_claims
                )
            )
        except JWTError as legacy_exc:
            legacy_msg = str(legacy_exc)

    # 2) Intento JWKS (ES256 / RS256 firmados por Supabase Auth nuevos).
    try:
        return _check_claims(_decode_with_jwks(token))
    except (JWTError, TokenError) as jwks_exc:
        raise TokenError(
            f"Legacy: {legacy_msg} · JWKS: {jwks_exc}"
        ) from jwks_exc
