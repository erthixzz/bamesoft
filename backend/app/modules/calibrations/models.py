"""Calibraciones por equipo."""
from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import Timestamps, UUIDPrimaryKey

if TYPE_CHECKING:
    from app.modules.equipment.models import Equipment
    from app.modules.users.models import User


class Calibration(Base, UUIDPrimaryKey, Timestamps):
    __tablename__ = "calibrations"

    equipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False
    )
    performed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    performed_at: Mapped[date] = mapped_column(Date, nullable=False)
    expires_at: Mapped[date | None] = mapped_column(Date)
    passed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    standard: Mapped[str | None] = mapped_column(String(128))
    certificate_path: Mapped[str | None] = mapped_column(String(512))
    notes: Mapped[str | None] = mapped_column(Text)

    equipment: Mapped["Equipment"] = relationship(back_populates="calibrations")
    technician: Mapped["User | None"] = relationship()
