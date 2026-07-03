"""Búsqueda global: equipos, casos, usuarios, unidades y compañías.

Respeta el aislamiento por clínica (`clinic_scope`) y los roles: usuarios solo
para admin/clinic_admin; compañías solo para el super admin.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import UserRole
from app.db.session import get_session
from app.modules.auth.deps import clinic_scope, require_authenticated
from app.modules.cases.models import Case
from app.modules.clinics.models import Clinic
from app.modules.equipment.models import Equipment
from app.modules.sectors.models import Sector
from app.modules.users.models import User

router = APIRouter(prefix="/search", tags=["search"])

_PER_TYPE = 5


class SearchResult(BaseModel):
    type: str  # equipment | case | user | sector | clinic
    id: str
    title: str
    subtitle: str | None = None


class SearchOut(BaseModel):
    results: list[SearchResult] = Field(default_factory=list)
    total: int = 0


@router.get("", response_model=SearchOut)
async def global_search(
    q: str = Query(..., min_length=2, max_length=120),
    db: AsyncSession = Depends(get_session),
    current: User = Depends(require_authenticated),
):
    scope = clinic_scope(current)
    like = f"%{q.strip()}%"
    results: list[SearchResult] = []

    # Equipos ---------------------------------------------------------------
    eq_stmt = select(Equipment).where(
        or_(
            Equipment.code.ilike(like),
            Equipment.name.ilike(like),
            Equipment.serial_number.ilike(like),
            Equipment.brand.ilike(like),
            Equipment.model.ilike(like),
        )
    )
    if scope is not None:
        eq_stmt = eq_stmt.where(Equipment.clinic_id == scope)
    for e in (await db.execute(eq_stmt.limit(_PER_TYPE))).scalars():
        results.append(
            SearchResult(
                type="equipment",
                id=str(e.id),
                title=f"{e.code} · {e.name}",
                subtitle=" · ".join(x for x in [e.brand, e.model, e.serial_number] if x) or None,
            )
        )

    # Casos -----------------------------------------------------------------
    case_stmt = (
        select(Case, Equipment.name.label("eq_name"))
        .join(Equipment, Equipment.id == Case.equipment_id)
        .where(or_(Case.code.ilike(like), Case.title.ilike(like)))
    )
    if scope is not None:
        case_stmt = case_stmt.where(Equipment.clinic_id == scope)
    for c, eq_name in (await db.execute(case_stmt.limit(_PER_TYPE))).all():
        results.append(
            SearchResult(
                type="case",
                id=str(c.id),
                title=f"{c.code} · {c.title}",
                subtitle=eq_name,
            )
        )

    # Unidades de servicio ----------------------------------------------------
    sec_stmt = select(Sector).where(or_(Sector.name.ilike(like), Sector.code.ilike(like)))
    if scope is not None:
        sec_stmt = sec_stmt.where(Sector.clinic_id == scope)
    for s in (await db.execute(sec_stmt.limit(_PER_TYPE))).scalars():
        results.append(
            SearchResult(type="sector", id=str(s.id), title=s.name, subtitle=s.description)
        )

    # Usuarios (solo quien puede gestionarlos) --------------------------------
    if current.role in (UserRole.ADMIN, UserRole.CLINIC_ADMIN):
        u_stmt = select(User).where(or_(User.full_name.ilike(like), User.email.ilike(like)))
        if scope is not None:
            u_stmt = u_stmt.where(User.clinic_id == scope)
        for u in (await db.execute(u_stmt.limit(_PER_TYPE))).scalars():
            results.append(
                SearchResult(type="user", id=str(u.id), title=u.full_name, subtitle=u.email)
            )

    # Compañías (solo super admin) --------------------------------------------
    if current.role == UserRole.ADMIN:
        cl_stmt = select(Clinic).where(Clinic.name.ilike(like))
        for cl in (await db.execute(cl_stmt.limit(_PER_TYPE))).scalars():
            results.append(
                SearchResult(type="clinic", id=str(cl.id), title=cl.name, subtitle=cl.address)
            )

    return SearchOut(results=results, total=len(results))
