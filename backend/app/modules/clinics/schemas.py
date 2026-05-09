"""Schemas de clínicas y ubicaciones."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClinicBase(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    tax_id: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    logo_url: str | None = None


class ClinicCreate(ClinicBase):
    pass


class ClinicUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    logo_url: str | None = None


class ClinicOut(ClinicBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class LocationBase(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    building: str | None = None
    floor: str | None = None
    room: str | None = None


class LocationCreate(LocationBase):
    clinic_id: uuid.UUID


class LocationUpdate(BaseModel):
    name: str | None = None
    building: str | None = None
    floor: str | None = None
    room: str | None = None


class LocationOut(LocationBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    clinic_id: uuid.UUID
    created_at: datetime
