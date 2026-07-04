"""Mide el tiempo de la búsqueda global (consulta única UNION ALL) contra la BD.

Uso:  .venv/Scripts/python.exe scripts/bench_search.py [término]
Imprime el tiempo de 5 ejecuciones (la primera incluye conexión/plan).
"""
from __future__ import annotations

import asyncio
import sys
import time

import app.db.registry  # noqa: F401  (registra modelos)
from app.db.session import AsyncSessionLocal
from app.modules.search.routes import _PER_TYPE, _SEARCH_SQL


async def main(term: str) -> None:
    params = {
        "scope": None,  # super admin (peor caso: busca en todas las clínicas)
        "like": f"%{term}%",
        "prefix": f"{term}%",
        "per": _PER_TYPE,
        "inc_users": True,
        "inc_clinics": True,
    }
    async with AsyncSessionLocal() as db:
        for i in range(5):
            t0 = time.perf_counter()
            rows = (await db.execute(_SEARCH_SQL, params)).all()
            ms = (time.perf_counter() - t0) * 1000
            print(f"  intento {i + 1}: {ms:7.1f} ms  ({len(rows)} resultados)")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "des"))
