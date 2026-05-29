"""Esquemas de la ficha pública del equipo (info general, no sensible)."""
from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel


class PublicCaseBrief(BaseModel):
    code: str
    title: str
    type: str
    status: str
    priority: str
    opened_at: datetime | None = None
    closed_at: datetime | None = None


class PublicMaintenanceBrief(BaseModel):
    name: str
    frequency_days: int
    last_done_at: date | None = None
    next_due_at: date | None = None


class PublicCalibrationBrief(BaseModel):
    performed_at: date
    expires_at: date | None = None
    passed: bool
    standard: str | None = None


class PublicEquipmentOut(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    brand: str | None = None
    model: str | None = None
    serial_number: str | None = None
    manufacturer: str | None = None
    status: str
    risk_class: str | None = None
    category_name: str | None = None
    clinic_name: str | None = None
    location_name: str | None = None
    acquisition_date: date | None = None
    warranty_until: date | None = None
    image_url: str | None = None
    notes: str | None = None

    cases_open: int = 0
    cases_total: int = 0

    cases: list[PublicCaseBrief] = []
    maintenance: list[PublicMaintenanceBrief] = []
    calibrations: list[PublicCalibrationBrief] = []
