from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import Forbidden
from app.db.enums import UserRole
from app.db.session import get_session
from app.modules.access import requests_service, service
from app.modules.access.requests_schemas import (
    AccessRequestOut,
    ApproveIn,
    RejectIn,
)
from app.modules.access.schemas import (
    ClinicFeaturesIn,
    ClinicFeaturesOut,
    MyFeaturesOut,
    RolesIn,
    RolesOut,
)
from app.modules.auth.deps import require_admin, require_authenticated, requires
from app.modules.users.models import User
from app.modules.users.schemas import UserOut

router = APIRouter(prefix="/access", tags=["access"])


@router.get("/roles", response_model=RolesOut)
async def get_roles(
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_authenticated),
):
    return RolesOut(matrix=await service.get_role_matrix(db))


@router.put(
    "/roles",
    response_model=RolesOut,
    dependencies=[Depends(requires("access"))],
)
async def put_roles(
    payload: RolesIn,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),  # solo super admin
):
    return RolesOut(matrix=await service.save_role_matrix(db, payload.matrix))


@router.get("/clinic-features", response_model=ClinicFeaturesOut)
async def get_clinic_features(
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),  # solo super admin ve todas las compañías
):
    return ClinicFeaturesOut(matrix=await service.get_clinic_features(db))


@router.put(
    "/clinic-features",
    response_model=ClinicFeaturesOut,
    dependencies=[Depends(requires("access"))],
)
async def put_clinic_features(
    payload: ClinicFeaturesIn,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),
):
    return ClinicFeaturesOut(matrix=await service.save_clinic_features(db, payload.matrix))


@router.get("/my-features", response_model=MyFeaturesOut)
async def my_features(
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
):
    """Features de la clínica del usuario. Super admin (sin scope) → todas true."""
    clinic = None if current.role == UserRole.ADMIN else current.clinic_id
    return MyFeaturesOut(features=await service.features_for_clinic(db, clinic))


# --- Solicitudes de acceso --------------------------------------------------
# Solo el super admin. Una solicitud pendiente todavía no tiene clínica, así que
# mostrársela a un `clinic_admin` le revelaría los correos de personas que
# intentan entrar a OTRA clínica. Es el mismo criterio de aislamiento que rige
# el resto de la aplicación.

@router.get("/requests", response_model=list[AccessRequestOut])
async def list_access_requests(
    status: str | None = "pending",
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),
):
    """Solicitudes de acceso. Por defecto solo las pendientes."""
    return list(await requests_service.list_requests(db, status=status))


@router.post(
    "/requests/{user_id}/approve",
    response_model=UserOut,
    dependencies=[Depends(requires("access"))],
)
async def approve_access_request(
    user_id: uuid.UUID,
    payload: ApproveIn,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_admin),
):
    """Da de alta a la persona en una clínica. Su sesión abierta pasa a valer."""
    if payload.role == UserRole.ADMIN:
        raise Forbidden(
            "El super administrador no se concede aprobando una solicitud externa."
        )
    return await requests_service.approve(
        db,
        user_id,
        clinic_id=payload.clinic_id,
        role=payload.role,
        resolved_by=current.id,
    )


@router.post(
    "/requests/{user_id}/reject",
    response_model=AccessRequestOut,
    dependencies=[Depends(requires("access"))],
)
async def reject_access_request(
    user_id: uuid.UUID,
    payload: RejectIn,
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_admin),
):
    return await requests_service.reject(
        db, user_id, resolved_by=current.id, note=payload.note
    )


@router.post(
    "/requests/{user_id}/reopen",
    response_model=AccessRequestOut,
    dependencies=[Depends(requires("access"))],
)
async def reopen_access_request(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),
):
    """Devuelve a pendiente una solicitud rechazada por error."""
    return await requests_service.reopen(db, user_id)
