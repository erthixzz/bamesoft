from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SectorBase(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    default_engineer_id: uuid.UUID | None = None


class SectorCreate(SectorBase):
    clinic_id: uuid.UUID


class SectorUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    default_engineer_id: uuid.UUID | None = None


class SectorOut(SectorBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    clinic_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
