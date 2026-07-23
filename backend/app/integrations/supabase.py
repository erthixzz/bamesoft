"""Cliente Supabase (Storage / Auth admin) — sólo server-side."""
from __future__ import annotations

import re
import unicodedata
from functools import lru_cache

from supabase import Client, create_client

from app.core.config import settings


def safe_filename(name: str) -> str:
    """Normaliza un nombre de archivo para usarlo como clave de Supabase Storage.

    Quita acentos, conserva solo `[A-Za-z0-9._-]`, reemplaza el resto por `_` y
    colapsa repeticiones. Evita claves inválidas (espacios, tildes, símbolos) que
    hacen fallar la subida. Devuelve "archivo" si el resultado queda vacío.
    """
    base = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", base).strip("._-")
    base = re.sub(r"_{2,}", "_", base)
    return base or "archivo"


@lru_cache(maxsize=1)
def supabase_admin() -> Client:
    """Cliente con la `service_role` key — uso administrativo."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        raise RuntimeError("Supabase no está configurado (URL / SERVICE_KEY).")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


def upload_file(path: str, content: bytes, content_type: str = "application/octet-stream") -> str:
    """Sube un archivo al bucket configurado y devuelve la ruta interna."""
    sb = supabase_admin()
    sb.storage.from_(settings.STORAGE_BUCKET).upload(
        path=path,
        file=content,
        file_options={"content-type": content_type, "upsert": "true"},
    )
    return path


def signed_url(path: str, expires_in: int = 60 * 60) -> str:
    sb = supabase_admin()
    res = sb.storage.from_(settings.STORAGE_BUCKET).create_signed_url(path, expires_in)
    return res["signedURL"] if isinstance(res, dict) else res.signed_url
