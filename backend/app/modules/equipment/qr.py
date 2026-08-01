"""Generación y parsing de QR para equipos."""

from __future__ import annotations

import io
import json
import secrets
from urllib.parse import parse_qs, quote, urlparse

import qrcode
from PIL import Image, ImageDraw

from app.core.config import settings

QR_VERSION = 1

# Colores de marca (gradiente del logo Bamesoft: azul profundo -> cian).
_BRAND_FROM = (30, 58, 138)  # #1e3a8a (profundidad)
_BRAND_TO = (6, 182, 212)  # #06b6d4
_CYAN = (125, 211, 252)  # #7dd3fc (circuito IA)
_EMERALD = (52, 211, 153)  # #34d399 (cruz médica)


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


def _diagonal_gradient(
    size: tuple[int, int], c1: tuple[int, int, int], c2: tuple[int, int, int]
) -> Image.Image:
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
    """Insignia de marca (mismo monograma vectorial de la app): placa blanca +
    cuadro con degradado, grilla técnica, 'B' sólida, cruz médica y circuito."""
    scale = 4  # supermuestreo para bordes nítidos
    s = box * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Placa blanca redondeada (separa el logo de los módulos del QR).
    draw.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.26), fill=(255, 255, 255, 255))

    # Cuadro de marca con degradado.
    pad = int(s * 0.1)
    inner = s - 2 * pad
    grad = _diagonal_gradient((inner, inner), _BRAND_FROM, _BRAND_TO).convert("RGBA")
    gmask = Image.new("L", (inner, inner), 0)
    ImageDraw.Draw(gmask).rounded_rectangle(
        [0, 0, inner - 1, inner - 1], radius=int(inner * 0.27), fill=255
    )
    img.paste(grad, (pad, pad), gmask)

    d = ImageDraw.Draw(img)
    u = inner / 48.0

    def gx(x: float) -> float:  # coords 48-grid -> píxel global
        return pad + x * u

    white = (255, 255, 255, 255)

    # Trazas + nodos de circuito (cian).
    tw = max(1, int(1.4 * u))
    d.line([gx(32.5), gx(16), gx(38.5), gx(16)], fill=_CYAN, width=tw)
    d.line([gx(34.5), gx(32), gx(39.5), gx(32)], fill=_CYAN, width=tw)
    for cx, cy, r in [(39.2, 16, 1.9), (40, 32, 1.7)]:
        d.ellipse([gx(cx - r), gx(cy - r), gx(cx + r), gx(cy + r)], fill=_CYAN)

    # "B" sólida blanca: espina + dos bombas (rectángulos redondeados; el lado
    # izquierdo redondeado queda oculto tras la espina).
    d.rounded_rectangle([gx(12), gx(10), gx(19.6), gx(38)], radius=int(2.6 * u), fill=white)
    d.rounded_rectangle([gx(13), gx(10), gx(32.5), gx(24)], radius=int(7 * u), fill=white)
    d.rounded_rectangle([gx(13), gx(23), gx(34.6), gx(38)], radius=int(7.5 * u), fill=white)

    # Contra-huecos: repegar el degradado con máscara.
    cmask = Image.new("L", (inner, inner), 0)
    cd = ImageDraw.Draw(cmask)
    cd.rounded_rectangle([19.6 * u, 14.3 * u, 29 * u, 22 * u], radius=int(3.8 * u), fill=255)
    cd.rounded_rectangle([19.6 * u, 26.7 * u, 30 * u, 35 * u], radius=int(4.1 * u), fill=255)
    img.paste(grad, (pad, pad), cmask)

    # Cruz médica (esmeralda) en el hueco superior.
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(
        [gx(21.3), gx(15.7), gx(23.3), gx(21.3)], radius=int(0.9 * u), fill=_EMERALD
    )
    d.rounded_rectangle(
        [gx(19.5), gx(17.5), gx(25.1), gx(19.5)], radius=int(0.9 * u), fill=_EMERALD
    )

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
