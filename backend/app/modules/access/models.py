"""Control de acceso configurable: acciones por rol y módulos por compañía."""
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RolePermission(Base):
    """Qué puede *hacer* cada rol (matriz rol × capacidad). Global."""

    __tablename__ = "role_permissions"

    role: Mapped[str] = mapped_column(String(32), primary_key=True)
    capability: Mapped[str] = mapped_column(String(64), primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class ClinicFeature(Base):
    """Qué módulos puede *ver* cada compañía (matriz compañía × módulo)."""

    __tablename__ = "clinic_features"

    clinic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clinics.id", ondelete="CASCADE"), primary_key=True
    )
    feature: Mapped[str] = mapped_column(String(64), primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
