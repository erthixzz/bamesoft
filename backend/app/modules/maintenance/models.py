"""Cronograma de mantenimiento preventivo."""
from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import Timestamps, UUIDPrimaryKey

if TYPE_CHECKING:
    from app.modules.equipment.models import Equipment


class MaintenanceSchedule(Base, UUIDPrimaryKey, Timestamps):
    __tablename__ = "maintenance_schedules"

    equipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    frequency_days: Mapped[int] = mapped_column(Integer, nullable=False)
    last_done_at: Mapped[date | None] = mapped_column(Date)
    next_due_at: Mapped[date | None] = mapped_column(Date, index=True)

    equipment: Mapped["Equipment"] = relationship(back_populates="schedules")
