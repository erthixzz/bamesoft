"""Cabeceras de seguridad en todas las respuestas de la API.

La API devuelve JSON, así que la CSP es deliberadamente mínima (`default-src
'none'`): un navegador no debería cargar recurso alguno desde una respuesta de
la API. Las excepciones son `/docs` y `/redoc`, que sí son HTML y cargan Swagger
desde un CDN; por eso se saltan la CSP (y en producción están apagadas).

Ojo: estas cabeceras protegen la API. El frontend en Vercel necesita las suyas
(ver `frontend/vercel.json`) — son dos superficies distintas.
"""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import settings

# Rutas HTML que necesitan cargar assets externos (Swagger/ReDoc desde CDN).
_HTML_DOC_PATHS = ("/docs", "/redoc")

_BASE_HEADERS = {
    # Nunca dejes que el navegador adivine el tipo de contenido (evita que un
    # archivo subido se interprete como HTML/JS).
    "X-Content-Type-Options": "nosniff",
    # La API no debe embeberse en un iframe.
    "X-Frame-Options": "DENY",
    # No filtres la URL completa (puede llevar ids) a terceros.
    "Referrer-Policy": "strict-origin-when-cross-origin",
    # La API no necesita ninguna capacidad del navegador.
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
    # Respuestas con datos de clínica: fuera de cachés compartidas.
    "Cache-Control": "no-store",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        for header, value in _BASE_HEADERS.items():
            response.headers.setdefault(header, value)

        # HSTS solo tiene sentido sobre HTTPS y solo en producción: en local
        # forzaría https://localhost y rompería el desarrollo.
        if settings.is_production:
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )

        if not request.url.path.startswith(_HTML_DOC_PATHS):
            response.headers.setdefault(
                "Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'"
            )

        return response
