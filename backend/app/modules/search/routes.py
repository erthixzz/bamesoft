"""Búsqueda global: equipos, casos, usuarios, unidades y compañías.

Optimizada para latencia: TODO se resuelve en UNA sola consulta (UNION ALL con
límite por tipo) en vez de un viaje a la BD por entidad. Cada bloque busca
sobre una expresión concatenada que coincide con su índice GIN pg_trgm
(migración 0008), de modo que el ILIKE '%…%' usa índice y no escanea la tabla.

Respeta el aislamiento por clínica (`clinic_scope`) y los roles: usuarios solo
para admin/clinic_admin; compañías solo para el super admin.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import UserRole
from app.db.session import get_session
from app.modules.auth.deps import clinic_scope, require_authenticated
from app.modules.users.models import User

router = APIRouter(prefix="/search", tags=["search"])

_PER_TYPE = 5

# Las expresiones `coalesce(...) || ' ' || ...` deben coincidir EXACTAMENTE con
# las de los índices GIN trgm de 0008_search_indexes.sql para que el planner
# los use. Dentro de cada bloque, los aciertos por prefijo se ordenan primero.
# Nota: se usa cast(... as ...) en vez de `::` porque el `::` choca con el
# marcador de bind params `:nombre` de SQLAlchemy text() (interpreta `:text`).
_SEARCH_SQL = text(
    """
    (
      select 'equipment' as rtype, cast(e.id as text) as rid, e.code as slug,
             e.code || ' · ' || e.name as title,
             nullif(concat_ws(' · ', e.brand, e.model, e.serial_number), '') as subtitle
      from equipment e
      where (cast(:scope as uuid) is null or e.clinic_id = cast(:scope as uuid))
        and (coalesce(e.code,'') || ' ' || coalesce(e.name,'') || ' ' ||
             coalesce(e.serial_number,'') || ' ' || coalesce(e.brand,'') || ' ' ||
             coalesce(e.model,'')) ilike :like
      order by (e.code ilike :prefix or e.name ilike :prefix) desc, e.name
      limit :per
    )
    union all
    (
      select 'case', cast(c.id as text), c.code, c.code || ' · ' || c.title, e.name
      from cases c
      join equipment e on e.id = c.equipment_id
      where (cast(:scope as uuid) is null or e.clinic_id = cast(:scope as uuid))
        and (coalesce(c.code,'') || ' ' || coalesce(c.title,'')) ilike :like
      order by (c.code ilike :prefix) desc, c.created_at desc
      limit :per
    )
    union all
    (
      select 'sector', cast(s.id as text), null, s.name, s.description
      from sectors s
      where (cast(:scope as uuid) is null or s.clinic_id = cast(:scope as uuid))
        and (coalesce(s.code,'') || ' ' || coalesce(s.name,'')) ilike :like
      order by s.name
      limit :per
    )
    union all
    (
      select 'user', cast(u.id as text), null, u.full_name, u.email
      from users u
      where :inc_users
        and (cast(:scope as uuid) is null or u.clinic_id = cast(:scope as uuid))
        and (coalesce(u.full_name,'') || ' ' || coalesce(u.email,'')) ilike :like
      order by (u.full_name ilike :prefix) desc, u.full_name
      limit :per
    )
    union all
    (
      select 'clinic', cast(cl.id as text), null, cl.name, cl.address
      from clinics cl
      where :inc_clinics and coalesce(cl.name,'') ilike :like
      order by cl.name
      limit :per
    )
    """
)


class SearchResult(BaseModel):
    type: str  # equipment | case | user | sector | clinic
    id: str
    slug: str | None = None  # código legible para URL bonita (equipos/casos)
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
    term = q.strip()
    params = {
        "scope": str(scope) if scope is not None else None,
        "like": f"%{term}%",
        "prefix": f"{term}%",
        "per": _PER_TYPE,
        "inc_users": current.role in (UserRole.ADMIN, UserRole.CLINIC_ADMIN),
        "inc_clinics": current.role == UserRole.ADMIN,
    }

    rows = (await db.execute(_SEARCH_SQL, params)).all()
    results = [
        SearchResult(type=r.rtype, id=r.rid, slug=r.slug, title=r.title, subtitle=r.subtitle)
        for r in rows
    ]
    return SearchOut(results=results, total=len(results))
