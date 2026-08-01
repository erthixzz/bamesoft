"""Schemas de las solicitudes de acceso."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.enums import UserRole


class AccessRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    email: str
    full_name: str | None = None
    avatar_url: str | None = None
    provider: str | None = None
    status: str
    attempts: int
    first_seen_at: datetime
    last_seen_at: datetime
    resolved_at: datetime | None = None
    note: str | None = None


class ApproveIn(BaseModel):
    """El admin decide a qué clínica entra y con qué rol.

    No se acepta el rol `admin`: el super admin de la plataforma se crea a mano,
    nunca aprobando una solicitud que llegó desde fuera.
    """

    model_config = ConfigDict(extra="forbid")

    clinic_id: uuid.UUID
    role: UserRole = UserRole.CLIENT


class RejectIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    note: str | None = Field(default=None, max_length=500)
