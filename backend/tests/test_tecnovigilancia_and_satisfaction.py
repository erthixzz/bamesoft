"""Tecnovigilancia del caso y satisfacción en escala Likert de 7 puntos.

Se prueba contra Postgres real y a través de la API completa porque lo que hay
que verificar es SQL: el enum nativo `tecnovigilancia_stage`, los agregados de
los reportes (`filter(...)`, `avg`, `concat`) y los filtros nuevos. Un mock no
probaría ninguna de esas cosas.
"""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.session import get_session
from app.main import create_app
from app.modules.auth.deps import require_authenticated
from tests.conftest_db import Tenant, requires_db

pytestmark = requires_db


def _client(sessionmaker, actor):
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
        async with sessionmaker() as s:
            from app.modules.users.models import User

            return await s.get(User, actor.id)

    app.dependency_overrides[get_session] = _session_override
    app.dependency_overrides[require_authenticated] = _user_override
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


async def _new_case(client, tenant: Tenant, title: str = "Falla del ventilador") -> dict:
    res = await client.post(
        "/api/v1/cases",
        json={
            "title": title,
            "type": "corrective",
            "equipment_id": str(tenant.equipment.id),
            "assigned_to": str(tenant.user("engineer").id),
        },
    )
    assert res.status_code == 201, res.text
    return res.json()


# --- Tecnovigilancia --------------------------------------------------------


async def test_marcar_y_desmarcar_tecnovigilancia(db_sessionmaker, tenants):
    a, _ = tenants
    async with _client(db_sessionmaker, a.user("engineer")) as client:
        case = await _new_case(client, a)
        assert case["is_tecnovigilancia"] is False

        res = await client.patch(
            f"/api/v1/cases/{case['id']}/tecnovigilancia",
            json={
                "is_tecnovigilancia": True,
                "stage": "investigation",
                "description": "El equipo entregó una dosis mayor a la programada.",
            },
        )
        assert res.status_code == 200, res.text
        marked = res.json()
        assert marked["is_tecnovigilancia"] is True
        assert marked["tecnovigilancia_stage"] == "investigation"
        assert marked["tecnovigilancia_at"] is not None

        # Desmarcar limpia etapa y descripción (lo exige el check de la BD).
        res = await client.patch(
            f"/api/v1/cases/{case['id']}/tecnovigilancia",
            json={"is_tecnovigilancia": False},
        )
        assert res.status_code == 200, res.text
        cleared = res.json()
        assert cleared["is_tecnovigilancia"] is False
        assert cleared["tecnovigilancia_stage"] is None
        assert cleared["tecnovigilancia_description"] is None


async def test_tecnovigilancia_exige_etapa(db_sessionmaker, tenants):
    a, _ = tenants
    async with _client(db_sessionmaker, a.user("engineer")) as client:
        case = await _new_case(client, a)
        res = await client.patch(
            f"/api/v1/cases/{case['id']}/tecnovigilancia",
            json={"is_tecnovigilancia": True},
        )
        assert res.status_code == 422, res.text


async def test_filtro_de_casos_por_tecnovigilancia(db_sessionmaker, tenants):
    a, _ = tenants
    async with _client(db_sessionmaker, a.user("engineer")) as client:
        marked = await _new_case(client, a, "Con evento adverso")
        await _new_case(client, a, "Servicio normal")
        await client.patch(
            f"/api/v1/cases/{marked['id']}/tecnovigilancia",
            json={"is_tecnovigilancia": True, "stage": "detection"},
        )

        only = (await client.get("/api/v1/cases", params={"tecnovigilancia": True})).json()
        assert [c["code"] for c in only] == [marked["code"]]

        rest = (await client.get("/api/v1/cases", params={"tecnovigilancia": False})).json()
        assert marked["code"] not in [c["code"] for c in rest]


async def test_reporte_de_tecnovigilancia(db_sessionmaker, tenants):
    a, _ = tenants
    async with _client(db_sessionmaker, a.user("engineer")) as client:
        case = await _new_case(client, a)
        await client.patch(
            f"/api/v1/cases/{case['id']}/tecnovigilancia",
            json={"is_tecnovigilancia": True, "stage": "report", "description": "Quemadura leve."},
        )

        res = await client.get("/api/v1/reports/tecnovigilancia")
        assert res.status_code == 200, res.text
        rep = res.json()
        assert rep["total"] == 1
        assert rep["open_total"] == 1  # 'report' no es la etapa de cierre
        assert rep["items"][0]["stage"] == "report"
        assert rep["items"][0]["description"] == "Quemadura leve."
        assert rep["items"][0]["equipment_label"].startswith(a.equipment.code)
        # Las 6 etapas siempre vienen, con 0 donde no hay casos.
        by_stage = {r["label"]: r["value"] for r in rep["by_stage"]}
        assert by_stage["report"] == 1 and by_stage["closed"] == 0
        assert len(rep["by_stage"]) == 6
        assert rep["by_equipment"][0]["value"] == 1

        # Filtro por etapa.
        empty = (
            await client.get("/api/v1/reports/tecnovigilancia", params={"stage": "closed"})
        ).json()
        assert empty["items"] == []


async def test_tecnovigilancia_aislada_por_clinica(db_sessionmaker, tenants):
    a, b = tenants
    async with _client(db_sessionmaker, a.user("engineer")) as ca:
        case = await _new_case(ca, a)
        await ca.patch(
            f"/api/v1/cases/{case['id']}/tecnovigilancia",
            json={"is_tecnovigilancia": True, "stage": "detection"},
        )

    async with _client(db_sessionmaker, b.user("clinic_admin")) as cb:
        rep = (await cb.get("/api/v1/reports/tecnovigilancia")).json()
        assert rep["total"] == 0 and rep["items"] == []

        # Tampoco puede marcar un caso de la clínica A.
        res = await cb.patch(
            f"/api/v1/cases/{case['id']}/tecnovigilancia",
            json={"is_tecnovigilancia": True, "stage": "report"},
        )
        assert res.status_code == 404


# --- Satisfacción (Likert 1-7) ---------------------------------------------


@pytest.mark.parametrize("score", [0, 8, -1])
async def test_satisfaccion_fuera_de_la_escala_se_rechaza(db_sessionmaker, tenants, score):
    a, _ = tenants
    async with _client(db_sessionmaker, a.user("engineer")) as client:
        case = await _new_case(client, a)
        res = await client.patch(
            f"/api/v1/cases/{case['id']}", json={"satisfaction_score": score}
        )
        assert res.status_code == 422, res.text


async def test_satisfaccion_se_guarda_y_se_limpia_al_reabrir(db_sessionmaker, tenants):
    a, _ = tenants
    async with _client(db_sessionmaker, a.user("engineer")) as client:
        case = await _new_case(client, a)
        res = await client.patch(
            f"/api/v1/cases/{case['id']}",
            json={"satisfaction_score": 6, "completion": "complete", "status": "closed"},
        )
        assert res.status_code == 200, res.text
        assert res.json()["satisfaction_score"] == 6

        # Reabrir borra el cierre: la calificación anterior ya no representa nada.
        reopened = (
            await client.patch(f"/api/v1/cases/{case['id']}", json={"status": "in_progress"})
        ).json()
        assert reopened["satisfaction_score"] is None


async def test_metricas_de_satisfaccion_en_reportes(db_sessionmaker, tenants):
    a, _ = tenants
    async with _client(db_sessionmaker, a.user("engineer")) as client:
        # 7 y 6 → satisfechos · 4 → neutral · 2 → insatisfecho. Promedio = 4.75.
        for score in (7, 6, 4, 2):
            case = await _new_case(client, a, f"Caso {score}")
            await client.patch(
                f"/api/v1/cases/{case['id']}",
                json={"satisfaction_score": score, "completion": "complete", "status": "closed"},
            )

        prod = (await client.get("/api/v1/reports/productivity")).json()
        assert prod["sat_count"] == 4
        assert prod["sat_avg"] == 4.75
        assert prod["sat_positive"] == 2
        assert prod["sat_neutral"] == 1
        assert prod["sat_negative"] == 1
        assert prod["items"][0]["sat_avg"] == 4.75

        # La distribución trae siempre los 7 puntos, en orden.
        breakdown = (await client.get("/api/v1/reports/breakdown")).json()
        dist = {r["label"]: r["value"] for r in breakdown["by_satisfaction"]}
        assert [r["label"] for r in breakdown["by_satisfaction"]] == list("1234567")
        assert dist["7"] == 1 and dist["6"] == 1 and dist["4"] == 1 and dist["2"] == 1
        assert dist["1"] == 0 and dist["3"] == 0 and dist["5"] == 0


async def test_filtros_de_satisfaccion_en_servicios(db_sessionmaker, tenants):
    a, _ = tenants
    async with _client(db_sessionmaker, a.user("engineer")) as client:
        for score in (7, 4, 2):
            case = await _new_case(client, a, f"Caso {score}")
            await client.patch(
                f"/api/v1/cases/{case['id']}",
                json={"satisfaction_score": score, "completion": "complete", "status": "closed"},
            )

        satisfied = (
            await client.get(
                "/api/v1/reports/services", params={"satisfaction_min": 5, "satisfaction_max": 7}
            )
        ).json()
        assert [r["satisfaction_score"] for r in satisfied["items"]] == [7]

        unhappy = (
            await client.get("/api/v1/reports/services", params={"satisfaction_max": 3})
        ).json()
        assert [r["satisfaction_score"] for r in unhappy["items"]] == [2]
