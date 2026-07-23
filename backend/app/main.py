"""FastAPI application factory."""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.audit_middleware import AuditMiddleware
from app.core.config import settings
from app.core.error_middleware import CatchAllErrorMiddleware
from app.core.logging import configure_logging
from app.db.session import dispose_engine


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    yield
    await dispose_engine()


def create_app() -> FastAPI:
    app = FastAPI(
        title=f"{settings.APP_NAME} API",
        version=settings.APP_VERSION,
        debug=settings.APP_DEBUG,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # El orden importa: `add_middleware` inserta al frente, así que el ÚLTIMO
    # añadido queda más externo. Queremos CORS como el más EXTERNO para que
    # incluso las respuestas de error lleven cabeceras CORS.
    # Ejecución (externo→interno): CORS → Auditoría → CatchAll → rutas.

    # Convierte cualquier excepción no controlada en un 500 JSON (dentro de CORS).
    app.add_middleware(CatchAllErrorMiddleware)

    # Bitácora de auditoría (registra mutaciones exitosas con su actor).
    app.add_middleware(AuditMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        # Previews y ramas: https://<proyecto>-<hash>-<team>.vercel.app
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health", tags=["meta"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.APP_NAME, "version": settings.APP_VERSION}

    return app


app = create_app()
