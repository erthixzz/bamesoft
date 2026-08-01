"""FastAPI application factory."""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.audit_middleware import AuditMiddleware
from app.core.config import check_production_readiness, settings
from app.core.error_middleware import CatchAllErrorMiddleware
from app.core.logging import configure_logging
from app.core.rate_limit import RateLimitMiddleware
from app.core.security_headers import SecurityHeadersMiddleware
from app.db.session import dispose_engine


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging()

    # Puerta de despliegue: si la configuración de producción está mal, es mejor
    # que el arranque falle a que la API quede expuesta.
    problems = check_production_readiness(settings)
    if problems:
        detail = "\n  - ".join(problems)
        raise RuntimeError(f"Configuración de producción inválida:\n  - {detail}")

    yield
    await dispose_engine()


def create_app() -> FastAPI:
    docs_on = settings.docs_enabled
    app = FastAPI(
        title=f"{settings.APP_NAME} API",
        version=settings.APP_VERSION,
        debug=settings.APP_DEBUG,
        lifespan=lifespan,
        # En producción no se publica el catálogo de endpoints: no es un secreto,
        # pero le ahorra el mapa a quien esté buscando por dónde entrar.
        docs_url="/docs" if docs_on else None,
        redoc_url="/redoc" if docs_on else None,
        openapi_url="/openapi.json" if docs_on else None,
    )

    # El orden importa: `add_middleware` inserta al frente, así que el ÚLTIMO
    # añadido queda más externo. Queremos CORS como el más EXTERNO para que
    # incluso las respuestas de error lleven cabeceras CORS.
    # Ejecución (externo→interno): CORS → Headers → Auditoría → CatchAll → rutas.

    # Convierte cualquier excepción no controlada en un 500 JSON (dentro de CORS).
    app.add_middleware(CatchAllErrorMiddleware)

    # Bitácora de auditoría (registra mutaciones exitosas con su actor).
    app.add_middleware(AuditMiddleware)

    # Cabeceras de seguridad en toda respuesta (incluidos los errores).
    app.add_middleware(SecurityHeadersMiddleware)

    # Rate limiting: lo más externo posible (después de CORS) para que una
    # avalancha no llegue a tocar la base de datos.
    app.add_middleware(RateLimitMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        # Previews de Vercel: se configura por entorno (CORS_ORIGIN_REGEX) y
        # acotado al propio proyecto. El comodín `https://.*\.vercel\.app` que
        # había aquí aceptaba el despliegue de CUALQUIER usuario de Vercel.
        allow_origin_regex=settings.CORS_ORIGIN_REGEX or None,
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
