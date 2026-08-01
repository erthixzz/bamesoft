"""Lógica de control de acceso (roles y features de compañía)."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.access.models import ClinicFeature, RolePermission

# Módulos que una compañía puede tener habilitados (deben coincidir con el frontend).
FEATURES = [
    "dashboard",
    "equipment",
    "sectors",
    "cases",
    "alerts",
    "documents",
    "standards",
    "reports",
]


async def get_role_matrix(db: AsyncSession) -> dict[str, dict[str, bool]]:
    rows = (await db.execute(select(RolePermission))).scalars().all()
    matrix: dict[str, dict[str, bool]] = {}
    for r in rows:
        matrix.setdefault(r.role, {})[r.capability] = r.enabled
    return matrix


async def save_role_matrix(
    db: AsyncSession, matrix: dict[str, dict[str, bool]]
) -> dict[str, dict[str, bool]]:
    for role, caps in matrix.items():
        for capability, enabled in caps.items():
            existing = await db.get(RolePermission, (role, capability))
            if existing is not None:
                existing.enabled = bool(enabled)
            else:
                db.add(RolePermission(role=role, capability=capability, enabled=bool(enabled)))
    await db.flush()
    return await get_role_matrix(db)


async def get_clinic_features(db: AsyncSession) -> dict[str, dict[str, bool]]:
    rows = (await db.execute(select(ClinicFeature))).scalars().all()
    matrix: dict[str, dict[str, bool]] = {}
    for r in rows:
        matrix.setdefault(str(r.clinic_id), {})[r.feature] = r.enabled
    return matrix


async def save_clinic_features(
    db: AsyncSession, matrix: dict[str, dict[str, bool]]
) -> dict[str, dict[str, bool]]:
    for clinic_id, feats in matrix.items():
        cid = uuid.UUID(clinic_id)
        for feature, enabled in feats.items():
            existing = await db.get(ClinicFeature, (cid, feature))
            if existing is not None:
                existing.enabled = bool(enabled)
            else:
                db.add(ClinicFeature(clinic_id=cid, feature=feature, enabled=bool(enabled)))
    await db.flush()
    return await get_clinic_features(db)


async def role_has_capability(db: AsyncSession, role: str, capability: str) -> bool:
    """¿La matriz Roles habilita esta capacidad para este rol?

    Fail-closed: si no existe la fila, se deniega. La migración 0007 siembra la
    matriz completa, así que una fila ausente significa "capacidad nueva sin
    decidir", y lo seguro es negarla hasta que un admin la habilite.
    """
    row = await db.get(RolePermission, (role, capability))
    return bool(row is not None and row.enabled)


async def feature_enabled(db: AsyncSession, clinic_id: uuid.UUID | None, feature: str) -> bool:
    """¿La compañía tiene habilitado este módulo?

    Sin fila → habilitado (mismo criterio que `features_for_clinic`): las
    clínicas nuevas arrancan con todo activo y el admin va apagando.
    `clinic_id=None` (super admin) → siempre habilitado.
    """
    if clinic_id is None:
        return True
    row = await db.get(ClinicFeature, (clinic_id, feature))
    return True if row is None else bool(row.enabled)


async def features_for_clinic(db: AsyncSession, clinic_id: uuid.UUID | None) -> dict[str, bool]:
    """Features efectivas de una clínica. Sin fila en BD → habilitado por defecto.
    `clinic_id=None` (super admin) → todo habilitado."""
    result = dict.fromkeys(FEATURES, True)
    if clinic_id is None:
        return result
    rows = (
        (await db.execute(select(ClinicFeature).where(ClinicFeature.clinic_id == clinic_id)))
        .scalars()
        .all()
    )
    for r in rows:
        result[r.feature] = r.enabled
    return result
