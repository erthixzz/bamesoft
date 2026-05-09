"""Clínicas y ubicaciones físicas."""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import Timestamps, UUIDPrimaryKey

if TYPE_CHECKING:
    from app.modules.equipment.models import Equipment
    from app.modules.users.models import User


class Clinic(Base, UUIDPrimaryKey, Timestamps):
    __tablename__ = "clinics"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tax_id: Mapped[str | None] = mapped_column(String(64), unique=True)
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(32))
    address: Mapped[str | None] = mapped_column(String(512))
    logo_url: Mapped[str | None] = mapped_column(String(512))

    locations: Mapped[list["Location"]] = relationship(
        back_populates="clinic", cascade="all, delete-orphan"
    )
    users: Mapped[list["User"]] = relationship(back_populates="clinic")
    equipment: Mapped[list["Equipment"]] = relationship(back_populates="clinic")


class Location(Base, UUIDPrimaryKey, Timestamps):
    """Ubicación física dentro de una clínica (área / sala / piso)."""

    __tablename__ = "locations"
    __table_args__ = (UniqueConstraint("clinic_id", "code", name="uq_location_clinic_code"),)

    clinic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clinics.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    building: Mapped[str | None] = mapped_column(String(128))
    floor: Mapped[str | None] = mapped_column(String(64))
    room: Mapped[str | None] = mapped_column(String(64))

    clinic: Mapped["Clinic"] = relationship(back_populates="locations")
    equipment: Mapped[list["Equipment"]] = relationship(back_populates="location")
