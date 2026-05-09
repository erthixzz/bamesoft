from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class CalibrationBase(BaseModel):
    equipment_id: uuid.UUID
    performed_by: uuid.UUID | None = None
    performed_at: date
    expires_at: date | None = None
    passed: bool = True
    standard: str | None = None
    certificate_path: str | None = None
    notes: str | None = None


class CalibrationCreate(CalibrationBase):
    pass


class CalibrationOut(CalibrationBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
