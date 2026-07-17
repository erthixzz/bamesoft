"""Schemas de la bitácora de auditoría."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    actor_id: uuid.UUID | None = None
    actor_name: str | None = None
    actor_role: str | None = None
    method: str
    action: str
    entity: str | None = None
    entity_id: str | None = None
    status_code: int | None = None
    created_at: datetime


class CountRow(BaseModel):
    key: str
    label: str
    count: int


class DayCount(BaseModel):
    day: str
    count: int


class AuditSummary(BaseModel):
    total: int
    actors: int
    by_actor: list[CountRow]
    by_action: list[CountRow]
    by_entity: list[CountRow]
    by_day: list[DayCount]
