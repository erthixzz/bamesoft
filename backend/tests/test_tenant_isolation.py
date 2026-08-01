"""Aislamiento multi-clínica: la clínica A no puede tocar datos de la B.

Es la garantía más importante del producto, así que se prueba contra Postgres
real y a través de la API completa (routers + dependencias + servicios), no
llamando funciones sueltas.

La autenticación se sustituye por un override de `require_authenticated`: nos
interesa probar la AUTORIZACIÓN, no volver a probar la validación de JWT (que
depende de Supabase). El resto de la cadena —guards de rol, `clinic_scope`,
capacidades y las consultas SQL— se ejecuta de verdad.
"""
from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.session import get_session
from app.main import create_app
from app.modules.auth.deps import require_authenticated
from tests.conftest_db import Tenant, requires_db

pytestmark = requires_db


def _client(sessionmaker, actor):
    """Cliente HTTP autenticado como `actor`, contra la BD de pruebas."""
    app = create_app()

    async def _session_override():
        async with sessionmaker() as s:
            try:
                yield s
                await s.commit()
            except Exception:
                await s.rollback()
                raise

    async def _user_override():
        # Se relee en la sesión activa para que quede adjunto a ella.
        async with sessionmaker() as s:
            from app.modules.users.models import User

            return await s.get(User, actor.id)

    app.dependency_overrides[get_session] = _session_override
    app.dependency_overrides[require_authenticated] = _user_override
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


# --- Lectura cruzada -------------------------------------------------------

@pytest.mark.parametrize(
    "path_for",
    [
        pytest.param(lambda t: f"/api/v1/equipment/{t.equipment.id}", id="equipment-detalle"),
        pytest.param(
            lambda t: f"/api/v1/equipment/{t.equipment.id}/life-sheet", id="hoja-de-vida"
        ),
        pytest.param(
            lambda t: f"/api/v1/maintenance/equipment/{t.equipment.id}", id="mantenimientos"
        ),
        pytest.param(
            lambda t: f"/api/v1/calibrations/equipment/{t.equipment.id}", id="calibraciones"
        ),
        pytest.param(
            lambda t: f"/api/v1/documents/equipment/{t.equipment.id}", id="documentos"
        ),
        pytest.param(lambda t: f"/api/v1/clinics/{t.clinic.id}", id="clinica"),
        pytest.param(lambda t: f"/api/v1/clinics/{t.clinic.id}/locations", id="ubicaciones"),
        pytest.param(lambda t: f"/api/v1/users/{t.user('engineer').id}", id="usuario"),
    ],
)
async def test_no_se_leen_recursos_de_otra_clinica(
    db_sessionmaker, tenants: tuple[Tenant, Tenant], path_for
) -> None:
    a, b = tenants
    async with _client(db_sessionmaker, a.user("clinic_admin")) as c:
        propio = await c.get(path_for(a))
        ajeno = await c.get(path_for(b))

    assert propio.status_code == 200, f"El recurso propio debería verse: {propio.text}"
    assert ajeno.status_code in (403, 404), (
        f"FUGA: se leyó un recurso de otra clínica ({ajeno.status_code}): {ajeno.text[:200]}"
    )


async def test_los_listados_solo_traen_la_clinica_propia(
    db_sessionmaker, tenants: tuple[Tenant, Tenant]
) -> None:
    a, b = tenants
    async with _client(db_sessionmaker, a.user("clinic_admin")) as c:
        equipos = (await c.get("/api/v1/equipment")).json()
        usuarios = (await c.get("/api/v1/users")).json()
        clinicas = (await c.get("/api/v1/clinics")).json()

    assert {e["code"] for e in equipos} == {"EQ-a"}
    assert all(u["email"].endswith("@clinica-a.com") for u in usuarios), usuarios
    assert {cl["id"] for cl in clinicas} == {str(a.clinic.id)}
    assert str(b.clinic.id) not in {cl["id"] for cl in clinicas}


# --- Escritura cruzada -----------------------------------------------------

async def test_no_se_modifica_equipo_de_otra_clinica(
    db_sessionmaker, tenants: tuple[Tenant, Tenant]
) -> None:
    a, b = tenants
    async with _client(db_sessionmaker, a.user("engineer")) as c:
        r = await c.patch(
            f"/api/v1/equipment/{b.equipment.id}", json={"name": "SECUESTRADO"}
        )
    assert r.status_code in (403, 404), f"FUGA de escritura: {r.status_code} {r.text[:200]}"


async def test_no_se_crea_mantenimiento_en_equipo_ajeno(
    db_sessionmaker, tenants: tuple[Tenant, Tenant]
) -> None:
    a, b = tenants
    async with _client(db_sessionmaker, a.user("engineer")) as c:
        r = await c.post(
            "/api/v1/maintenance",
            json={
                "equipment_id": str(b.equipment.id),
                "name": "Preventivo inyectado",
                "frequency_days": 30,
            },
        )
    assert r.status_code in (403, 404), f"FUGA de escritura: {r.status_code} {r.text[:200]}"


async def test_no_se_crea_calibracion_en_equipo_ajeno(
    db_sessionmaker, tenants: tuple[Tenant, Tenant]
) -> None:
    a, b = tenants
    async with _client(db_sessionmaker, a.user("engineer")) as c:
        r = await c.post(
            "/api/v1/calibrations",
            json={
                "equipment_id": str(b.equipment.id),
                "performed_at": "2026-01-15",
                "passed": True,
            },
        )
    assert r.status_code in (403, 404), f"FUGA de escritura: {r.status_code} {r.text[:200]}"


async def test_no_se_mueve_un_usuario_a_otra_clinica(
    db_sessionmaker, tenants: tuple[Tenant, Tenant]
) -> None:
    """Un admin de clínica no puede reasignar a los suyos a otra compañía."""
    a, b = tenants
    victima = a.user("engineer")
    async with _client(db_sessionmaker, a.user("clinic_admin")) as c:
        r = await c.patch(
            f"/api/v1/users/{victima.id}", json={"clinic_id": str(b.clinic.id)}
        )
        assert r.status_code == 200, r.text
        assert r.json()["clinic_id"] == str(a.clinic.id), "El clinic_id fue reasignado"


async def test_admin_de_clinica_no_crea_super_admins(
    db_sessionmaker, tenants: tuple[Tenant, Tenant]
) -> None:
    a, _ = tenants
    async with _client(db_sessionmaker, a.user("clinic_admin")) as c:
        r = await c.post(
            "/api/v1/users",
            json={
                "id": str(uuid.uuid4()),
                "email": "escalada@clinica-a.com",
                "full_name": "Intento de escalada",
                "role": "admin",
            },
        )
    assert r.status_code == 403, f"Escalada de privilegios: {r.status_code} {r.text[:200]}"


# --- Capacidades -----------------------------------------------------------

async def test_capacidad_revocada_bloquea_la_mutacion(
    db_sessionmaker, tenants: tuple[Tenant, Tenant]
) -> None:
    """El corazón del arreglo: apagar la capacidad en la matriz debe cerrar la
    API, no solo esconder el menú."""
    from sqlalchemy import update

    from app.modules.access.models import RolePermission

    a, _ = tenants
    payload = {
        "code": "EQ-nuevo",
        "name": "Equipo nuevo",
        "status": "operational",
        "clinic_id": str(a.clinic.id),
    }

    async with _client(db_sessionmaker, a.user("engineer")) as c:
        permitido = await c.post("/api/v1/equipment", json=payload)
    assert permitido.status_code == 201, permitido.text

    # El admin apaga "engineer -> equipment" en la matriz.
    async with db_sessionmaker() as s:
        await s.execute(
            update(RolePermission)
            .where(
                RolePermission.role == "engineer",
                RolePermission.capability == "equipment",
            )
            .values(enabled=False)
        )
        await s.commit()

    async with _client(db_sessionmaker, a.user("engineer")) as c:
        bloqueado = await c.post("/api/v1/equipment", json={**payload, "code": "EQ-nuevo-2"})
    assert bloqueado.status_code == 403, (
        "La capacidad revocada NO se aplicó: la matriz sigue siendo decorativa "
        f"({bloqueado.status_code})"
    )


async def test_cliente_no_puede_cerrar_casos(
    db_sessionmaker, tenants: tuple[Tenant, Tenant]
) -> None:
    """`client` no tiene la capacidad `close` ni el rol para editar casos."""
    a, _ = tenants
    async with _client(db_sessionmaker, a.user("client")) as c:
        creado = await c.post(
            "/api/v1/cases",
            json={
                "equipment_id": str(a.equipment.id),
                "type": "corrective",
                "title": "Falla reportada por el cliente",
            },
        )
        assert creado.status_code == 201, creado.text  # reportar sí puede
        r = await c.patch(f"/api/v1/cases/{creado.json()['id']}", json={"status": "closed"})
    assert r.status_code == 403, f"Un cliente cerró un caso: {r.status_code} {r.text[:200]}"
