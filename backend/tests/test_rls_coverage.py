"""Gate de seguridad: toda tabla de `public` debe tener RLS activada.

Supabase expone el esquema `public` vía PostgREST usando la anon key, que viaja
en el bundle del frontend. Una tabla sin RLS ahí es legible (y escribible) desde
internet sin pasar nunca por FastAPI ni por `require_*`. Este test convierte el
linter de Supabase —que avisa cuando el hueco YA está en producción— en una
barrera antes del merge.

Es análisis estático de `infra/supabase/migrations/*.sql`: no necesita base de
datos, corre en el CI actual. Para detectar deriva del esquema real (tablas
creadas a mano en Studio, que nunca pasaron por una migración) usa
`infra/supabase/check_rls.sql`.
"""
from __future__ import annotations

import re
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "infra" / "supabase" / "migrations"

# Tablas que legítimamente viven sin RLS. Añadir una aquí exige justificar por
# qué es seguro que PostgREST la exponga a cualquiera con la anon key; por
# defecto la respuesta es "no lo es".
RLS_EXEMPT: dict[str, str] = {}

_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)
_LINE_COMMENT = re.compile(r"--[^\n]*")
_CREATE_TABLE = re.compile(r"\bcreate\s+table\s+(?:if\s+not\s+exists\s+)?([\w.\"]+)", re.I)
_ENABLE_RLS = re.compile(
    r"\balter\s+table\s+(?:only\s+)?([\w.\"]+)\s+enable\s+row\s+level\s+security", re.I
)
_FORCE_RLS = re.compile(
    r"\balter\s+table\s+(?:only\s+)?([\w.\"]+)\s+force\s+row\s+level\s+security", re.I
)


def _normalize(name: str) -> str:
    """`public."Equipment"` -> `equipment`."""
    return name.replace('"', "").rsplit(".", 1)[-1].lower()


def _migrations_sql() -> str:
    """Todas las migraciones concatenadas, sin comentarios."""
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    assert files, f"No se encontraron migraciones en {MIGRATIONS_DIR}"
    joined = "\n".join(f.read_text(encoding="utf-8") for f in files)
    return _LINE_COMMENT.sub("", _BLOCK_COMMENT.sub("", joined))


def test_parser_ve_el_esquema() -> None:
    """Guarda del guarda: un regex que deja de matchear haría pasar el gate en
    vacío, que es peor que no tenerlo. Si este test falla, arregla el parser
    antes de creerle al de abajo."""
    created = {_normalize(t) for t in _CREATE_TABLE.findall(_migrations_sql())}
    assert {"equipment", "cases", "audit_logs", "role_permissions"} <= created
    assert len(created) >= 18, f"Solo se detectaron {len(created)} tablas: {sorted(created)}"


def test_toda_tabla_publica_tiene_rls() -> None:
    sql = _migrations_sql()
    created = {_normalize(t) for t in _CREATE_TABLE.findall(sql)}
    protected = {_normalize(t) for t in _ENABLE_RLS.findall(sql)}

    missing = sorted(created - protected - set(RLS_EXEMPT))
    assert not missing, (
        f"Tablas en `public` sin RLS: {', '.join(missing)}.\n"
        "PostgREST las expone con la anon key del frontend. Añade a tu migración:\n"
        + "\n".join(
            f"  alter table {t} enable row level security;\n"
            f"  revoke all on table {t} from anon, authenticated;"
            for t in missing
        )
    )


def test_ninguna_tabla_usa_force_rls() -> None:
    """`force row level security` rompería la app: el backend se conecta como
    owner de las tablas y en Postgres el owner omite RLS — salvo con `force`,
    que lo dejaría sin acceso."""
    forced = sorted({_normalize(t) for t in _FORCE_RLS.findall(_migrations_sql())})
    assert not forced, (
        f"`force row level security` en: {', '.join(forced)}. "
        "El backend perdería acceso a esas tablas (se conecta como owner)."
    )
