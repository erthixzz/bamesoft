"""Aplica las migraciones SQL nuevas (DDL aditiva) contra la BD configurada.

Ejecuta solo los archivos indicados por argumento, vía asyncpg (protocolo de
consulta simple, admite múltiples sentencias). NO corre el seed.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import asyncpg

from app.core.config import settings

MIG_DIR = Path(__file__).resolve().parents[2] / "infra" / "supabase" / "migrations"


def _dsn() -> str:
    return settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


async def main(files: list[str]) -> None:
    conn = await asyncpg.connect(_dsn())
    try:
        for fname in files:
            sql = (MIG_DIR / fname).read_text(encoding="utf-8")
            print(f"[..] Aplicando {fname}")
            await conn.execute(sql)
            print(f"[OK] {fname} aplicado")
    finally:
        await conn.close()


if __name__ == "__main__":
    targets = sys.argv[1:] or ["0005_case_service.sql", "0006_equipment_sector.sql"]
    asyncio.run(main(targets))
