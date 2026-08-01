"""Infraestructura para tests de integración contra Postgres real.

Se necesita una BD de verdad porque el esquema usa tipos propios de Postgres
(UUID, enums nativos) y porque el aislamiento por clínica se decide en SQL: un
mock no probaría nada.

La BD sale de `TEST_DATABASE_URL`; si no está definida, los tests que dependen
de ella se saltan (`pytest.skip`) en vez de fallar, para no romper el CI de
quien no tenga Postgres a mano.

Levantar una desechable en local:

    docker run -d --name bamesoft-test-db -e POSTGRES_PASSWORD=postgres \\
      -e POSTGRES_DB=bamesoft_test -p 55432:5432 postgres:16-alpine

    TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:55432/bamesoft_test

El esquema se crea con `Base.metadata.create_all` (desde los modelos), no con
las migraciones SQL: esas usan `auth.uid()` de Supabase y no corren en un
Postgres normal.
"""
from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db import registry  # noqa: F401 — registra todos los modelos en Base.metadata
from app.db.base import Base
from app.db.enums import EquipmentStatus, UserRole
from app.modules.access.models import RolePermission
from app.modules.clinics.models import Clinic
from app.modules.equipment.models import Equipment
from app.modules.users.models import User

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "")

# Donde el aislamiento DEBE comprobarse (el job `security-gates`), un skip
# dejaría el pipeline verde sin haber probado nada — el peor resultado posible.
# Ese job declara `REQUIRE_TEST_DB=1` y aquí convertimos el skip en error.
#
# No se usa la variable `CI` para esto: GitHub la define en TODOS los jobs, y el
# job `test` corre sin Postqres a propósito (sus pruebas no lo necesitan). Atarlo
# a `CI` hacía fallar ese job por una base de datos que nunca debió pedir.
_REQUIRE_DB = os.getenv("REQUIRE_TEST_DB", "").lower() in {"1", "true", "yes"}

if _REQUIRE_DB and not TEST_DATABASE_URL:
    raise RuntimeError(
        "REQUIRE_TEST_DB está activo pero falta TEST_DATABASE_URL: los tests de "
        "aislamiento multi-clínica no pueden saltarse en este job."
    )

requires_db = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="Define TEST_DATABASE_URL para correr los tests de integración",
)

# Matriz de capacidades igual a la que siembra `0007_access_control.sql`.
ROLE_CAPS: dict[str, list[str]] = {
    "admin": [
        "report", "work", "close", "equipment", "sectors", "docs",
        "standards", "reports", "users", "clinics", "access", "dashboard", "audit",
    ],
    "clinic_admin": [
        "report", "work", "close", "equipment", "sectors", "docs",
        "standards", "reports", "users", "dashboard",
    ],
    "engineer": [
        "report", "work", "close", "equipment", "sectors", "docs",
        "standards", "reports", "dashboard",
    ],
    "support": ["report", "docs", "reports", "dashboard"],
    "service": ["report", "docs"],
    "client": ["report"],
}


class Tenant:
    """Una clínica con su equipo y sus usuarios, para probar el aislamiento."""

    def __init__(self, clinic: Clinic, equipment: Equipment, users: dict[str, User]) -> None:
        self.clinic = clinic
        self.equipment = equipment
        self.users = users

    def user(self, role: str) -> User:
        return self.users[role]


async def _seed_tenant(session: AsyncSession, slug: str) -> Tenant:
    clinic = Clinic(name=f"Clínica {slug}", tax_id=f"NIT-{slug}")
    session.add(clinic)
    await session.flush()

    equipment = Equipment(
        code=f"EQ-{slug}",
        qr_token=f"token-{slug}",
        name=f"Equipo {slug}",
        status=EquipmentStatus.OPERATIONAL,
        clinic_id=clinic.id,
    )
    session.add(equipment)

    users: dict[str, User] = {}
    for role in ("clinic_admin", "engineer", "client"):
        u = User(
            id=uuid.uuid4(),
            email=f"{role}@clinica-{slug}.com",
            full_name=f"{role} {slug}",
            role=UserRole(role),
            clinic_id=clinic.id,
        )
        session.add(u)
        users[role] = u

    await session.flush()
    return Tenant(clinic, equipment, users)


@pytest.fixture(scope="session")
def db_url() -> str:
    if not TEST_DATABASE_URL:
        pytest.skip("Sin TEST_DATABASE_URL")
    return TEST_DATABASE_URL


def _pg_enum_types() -> list[PgEnum]:
    """Tipos enum nativos usados por los modelos, sin repetir.

    `app.db.types.pg_enum` los declara con `create_type=False` porque en
    producción los crean las migraciones SQL. Aquí construimos el esquema desde
    los modelos, así que hay que crearlos a mano antes de `create_all`.
    """
    seen: dict[str, PgEnum] = {}
    for table in Base.metadata.tables.values():
        for column in table.columns:
            if isinstance(column.type, PgEnum) and column.type.name:
                seen.setdefault(column.type.name, column.type)
    return list(seen.values())


def _build_schema(conn) -> None:
    for enum_type in _pg_enum_types():
        enum_type.create(conn, checkfirst=True)
    Base.metadata.create_all(conn)


def _drop_schema(conn) -> None:
    Base.metadata.drop_all(conn)
    for enum_type in _pg_enum_types():
        enum_type.drop(conn, checkfirst=True)


@pytest.fixture
async def db_engine(db_url: str):
    engine = create_async_engine(db_url, poolclass=None)
    async with engine.begin() as conn:
        await conn.run_sync(_drop_schema)
        await conn.run_sync(_build_schema)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(_drop_schema)
    await engine.dispose()


@pytest.fixture
async def db_sessionmaker(db_engine):
    return async_sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture
async def tenants(db_sessionmaker) -> tuple[Tenant, Tenant]:
    """Dos clínicas independientes: A y B."""
    async with db_sessionmaker() as s:
        for role, caps in ROLE_CAPS.items():
            for cap in caps:
                s.add(RolePermission(role=role, capability=cap, enabled=True))
        a = await _seed_tenant(s, "a")
        b = await _seed_tenant(s, "b")
        await s.commit()
        return a, b
