"""Schemas de equipos."""
from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.enums import EquipmentStatus, RiskClass


class EquipmentBase(BaseModel):
    code: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=2, max_length=255)
    brand: str | None = None
    model: str | None = None
    serial_number: str | None = None
    manufacturer: str | None = None
    category_id: uuid.UUID | None = None
    risk_class: RiskClass | None = None
    status: EquipmentStatus = EquipmentStatus.OPERATIONAL
    clinic_id: uuid.UUID
    location_id: uuid.UUID | None = None
    sector_id: uuid.UUID | None = None
    acquisition_date: date | None = None
    warranty_until: date | None = None
    image_url: str | None = None
    notes: str | None = None


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    name: str | None = None
    brand: str | None = None
    model: str | None = None
    serial_number: str | None = None
    manufacturer: str | None = None
    category_id: uuid.UUID | None = None
    risk_class: RiskClass | None = None
    status: EquipmentStatus | None = None
    location_id: uuid.UUID | None = None
    sector_id: uuid.UUID | None = None
    acquisition_date: date | None = None
    warranty_until: date | None = None
    image_url: str | None = None
    notes: str | None = None


class EquipmentOut(EquipmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    qr_token: str
    decommissioned_at: date | None = None
    created_at: datetime
    updated_at: datetime


class EquipmentCategoryBase(BaseModel):
    code: str = Field(min_length=2, max_length=64)
    name: str
    description: str | None = None


class EquipmentCategoryOut(EquipmentCategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class QRPayload(BaseModel):
    """Lo que se incrusta en el QR."""

    v: int = 1
    code: str
    token: str
