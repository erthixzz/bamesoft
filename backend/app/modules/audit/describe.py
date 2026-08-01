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

STATUS_LABELS: dict[str, str] = {
    "open": "Abierto",
    "assigned": "Asignado",
    "in_progress": "En progreso",
    "waiting_parts": "Espera repuestos",
    "waiting_client": "Espera cliente",
    "closed": "Cerrado",
    "cancelled": "Anulado",
}
PRIORITY_LABELS: dict[str, str] = {
    "low": "Baja",
    "medium": "Media",
    "high": "Alta",
    "critical": "Crítica",
}
COMPLETION_LABELS: dict[str, str] = {"complete": "Completo", "incomplete": "Incompleto"}
TYPE_LABELS: dict[str, str] = {
    "corrective": "Correctivo",
    "preventive": "Preventivo",
    "calibration": "Calibración",
    "installation": "Instalación",
    "inspection": "Inspección",
}


def summarize_case(body: dict) -> list[str]:
    """Partes legibles de lo que cambió en un caso (sin tocar la BD).
    `assigned_to` y el código del caso los resuelve el middleware."""
    parts: list[str] = []
    if body.get("status"):
        parts.append(f"estado → {STATUS_LABELS.get(body['status'], body['status'])}")
    if body.get("priority"):
        parts.append(f"prioridad → {PRIORITY_LABELS.get(body['priority'], body['priority'])}")
    if body.get("completion"):
        parts.append(f"servicio {COMPLETION_LABELS.get(body['completion'], body['completion'])}")
    if "sla_due_at" in body:
        parts.append("SLA definido" if body["sla_due_at"] else "SLA quitado")
    if body.get("title") or body.get("description"):
        parts.append("editó detalles")
    return parts


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
