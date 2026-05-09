from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class MaintenanceScheduleBase(BaseModel):
    equipment_id: uuid.UUID
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    frequency_days: int = Field(gt=0, le=3650)
    last_done_at: date | None = None
    next_due_at: date | None = None


class MaintenanceScheduleCreate(MaintenanceScheduleBase):
    pass


class MaintenanceScheduleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    frequency_days: int | None = None
    last_done_at: date | None = None
    next_due_at: date | None = None


class MaintenanceScheduleOut(MaintenanceScheduleBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
