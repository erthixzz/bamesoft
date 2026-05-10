"""Helpers de tipos SQLAlchemy."""
from __future__ import annotations

from enum import Enum
from typing import Any

from sqlalchemy.dialects.postgresql import ENUM as PgEnum


def pg_enum(enum_class: type[Enum], name: str) -> PgEnum:
    """Mapea un StrEnum de Python contra un tipo enum existente en Postgres.

    Importante: usa `values_callable` para que SQLAlchemy compare por
    `member.value` (lowercase) en vez de `member.name` (UPPERCASE).
    """
    return PgEnum(
        enum_class,
        name=name,
        create_type=False,
        values_callable=lambda obj: [e.value for e in obj],
        native_enum=True,
    )
