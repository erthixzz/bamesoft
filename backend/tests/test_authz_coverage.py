"""Gate de autorización: ninguna mutación puede quedar sin guard.

Recorre TODAS las rutas registradas en la app y exige que cada endpoint que
modifica estado (POST/PUT/PATCH/DELETE) tenga:

1. un guard de **rol** (`require_role` y derivados) — defensa base hardcodeada, y
2. un control de **capacidad** (`requires(...)`) — la matriz configurable
   Roles/Permisos que administra el super admin.

Sin esto, añadir un endpoint nuevo y olvidar el guard pasa desapercibido hasta
que alguien lo encuentra desde fuera. Es el mismo patrón que
`test_rls_coverage.py`, pero para la capa de API.

Las LECTURAS quedan fuera a propósito: las capacidades son permisos de
navegación y las páginas componen datos de varios módulos (`/cases` lee equipos,
usuarios y sectores). Los GET se protegen con rol + `clinic_scope`, y el
aislamiento por clínica lo cubre `test_tenant_isolation.py`.
"""
from __future__ import annotations

from fastapi.routing import APIRoute

from app.main import create_app

MUTATING = {"POST", "PUT", "PATCH", "DELETE"}

# Rutas que legítimamente no llevan guard. Añadir aquí exige justificarlo.
EXEMPT_PATHS: dict[str, str] = {
    "/api/v1/auth/login": "el login es la puerta de entrada: aún no hay usuario",
}


def _mutating_routes() -> list[APIRoute]:
    app = create_app()
    return [
        r
        for r in app.routes
        if isinstance(r, APIRoute)
        and (r.methods or set()) & MUTATING
        and r.path not in EXEMPT_PATHS
    ]


def _dependency_calls(route: APIRoute) -> list[object]:
    """Todas las funciones-dependencia del árbol de la ruta (recursivo)."""
    found: list[object] = []
    pending = list(route.dependant.dependencies)
    while pending:
        dep = pending.pop()
        if dep.call is not None:
            found.append(dep.call)
        pending.extend(dep.dependencies)
    return found


def test_hay_rutas_que_auditar() -> None:
    """Guarda del guarda: si la introspección deja de encontrar rutas, el gate
    pasaría en vacío."""
    routes = _mutating_routes()
    assert len(routes) >= 20, f"Solo se detectaron {len(routes)} mutaciones"


def test_toda_mutacion_tiene_guard_de_rol() -> None:
    missing = [
        f"{sorted(r.methods or [])} {r.path}"
        for r in _mutating_routes()
        if not any(hasattr(c, "__guard_roles__") for c in _dependency_calls(r))
    ]
    assert not missing, (
        "Mutaciones sin guard de rol:\n  " + "\n  ".join(sorted(missing))
        + "\nAñade `Depends(require_engineer)` (o el guard que corresponda)."
    )


def test_toda_mutacion_tiene_control_de_capacidad() -> None:
    missing = [
        f"{sorted(r.methods or [])} {r.path}"
        for r in _mutating_routes()
        if not any(hasattr(c, "__capability__") for c in _dependency_calls(r))
    ]
    assert not missing, (
        "Mutaciones sin control de capacidad:\n  " + "\n  ".join(sorted(missing))
        + '\nAñade `dependencies=[Depends(requires("<capacidad>", "<modulo>"))]`.'
    )
