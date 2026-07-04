"""Endpoint público mínimo: solo la imagen PNG del QR.

La ficha de datos del equipo YA NO es pública: escanear el QR obliga a iniciar
sesión (el frontend `/e/{code}` es un portón que redirige al login y luego al
detalle protegido, con aislamiento por clínica). Aquí solo queda el PNG del QR,
que no revela datos sensibles (solo codifica la URL del portón) y debe poder
renderizarse en una etiqueta <img> / impresión sin cabeceras de auth.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.equipment import qr, service

router = APIRouter(prefix="/public", tags=["public"])


@router.get(
    "/equipment/{code}/qr.png",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def public_equipment_qr(
    code: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_session),
) -> Response:
    """PNG del QR (codifica la URL del portón). Sin auth: sirve para <img> e impresión."""
    eq = await service.get_by_qr(db, code, token)
    url = qr.build_url(eq.code, eq.qr_token)
    return Response(content=qr.render_png(url), media_type="image/png")
