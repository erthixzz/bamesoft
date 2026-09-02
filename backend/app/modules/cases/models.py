"""Casos (tickets) y bitácora."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.enums import (
    CaseCompletion,
    CasePriority,
    CaseStatus,
    CaseType,
    TecnovigilanciaStage,
)
from app.db.mixins import Timestamps, UUIDPrimaryKey
from app.db.types import pg_enum

if TYPE_CHECKING:
    from app.modules.equipment.models import Equipment
    from app.modules.users.models import User


class Case(Base, UUIDPrimaryKey, Timestamps):
    __tablename__ = "cases"

    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    type: Mapped[CaseType] = mapped_column(
        pg_enum(CaseType, "case_type"), nullable=False
    )
    status: Mapped[CaseStatus] = mapped_column(
        pg_enum(CaseStatus, "case_status"),
        nullable=False,
        default=CaseStatus.OPEN,
    )
    priority: Mapped[CasePriority] = mapped_column(
        pg_enum(CasePriority, "case_priority"),
        nullable=False,
        default=CasePriority.MEDIUM,
    )

    equipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False
    )
    sector_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sectors.id", ondelete="SET NULL")
    )
    reported_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )

    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sla_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Tiempos de flujo del servicio (alimentan métricas de productividad).
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    work_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Resolución / soporte de servicio.
    operation_minutes: Mapped[int | None] = mapped_column(Integer)
    work_performed: Mapped[str | None] = mapped_column(Text)
    parts_count: Mapped[int | None] = mapped_column(Integer)
    parts_detail: Mapped[str | None] = mapped_column(Text)
    completion: Mapped[CaseCompletion | None] = mapped_column(
        pg_enum(CaseCompletion, "case_completion")
    )
    # Satisfacción en escala Likert de 7 puntos (1 = Muy insatisfecho … 7 = Muy
    # satisfecho). La columna `satisfaction` (3 caritas) quedó obsoleta en 0015.
    satisfaction_score: Mapped[int | None] = mapped_column(SmallInteger)
    receiver_name: Mapped[str | None] = mapped_column(String(255))
    receiver_doc: Mapped[str | None] = mapped_column(String(64))
    signature_path: Mapped[str | None] = mapped_column(String(1024))

    # Tecnovigilancia: el caso corresponde a un evento adverso / incidente en el
    # que el dispositivo causó (o pudo causar) daño al paciente o al operador.
    is_tecnovigilancia: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    tecnovigilancia_stage: Mapped[TecnovigilanciaStage | None] = mapped_column(
        pg_enum(TecnovigilanciaStage, "tecnovigilancia_stage")
    )
    tecnovigilancia_description: Mapped[str | None] = mapped_column(Text)
    tecnovigilancia_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    equipment: Mapped["Equipment"] = relationship(back_populates="cases")
    reporter: Mapped["User | None"] = relationship(foreign_keys=[reported_by])
    assignee: Mapped["User | None"] = relationship(
        back_populates="assigned_cases", foreign_keys=[assigned_to]
    )

    activities: Mapped[list["CaseActivity"]] = relationship(
        back_populates="case", cascade="all, delete-orphan", order_by="CaseActivity.created_at"
    )


class CaseActivity(Base, UUIDPrimaryKey, Timestamps):
    """Registro inmutable de actividad sobre un caso."""

    __tablename__ = "case_activities"

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    author_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    case: Mapped["Case"] = relationship(back_populates="activities")
    author: Mapped["User | None"] = relationship()
