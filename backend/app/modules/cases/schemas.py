"""Schemas de casos."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.enums import CaseCompletion, CasePriority, CaseStatus, CaseType


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


class CaseResolution(BaseModel):
    """Campos del soporte/cierre del servicio."""

    operation_minutes: int | None = Field(default=None, ge=0)
    work_performed: str | None = None
    parts_count: int | None = Field(default=None, ge=0)
    parts_detail: str | None = None
    completion: CaseCompletion | None = None
    receiver_name: str | None = Field(default=None, max_length=255)
    receiver_doc: str | None = Field(default=None, max_length=64)
    signature_path: str | None = Field(default=None, max_length=1024)


class CaseUpdate(CaseResolution):
    title: str | None = None
    description: str | None = None
    type: CaseType | None = None
    priority: CasePriority | None = None
    status: CaseStatus | None = None
    sector_id: uuid.UUID | None = None
    assigned_to: uuid.UUID | None = None
    sla_due_at: datetime | None = None


class CaseOut(CaseBase, CaseResolution):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    code: str
    status: CaseStatus
    reported_by: uuid.UUID | None = None
    opened_at: datetime | None = None
    closed_at: datetime | None = None
    assigned_at: datetime | None = None
    accepted_at: datetime | None = None
    work_started_at: datetime | None = None
    finished_at: datetime | None = None
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
