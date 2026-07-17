"""Traduce (método, ruta) a una acción legible en español para la bitácora."""
from __future__ import annotations

import uuid

# Etiqueta singular por módulo (para "Creó un equipo", etc.).
ENTITY_LABELS: dict[str, str] = {
    "cases": "un caso",
    "equipment": "un equipo",
    "users": "un usuario",
    "sectors": "una unidad de servicio",
    "clinics": "una compañía",
    "documents": "un documento",
    "alerts": "una alerta",
    "calibrations": "una calibración",
    "maintenance": "un mantenimiento",
    "standards": "una norma",
    "reports": "un reporte",
}

VERBS: dict[str, str] = {
    "POST": "Creó",
    "PUT": "Actualizó",
    "PATCH": "Actualizó",
    "DELETE": "Eliminó",
}


def _looks_id(part: str) -> bool:
    try:
        uuid.UUID(part)
        return True
    except (ValueError, AttributeError):
        return False


def describe(method: str, path: str) -> tuple[str, str, str | None]:
    """Devuelve (entity, action_label, entity_id) a partir de la ruta REST."""
    rest = path.split("/api/v1/", 1)[-1].strip("/")
    parts = [p for p in rest.split("/") if p]
    entity = parts[0] if parts else ""
    entity_id = next((p for p in parts[1:] if _looks_id(p)), None)
    sub = parts[-1] if len(parts) > 1 and not _looks_id(parts[-1]) else None

    label = ENTITY_LABELS.get(entity, entity or "un recurso")

    # Casos especiales con verbo propio.
    if entity == "cases" and sub == "accept":
        action = "Aceptó un caso"
    elif entity == "cases" and sub == "activities":
        action = "Agregó una nota a un caso"
    elif entity == "documents" and method == "POST":
        action = "Subió un documento"
    elif entity == "access":
        action = "Actualizó el control de acceso"
    else:
        action = f"{VERBS.get(method, 'Modificó')} {label}"

    return entity, action, entity_id
