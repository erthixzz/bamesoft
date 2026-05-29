"""Generación y parsing de QR para equipos."""
from __future__ import annotations

import io
import json
import secrets
from urllib.parse import parse_qs, quote, urlparse

import qrcode
from PIL import Image, ImageDraw, ImageFont

from app.core.config import settings

QR_VERSION = 1

# Colores de marca (gradiente del logo Bamesoft: brand-600 -> cyan-500).
_BRAND_FROM = (25, 113, 245)  # #1971f5
_BRAND_TO = (6, 182, 212)  # #06b6d4


def new_token() -> str:
    """Genera un token opaco para el QR (no usar el id directamente)."""
    return secrets.token_urlsafe(24)


def build_url(code: str, token: str) -> str:
    """URL pública que abre la ficha del equipo al escanear con cualquier cámara."""
    base = settings.PUBLIC_APP_URL.rstrip("/")
    return f"{base}/e/{quote(code, safe='')}?t={quote(token, safe='')}"


def build_payload(code: str, token: str) -> str:
    """Compatibilidad: payload JSON antiguo (ya no se usa para generar QR)."""
    return json.dumps({"v": QR_VERSION, "code": code, "token": token}, separators=(",", ":"))


def parse_payload(raw: str) -> tuple[str, str]:
    """Devuelve (code, token) desde el contenido del QR.

    Acepta el nuevo formato URL (`.../e/{code}?t={token}`) y el JSON antiguo.
    Lanza ValueError si no es válido.
    """
    raw = raw.strip()

    # Nuevo formato: URL
    if raw.startswith("http://") or raw.startswith("https://"):
        parsed = urlparse(raw)
        parts = [p for p in parsed.path.split("/") if p]
        token_vals = parse_qs(parsed.query).get("t", [])
        if len(parts) >= 2 and parts[-2] == "e" and token_vals:
            return parts[-1], token_vals[0]
        raise ValueError("URL de QR no reconocida")

    # Formato antiguo: JSON
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("QR no reconocido") from exc

    if not isinstance(data, dict) or data.get("v") != QR_VERSION:
        raise ValueError("Versión de QR no soportada")
    code = data.get("code")
    token = data.get("token")
    if not isinstance(code, str) or not isinstance(token, str):
        raise ValueError("QR sin code/token")
    return code, token


def _diagonal_gradient(size: tuple[int, int], c1: tuple[int, int, int], c2: tuple[int, int, int]) -> Image.Image:
    """Genera un degradado diagonal de c1 (arriba-izq) a c2 (abajo-der)."""
    w, h = size
    grad = Image.new("RGB", size)
    px = grad.load()
    denom = max(1, (w - 1) + (h - 1))
    for y in range(h):
        for x in range(w):
            t = (x + y) / denom
            px[x, y] = (
                int(c1[0] + (c2[0] - c1[0]) * t),
                int(c1[1] + (c2[1] - c1[1]) * t),
                int(c1[2] + (c2[2] - c1[2]) * t),
            )
    return grad


def _brand_badge(box: int) -> Image.Image:
    """Insignia de marca: placa blanca + cuadro con degradado y la 'B' centrada."""
    scale = 4  # supermuestreo para bordes nítidos
    s = box * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Placa blanca redondeada (separa el logo de los módulos del QR).
    draw.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.26), fill=(255, 255, 255, 255))

    # Cuadro de marca con degradado.
    pad = int(s * 0.12)
    inner = s - 2 * pad
    grad = _diagonal_gradient((inner, inner), _BRAND_FROM, _BRAND_TO).convert("RGBA")
    mask = Image.new("L", (inner, inner), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, inner - 1, inner - 1], radius=int(inner * 0.24), fill=255
    )
    img.paste(grad, (pad, pad), mask)

    # Letra "B" blanca centrada.
    try:
        font = ImageFont.load_default(size=int(inner * 0.72))
    except TypeError:  # Pillow < 10
        font = ImageFont.load_default()
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), "B", font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((s - tw) / 2 - bbox[0], (s - th) / 2 - bbox[1]), "B", font=font, fill=(255, 255, 255, 255))

    return img.resize((box, box), Image.LANCZOS)


def render_png(payload: str, *, brand: bool = True) -> bytes:
    """Devuelve PNG con el QR. Si brand=True, incrusta el logo Bamesoft al centro."""
    qr = qrcode.QRCode(
        version=None,
        # Corrección alta (H): tolera hasta ~30% de oclusión, necesario para el logo.
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    if brand:
        w, _ = img.size
        box = int(w * 0.24)  # 24% < 30% de capacidad de corrección
        badge = _brand_badge(box)
        img.alpha_composite(badge, ((w - box) // 2, (img.size[1] - box) // 2))

    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()
