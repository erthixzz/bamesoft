"""Usuarios sincronizados con Supabase Auth."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.enums import UserRole
from app.db.mixins import Timestamps, UUIDPrimaryKey
from app.db.types import pg_enum

if TYPE_CHECKING:
    from app.modules.cases.models import Case
    from app.modules.clinics.models import Clinic


class User(Base, UUIDPrimaryKey, Timestamps):
    """Espejo del usuario de Supabase Auth + perfil.

    El `id` coincide con `auth.users.id` de Supabase.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        pg_enum(UserRole, "user_role"),
        nullable=False,
        default=UserRole.CLIENT,
    )
    phone: Mapped[str | None] = mapped_column(String(32))
    license_number: Mapped[str | None] = mapped_column(String(64))
    avatar_url: Mapped[str | None] = mapped_column(String(512))
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    clinic_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clinics.id", ondelete="SET NULL")
    )
    clinic: Mapped["Clinic | None"] = relationship(back_populates="users")

    assigned_cases: Mapped[list["Case"]] = relationship(
        back_populates="assignee",
        foreign_keys="Case.assigned_to",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.email} role={self.role}>"
