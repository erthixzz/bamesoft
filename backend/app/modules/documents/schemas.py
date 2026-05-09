from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.enums import DocumentType


class DocumentMeta(BaseModel):
    """Metadatos enviados junto al archivo (multipart)."""

    title: str
    type: DocumentType
    clinic_id: uuid.UUID | None = None
    equipment_id: uuid.UUID | None = None
    case_id: uuid.UUID | None = None


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    type: DocumentType
    storage_path: str
    mime_type: str
    size_bytes: int
    clinic_id: uuid.UUID | None = None
    equipment_id: uuid.UUID | None = None
    case_id: uuid.UUID | None = None
    uploaded_by: uuid.UUID | None = None
    created_at: datetime


class SignedUrlOut(BaseModel):
    url: str
    expires_in: int
