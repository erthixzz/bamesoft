"""Alertas (vencimientos, SLAs)."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.enums import AlertSeverity, AlertType
from app.db.mixins import Timestamps, UUIDPrimaryKey
from app.db.types import pg_enum

if TYPE_CHECKING:
    from app.modules.cases.models import Case
    from app.modules.equipment.models import Equipment


class Alert(Base, UUIDPrimaryKey, Timestamps):
    __tablename__ = "alerts"

    type: Mapped[AlertType] = mapped_column(
        pg_enum(AlertType, "alert_type"), nullable=False
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        pg_enum(AlertSeverity, "alert_severity"),
        nullable=False,
        default=AlertSeverity.INFO,
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    equipment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipment.id", ondelete="CASCADE")
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE")
    )

    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    equipment: Mapped["Equipment | None"] = relationship()
    case: Mapped["Case | None"] = relationship()
