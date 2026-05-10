"""Schemas de casos."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.enums import CasePriority, CaseStatus, CaseType


class CaseBase(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    description: str | None = None
    type: CaseType
    priority: CasePriority = CasePriority.MEDIUM
    equipment_id: uuid.UUID
    sector_id: uuid.UUID | None = None
    assigned_to: uuid.UUID | None = None
    sla_due_at: datetime | None = None


class CaseCreate(CaseBase):
    pass


class CaseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: CasePriority | None = None
    status: CaseStatus | None = None
    sector_id: uuid.UUID | None = None
    assigned_to: uuid.UUID | None = None
    sla_due_at: datetime | None = None


class CaseOut(CaseBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    code: str
    status: CaseStatus
    reported_by: uuid.UUID | None = None
    opened_at: datetime | None = None
    closed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class CaseActivityIn(BaseModel):
    action: str = Field(min_length=2, max_length=64)
    notes: str | None = None


class CaseActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    case_id: uuid.UUID
    author_id: uuid.UUID | None
    action: str
    notes: str | None
    created_at: datetime
