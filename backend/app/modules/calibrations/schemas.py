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
    notes: str | None = None


class CalibrationCreate(CalibrationBase):
    """Alta de calibración.

    `certificate_path` NO se acepta del cliente: es una ruta de Supabase Storage
    y aceptarla permitiría apuntar al objeto de otra clínica. El certificado se
    sube por `/documents`, que sí valida el alcance por clínica.
    """

    model_config = ConfigDict(extra="forbid")


class CalibrationOut(CalibrationBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    certificate_path: str | None = None
    created_at: datetime
