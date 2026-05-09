"""Catálogo de normas y mapeo a equipos."""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import Timestamps, UUIDPrimaryKey

if TYPE_CHECKING:
    from app.modules.equipment.models import Equipment


class Standard(Base, UUIDPrimaryKey, Timestamps):
    __tablename__ = "standards"

    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    issuer: Mapped[str | None] = mapped_column(String(128))  # ISO, IEC, INVIMA…
    version: Mapped[str | None] = mapped_column(String(32))
    description: Mapped[str | None] = mapped_column(Text)
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL")
    )

    equipment_links: Mapped[list["EquipmentStandard"]] = relationship(
        back_populates="standard", cascade="all, delete-orphan"
    )


class EquipmentStandard(Base, UUIDPrimaryKey, Timestamps):
    __tablename__ = "equipment_standards"
    __table_args__ = (
        UniqueConstraint("equipment_id", "standard_id", name="uq_equipment_standard"),
    )

    equipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False
    )
    standard_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("standards.id", ondelete="CASCADE"), nullable=False
    )

    equipment: Mapped["Equipment"] = relationship(back_populates="standards")
    standard: Mapped["Standard"] = relationship(back_populates="equipment_links")
