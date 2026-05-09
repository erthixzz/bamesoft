"""Declarative base — sin imports de modelos para evitar ciclos.

Para registrar todos los modelos (p.ej. en Alembic), importar `app.db.registry`.
"""
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarativa común a todos los modelos."""
