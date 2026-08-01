from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import UserRole
from app.db.session import get_session
from app.modules.access import service
from app.modules.access.schemas import (
    ClinicFeaturesIn,
    ClinicFeaturesOut,
    MyFeaturesOut,
    RolesIn,
    RolesOut,
)
from app.modules.auth.deps import require_admin, require_authenticated, requires
from app.modules.users.models import User

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
