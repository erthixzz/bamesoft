from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import DocumentType
from app.db.session import get_session
from app.modules.auth.deps import require_authenticated, require_staff
from app.modules.documents import service
from app.modules.documents.schemas import DocumentMeta, DocumentOut, SignedUrlOut
from app.modules.users.models import User

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    type_: DocumentType = Form(..., alias="type"),
    clinic_id: uuid.UUID | None = Form(None),
    equipment_id: uuid.UUID | None = Form(None),
    case_id: uuid.UUID | None = Form(None),
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_staff),
):
    body = await file.read()
    meta = DocumentMeta(
        title=title,
        type=type_,
        clinic_id=clinic_id,
        equipment_id=equipment_id,
        case_id=case_id,
    )
    return await service.upload(
        db,
        meta=meta,
        filename=file.filename or "file",
        content=body,
        content_type=file.content_type or "application/octet-stream",
        uploaded_by=current.id,
    )


@router.get("/equipment/{equipment_id}", response_model=list[DocumentOut])
async def list_for_equipment(
    equipment_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    return list(await service.list_for_equipment(db, equipment_id))


@router.get("/case/{case_id}", response_model=list[DocumentOut])
async def list_for_case(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    return list(await service.list_for_case(db, case_id))


@router.get("/{document_id}/signed-url", response_model=SignedUrlOut)
async def get_signed_url(
    document_id: uuid.UUID,
    expires_in: int = 3600,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    url = await service.signed_url(db, document_id, expires_in)
    return SignedUrlOut(url=url, expires_in=expires_in)
