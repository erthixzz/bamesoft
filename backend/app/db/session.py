"""Async engine and session factory."""
from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    # Pool optimizado para Supabase Pooler remoto:
    # - sin pre_ping (ahorra 1 roundtrip por request a la DB)
    # - pool grande para no esperar por conexiones disponibles
    # - reciclado generoso para reutilizar conexiones
    pool_pre_ping=False,
    pool_size=20,
    max_overflow=10,
    pool_recycle=1800,
    pool_timeout=10,
    connect_args={
        # PgBouncer no soporta prepared statements persistentes:
        # evita "connection was closed in the middle of operation".
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    },
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: yield a transactional session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def dispose_engine() -> None:
    await engine.dispose()
