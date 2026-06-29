"""Limpia los equipos/casos de prueba de la clínica demo y aplica el seed.

Deja el escenario exacto: 3 unidades de servicio (UCI, Hospitalización, Rayos X)
y 9 equipos (anestesia/desfibrilador/rayos X por área).
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import asyncpg

from app.core.config import settings

DEMO_CLINIC = "11111111-1111-1111-1111-111111111111"
SEED = Path(__file__).resolve().parents[2] / "infra" / "supabase" / "seed.sql"


def _dsn() -> str:
    return settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


async def main() -> None:
    conn = await asyncpg.connect(_dsn())
    try:
        eq = await conn.fetchval("select count(*) from equipment where clinic_id=$1", DEMO_CLINIC)
        ca = await conn.fetchval(
            "select count(*) from cases c join equipment e on e.id=c.equipment_id "
            "where e.clinic_id=$1",
            DEMO_CLINIC,
        )
        print(f"[antes] equipos={eq} casos(de esos equipos)={ca}")

        print("[..] Borrando equipos de prueba de la clínica demo (cascada a casos)")
        await conn.execute("delete from equipment where clinic_id=$1", DEMO_CLINIC)

        print("[..] Aplicando seed.sql")
        await conn.execute(SEED.read_text(encoding="utf-8"))

        print("[OK] Seed aplicado. Estado final:")
        for r in await conn.fetch(
            "select s.code, s.name, count(e.id) as n "
            "from sectors s left join equipment e on e.sector_id=s.id "
            "where s.clinic_id=$1 group by s.id order by s.code",
            DEMO_CLINIC,
        ):
            print(f"  sector {r['code']:5} | {r['name']:18} | equipos={r['n']}")
        total_eq = await conn.fetchval("select count(*) from equipment")
        total_ca = await conn.fetchval("select count(*) from cases")
        total_se = await conn.fetchval("select count(*) from sectors")
        print(f"  TOTAL equipos={total_eq} casos={total_ca} sectores={total_se}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
