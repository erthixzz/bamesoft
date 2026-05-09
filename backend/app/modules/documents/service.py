from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFound
from app.integrations import supabase as sb
from app.modules.documents.models import Document
from app.modules.documents.schemas import DocumentMeta


def _build_path(meta: DocumentMeta, filename: str) -> str:
    scope = meta.equipment_id or meta.case_id or meta.clinic_id or "global"
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    return f"{meta.type.value}/{scope}/{ts}_{filename}"


async def upload(
    db: AsyncSession,
    *,
    meta: DocumentMeta,
    filename: str,
    content: bytes,
    content_type: str,
    uploaded_by: uuid.UUID,
) -> Document:
    path = _build_path(meta, filename)
    sb.upload_file(path, content, content_type=content_type)

    doc = Document(
        title=meta.title,
        type=meta.type,
        storage_path=path,
        mime_type=content_type,
        size_bytes=len(content),
        clinic_id=meta.clinic_id,
        equipment_id=meta.equipment_id,
        case_id=meta.case_id,
        uploaded_by=uploaded_by,
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)
    return doc


async def list_for_equipment(db: AsyncSession, equipment_id: uuid.UUID) -> Sequence[Document]:
    stmt = (
        select(Document)
        .where(Document.equipment_id == equipment_id)
        .order_by(Document.created_at.desc())
    )
    return (await db.execute(stmt)).scalars().all()


async def list_for_case(db: AsyncSession, case_id: uuid.UUID) -> Sequence[Document]:
    stmt = select(Document).where(Document.case_id == case_id).order_by(Document.created_at.desc())
    return (await db.execute(stmt)).scalars().all()


async def signed_url(db: AsyncSession, doc_id: uuid.UUID, expires_in: int = 3600) -> str:
    doc = await db.get(Document, doc_id)
    if doc is None:
        raise NotFound("Documento")
    return sb.signed_url(doc.storage_path, expires_in=expires_in)
