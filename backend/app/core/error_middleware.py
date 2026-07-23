"""Middleware que convierte errores no controlados en una respuesta JSON 500.

Se coloca DENTRO de `CORSMiddleware` (CORS es el más externo) para que la
respuesta de error pase de vuelta por CORS y lleve sus cabeceras. Sin esto, una
excepción no controlada la maneja el `ServerErrorMiddleware` de Starlette (el más
externo, por encima de CORS) y el 500 sale SIN `Access-Control-Allow-Origin`, lo
que el navegador reporta como un opaco "Failed to fetch" en vez del error real.
"""
from __future__ import annotations

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class CatchAllErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception:  # cualquier fallo no controlado
            logger.exception("Error no controlado en {} {}", request.method, request.url.path)
            return JSONResponse(
                status_code=500,
                content={"detail": "Error interno del servidor. Revisa los registros."},
            )
