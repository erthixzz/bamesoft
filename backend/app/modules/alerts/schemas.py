from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.enums import AlertSeverity, AlertType


class AlertBase(BaseModel):
    type: AlertType
    severity: AlertSeverity = AlertSeverity.INFO
    title: str
    message: str
    equipment_id: uuid.UUID | None = None
    case_id: uuid.UUID | None = None
    due_at: datetime | None = None


class AlertCreate(AlertBase):
    pass


class AlertOut(AlertBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    created_at: datetime
