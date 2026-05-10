"""Sectores de una clínica (cirugía, UCI, urgencias…)."""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import Timestamps, UUIDPrimaryKey

if TYPE_CHECKING:
    from app.modules.clinics.models import Clinic
    from app.modules.users.models import User


class Sector(Base, UUIDPrimaryKey, Timestamps):
    __tablename__ = "sectors"
    __table_args__ = (UniqueConstraint("clinic_id", "code", name="uq_sector_clinic_code"),)

    clinic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clinics.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    default_engineer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )

    clinic: Mapped["Clinic"] = relationship()
    default_engineer: Mapped["User | None"] = relationship()
