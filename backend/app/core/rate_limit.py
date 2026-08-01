"""Rate limiting por ventana fija, en memoria del proceso.

Objetivo: frenar enumeración de recursos (probar ids de otra clínica en bucle),
fuerza bruta contra `/auth/login` y abuso accidental de la API. No pretende
parar un ataque distribuido — para eso hace falta un WAF por delante.

**Limitación importante**: el contador vive en la memoria del proceso. Con
varias instancias en Render, cada una lleva su propia cuenta y el límite
efectivo se multiplica por el número de instancias. Para un límite exacto habría
que mover el contador a Redis. Como control anti-abuso básico es suficiente, y
no añade una dependencia de infraestructura nueva.
"""
from __future__ import annotations

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import settings

_WINDOW_SECONDS = 60
_MUTATING = {"POST", "PUT", "PATCH", "DELETE"}

# Rutas exentas: el health check lo golpea el monitor de Render constantemente.
_EXEMPT_PATHS = ("/health",)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Ventana fija de 60 s por cliente, con un cupo aparte para mutaciones."""

    def __init__(self, app) -> None:
        super().__init__(app)
        # clave -> (inicio_de_ventana, nº de peticiones)
        self._reads: dict[str, tuple[float, int]] = defaultdict(lambda: (0.0, 0))
        self._writes: dict[str, tuple[float, int]] = defaultdict(lambda: (0.0, 0))

    @staticmethod
    def _client_key(request: Request) -> str:
        """Identifica al cliente. Detrás de Render/Vercel la IP real viene en
        `X-Forwarded-For` (primer valor); `request.client` sería la del proxy.

        Se añade un prefijo del token para que varios usuarios tras la misma IP
        (una clínica con NAT) no compartan cupo. Es un prefijo, no el token
        entero: no queremos credenciales completas como clave en memoria.
        """
        forwarded = request.headers.get("x-forwarded-for", "")
        ip = forwarded.split(",")[0].strip() if forwarded else (
            request.client.host if request.client else "desconocido"
        )
        auth = request.headers.get("authorization", "")
        token_hint = auth[-16:] if len(auth) > 16 else ""
        return f"{ip}|{token_hint}"

    def _over_limit(
        self, bucket: dict[str, tuple[float, int]], key: str, limit: int, now: float
    ) -> bool:
        if limit <= 0:  # 0 = desactivado
            return False
        window_start, count = bucket[key]
        if now - window_start >= _WINDOW_SECONDS:
            bucket[key] = (now, 1)  # ventana nueva
            return False
        if count >= limit:
            return True
        bucket[key] = (window_start, count + 1)
        return False

    def _prune(self, now: float) -> None:
        """Evita que el diccionario crezca sin fin con claves viejas."""
        for bucket in (self._reads, self._writes):
            if len(bucket) < 10_000:
                continue
            stale = [k for k, (start, _) in bucket.items() if now - start >= _WINDOW_SECONDS]
            for k in stale:
                del bucket[k]

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith(_EXEMPT_PATHS):
            return await call_next(request)

        now = time.monotonic()
        self._prune(now)
        key = self._client_key(request)

        limited = self._over_limit(
            self._reads, key, settings.RATE_LIMIT_PER_MINUTE, now
        )
        if not limited and request.method in _MUTATING:
            limited = self._over_limit(
                self._writes, key, settings.RATE_LIMIT_WRITES_PER_MINUTE, now
            )

        if limited:
            return JSONResponse(
                status_code=429,
                content={"detail": "Demasiadas peticiones. Espera un momento."},
                headers={"Retry-After": str(_WINDOW_SECONDS)},
            )

        return await call_next(request)
