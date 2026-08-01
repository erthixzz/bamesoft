"""Application settings loaded from env."""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_NAME: str = "Bamesoft"
    APP_ENV: str = "development"
    # Por defecto FALSE: un despliegue al que se le olvide la variable arranca
    # seguro (sin trazas ni /docs), no al revés.
    APP_DEBUG: bool = False
    APP_VERSION: str = "0.1.0"

    # URL pública del frontend (a la que apunta el QR de cada equipo).
    PUBLIC_APP_URL: str = "http://localhost:5173"

    # DB
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/bamesoft"
    )

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    # Auth
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"
    # Regex opcional para previews (p. ej. r"https://bamesoft-[a-z0-9-]+\.vercel\.app").
    # Vacío = sin comodín. NO uses r"https://.*\.vercel\.app": eso acepta el
    # proyecto Vercel de cualquier persona, no solo los tuyos.
    CORS_ORIGIN_REGEX: str = ""

    # Storage
    STORAGE_BUCKET: str = "bamesoft"

    # Docs interactivas (/docs, /redoc, /openapi.json). Útiles en desarrollo;
    # en producción se apagan siempre (ver `docs_enabled`).
    ENABLE_DOCS: bool = True

    # Rate limiting (ventana de 60 s por IP + usuario). 0 = desactivado.
    RATE_LIMIT_PER_MINUTE: int = 120
    RATE_LIMIT_WRITES_PER_MINUTE: int = 40

    # Logs
    LOG_LEVEL: str = "INFO"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.strip().lower() in {"production", "prod"}

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def docs_enabled(self) -> bool:
        """En producción nunca, aunque la variable diga lo contrario."""
        return self.ENABLE_DOCS and not self.is_production


def check_production_readiness(s: Settings) -> list[str]:
    """Problemas de configuración que NO deben llegar a producción.

    Se ejecuta al arrancar (`app.main.lifespan`) y aborta el proceso si hay
    alguno: es preferible que el despliegue falle a que quede abierto.
    """
    problems: list[str] = []
    if not s.is_production:
        return problems

    if s.APP_DEBUG:
        problems.append("APP_DEBUG=true en producción (expone trazas de error).")
    if not s.SUPABASE_JWT_SECRET and not s.SUPABASE_URL:
        problems.append(
            "Sin SUPABASE_JWT_SECRET ni SUPABASE_URL: no hay forma de validar tokens."
        )
    if not s.SUPABASE_SERVICE_KEY:
        problems.append("Sin SUPABASE_SERVICE_KEY: Storage y alta de usuarios no funcionan.")
    if not s.cors_origins_list and not s.CORS_ORIGIN_REGEX:
        problems.append("CORS_ORIGINS vacío: el frontend no podrá llamar a la API.")
    if any(o.strip() == "*" for o in s.cors_origins_list):
        problems.append("CORS_ORIGINS contiene '*': incompatible con credenciales.")
    if "localhost" in s.CORS_ORIGINS:
        problems.append("CORS_ORIGINS incluye localhost en producción.")
    if s.PUBLIC_APP_URL.startswith("http://"):
        problems.append("PUBLIC_APP_URL no usa HTTPS (va dentro de los QR).")
    return problems


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
