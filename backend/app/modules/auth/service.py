"""Login server-side (proxy a Supabase Auth REST).

En la mayoría de los casos el frontend llamará a Supabase Auth directamente y
mandará el JWT al backend. Este servicio existe sólo por compatibilidad con
clientes server-to-server o pruebas.
"""
from __future__ import annotations

import httpx

from app.core.config import settings
from app.core.errors import Unauthorized
from app.modules.auth.schemas import LoginIn, TokenOut


async def password_login(payload: LoginIn) -> TokenOut:
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise Unauthorized("Supabase no configurado")

    url = f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": settings.SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(
            url,
            json={"email": payload.email, "password": payload.password},
            headers=headers,
        )
    if r.status_code != 200:
        raise Unauthorized("Credenciales inválidas")
    body = r.json()
    return TokenOut(
        access_token=body["access_token"],
        token_type="bearer",
        expires_in=body.get("expires_in", 3600),
    )
