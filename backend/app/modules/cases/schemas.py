"""Schemas de casos."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.db.enums import (
    SATISFACTION_MAX,
    SATISFACTION_MIN,
    CaseCompletion,
    CasePriority,
    CaseStatus,
    CaseType,
    TecnovigilanciaStage,
)


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
    # Satisfacción del servicio en escala Likert de 7 puntos.
    satisfaction_score: int | None = Field(
        default=None, ge=SATISFACTION_MIN, le=SATISFACTION_MAX
    )
    receiver_name: str | None = Field(default=None, max_length=255)
    receiver_doc: str | None = Field(default=None, max_length=64)
    signature_path: str | None = Field(default=None, max_length=1024)


class CaseTecnovigilancia(BaseModel):
    """Marcado de tecnovigilancia sobre un caso ya creado."""

    is_tecnovigilancia: bool
    stage: TecnovigilanciaStage | None = None
    description: str | None = Field(default=None, max_length=4000)

    @model_validator(mode="after")
    def _require_stage(self) -> CaseTecnovigilancia:
        if self.is_tecnovigilancia and self.stage is None:
            raise ValueError("Indica la etapa de tecnovigilancia")
        return self


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
    is_tecnovigilancia: bool = False
    tecnovigilancia_stage: TecnovigilanciaStage | None = None
    tecnovigilancia_description: str | None = None
    tecnovigilancia_at: datetime | None = None
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
