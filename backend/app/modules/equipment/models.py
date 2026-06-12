"""Equipos médicos y categorías."""
from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.enums import EquipmentStatus, RiskClass
from app.db.mixins import Timestamps, UUIDPrimaryKey
from app.db.types import pg_enum

if TYPE_CHECKING:
    from app.modules.calibrations.models import Calibration
    from app.modules.cases.models import Case
    from app.modules.clinics.models import Clinic, Location
    from app.modules.maintenance.models import MaintenanceSchedule
    from app.modules.standards.models import EquipmentStandard


class EquipmentCategory(Base, UUIDPrimaryKey, Timestamps):
    __tablename__ = "equipment_categories"

    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    equipment: Mapped[list["Equipment"]] = relationship(back_populates="category")


class Equipment(Base, UUIDPrimaryKey, Timestamps):
    __tablename__ = "equipment"

    # Identificación
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    qr_token: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(128))
    model: Mapped[str | None] = mapped_column(String(128))
    serial_number: Mapped[str | None] = mapped_column(String(128), index=True)
    manufacturer: Mapped[str | None] = mapped_column(String(255))

    # Clasificación
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipment_categories.id", ondelete="SET NULL")
    )
    risk_class: Mapped[RiskClass | None] = mapped_column(
        pg_enum(RiskClass, "risk_class")
    )

    # Estado y ubicación
    status: Mapped[EquipmentStatus] = mapped_column(
        pg_enum(EquipmentStatus, "equipment_status"),
        nullable=False,
        default=EquipmentStatus.OPERATIONAL,
    )
    clinic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clinics.id", ondelete="CASCADE"), nullable=False
    )
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id", ondelete="SET NULL")
    )

    # Vida útil
    acquisition_date: Mapped[date | None] = mapped_column(Date)
    warranty_until: Mapped[date | None] = mapped_column(Date)
    decommissioned_at: Mapped[date | None] = mapped_column(Date)

    image_url: Mapped[str | None] = mapped_column(String(512))
    notes: Mapped[str | None] = mapped_column(Text)

    # Relaciones
    category: Mapped["EquipmentCategory | None"] = relationship(back_populates="equipment")
    clinic: Mapped["Clinic"] = relationship(back_populates="equipment")
    location: Mapped["Location | None"] = relationship(back_populates="equipment")

    cases: Mapped[list["Case"]] = relationship(back_populates="equipment")
    schedules: Mapped[list["MaintenanceSchedule"]] = relationship(
        back_populates="equipment", cascade="all, delete-orphan"
    )
    calibrations: Mapped[list["Calibration"]] = relationship(
        back_populates="equipment", cascade="all, delete-orphan"
    )
    standards: Mapped[list["EquipmentStandard"]] = relationship(
        back_populates="equipment", cascade="all, delete-orphan"
    )
    life_sheet: Mapped["EquipmentLifeSheet | None"] = relationship(
        back_populates="equipment", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Equipment {self.code} {self.name!r}>"


class EquipmentLifeSheet(Base, UUIDPrimaryKey, Timestamps):
    """Hoja de Vida del equipo (formato clínico MNT-FR-023).

    El cuerpo del formato se guarda en `data` (JSONB) validado por Pydantic en
    la API; los campos compartidos (código, marca, serial, clínica, garantía…)
    se reutilizan desde la fila de `equipment`, no se duplican aquí.
    """

    __tablename__ = "equipment_life_sheets"

    equipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("equipment.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    formato_codigo: Mapped[str] = mapped_column(
        String(64), nullable=False, default="MNT-FR-023"
    )
    formato_fecha: Mapped[str | None] = mapped_column(String(64))
    data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    equipment: Mapped["Equipment"] = relationship(back_populates="life_sheet")
