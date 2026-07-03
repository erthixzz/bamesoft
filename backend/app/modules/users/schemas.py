"""Pydantic schemas para Users."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.db.enums import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    role: UserRole = UserRole.CLIENT
    phone: str | None = None
    license_number: str | None = None
    clinic_id: uuid.UUID | None = None


class UserCreate(UserBase):
    """Crear perfil (usado tras alta en Supabase Auth)."""

    id: uuid.UUID  # debe coincidir con auth.users.id


class UserInvite(UserBase):
    """Alta completa desde la UI: crea la cuenta en Supabase Auth + el perfil."""

    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: UserRole | None = None
    phone: str | None = None
    license_number: str | None = None
    avatar_url: str | None = None
    active: bool | None = None
    clinic_id: uuid.UUID | None = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    avatar_url: str | None = None
    active: bool
    clinic_name: str | None = None
    created_at: datetime
    updated_at: datetime
