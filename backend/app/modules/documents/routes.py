from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFound
from app.db.enums import DocumentType
from app.db.session import get_session
from app.modules.auth.deps import (
    clinic_scope,
    require_authenticated,
    require_staff,
    requires,
)
from app.modules.cases import service as cases_service
from app.modules.documents import service
from app.modules.documents.models import Document
from app.modules.documents.schemas import DocumentMeta, DocumentOut, SignedUrlOut
from app.modules.equipment import service as equipment_service
from app.modules.users.models import User

router = APIRouter(prefix="/documents", tags=["documents"])


async def _assert_doc_in_scope(db: AsyncSession, doc: Document, scope: uuid.UUID | None) -> None:
    """Verifica que el documento pertenece a la clínica del usuario (si aplica)."""
    if scope is None:
        return
    if doc.equipment_id:
        await equipment_service.get_equipment(db, doc.equipment_id, scope)
    elif doc.case_id:
        await cases_service.get_case(db, doc.case_id, scope)
    elif doc.clinic_id and doc.clinic_id != scope:
        raise NotFound("Documento")


@router.post(
    "",
    response_model=DocumentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(requires("docs", "documents"))],
)
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
    scope = clinic_scope(current)
    if scope is not None:
        # El destino (equipo/caso) debe ser de la clínica del usuario.
        if equipment_id:
            await equipment_service.get_equipment(db, equipment_id, scope)
        if case_id:
            await cases_service.get_case(db, case_id, scope)
        clinic_id = scope
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
    current: User = Depends(require_authenticated),
):
    await equipment_service.get_equipment(db, equipment_id, clinic_scope(current))
    return list(await service.list_for_equipment(db, equipment_id))


@router.get("/case/{case_id}", response_model=list[DocumentOut])
async def list_for_case(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
):
    await cases_service.get_case(db, case_id, clinic_scope(current))
    return list(await service.list_for_case(db, case_id))


@router.get("/{document_id}/signed-url", response_model=SignedUrlOut)
async def get_signed_url(
    document_id: uuid.UUID,
    expires_in: int = 3600,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
):
    doc = await service.get_document(db, document_id)
    await _assert_doc_in_scope(db, doc, clinic_scope(current))
    url = await service.signed_url(db, document_id, expires_in)
    return SignedUrlOut(url=url, expires_in=expires_in)
