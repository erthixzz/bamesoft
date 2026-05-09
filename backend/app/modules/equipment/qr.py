"""Generación y parsing de QR para equipos."""
from __future__ import annotations

import io
import json
import secrets

import qrcode

QR_VERSION = 1


def new_token() -> str:
    """Genera un token opaco para el QR (no usar el id directamente)."""
    return secrets.token_urlsafe(24)


def build_payload(code: str, token: str) -> str:
    return json.dumps({"v": QR_VERSION, "code": code, "token": token}, separators=(",", ":"))


def parse_payload(raw: str) -> tuple[str, str]:
    """Devuelve (code, token) si el payload es válido. Lanza ValueError si no."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("QR no es JSON válido") from exc

    if not isinstance(data, dict) or data.get("v") != QR_VERSION:
        raise ValueError("Versión de QR no soportada")
    code = data.get("code")
    token = data.get("token")
    if not isinstance(code, str) or not isinstance(token, str):
        raise ValueError("QR sin code/token")
    return code, token


def render_png(payload: str) -> bytes:
    """Devuelve PNG con el QR ya renderizado."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
