from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StandardBase(BaseModel):
    code: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=2, max_length=255)
    issuer: str | None = None
    version: str | None = None
    description: str | None = None
    document_id: uuid.UUID | None = None


class StandardCreate(StandardBase):
    pass


class StandardOut(StandardBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime


class EquipmentStandardLink(BaseModel):
    equipment_id: uuid.UUID
    standard_id: uuid.UUID
