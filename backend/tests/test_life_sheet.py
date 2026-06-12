"""Tests de los schemas de la Hoja de Vida (capa pura, sin DB).

La validación de endpoints/sincronización con `equipment` requiere una BD
Postgres (JSONB + enums) y se cubre en la verificación manual.
"""
from __future__ import annotations

from datetime import date

from app.db.enums import EquipmentStatus, RiskClass
from app.modules.equipment.life_sheet_schemas import (
    LifeSheetData,
    LifeSheetUpdate,
    SharedFields,
)


def test_life_sheet_data_defaults() -> None:
    """Una hoja vacía trae todas las secciones inicializadas."""
    data = LifeSheetData()
    assert data.registro_historico.tec_predominante == []
    assert data.tecnico.fuente_alimentacion == []
    assert data.apoyo_tecnico.manuales == []
    assert data.componentes == []
    assert data.registro_historico.proveedor.nombre is None
    assert data.mantenimiento.requiere_calibracion is None


def test_life_sheet_update_partial() -> None:
    """Un payload parcial llena lo enviado y deja el resto por defecto."""
    payload = LifeSheetUpdate.model_validate(
        {
            "data": {
                "identificacion": {"activo_fijo": "AF-1", "registro_tipo": "NR"},
                "componentes": [{"nombre": "Frasco", "marca": "X"}],
            },
            "shared": {"brand": "Pulmo-Med"},
        }
    )
    assert payload.data.identificacion.activo_fijo == "AF-1"
    assert payload.data.identificacion.registro_tipo == "NR"
    assert payload.data.componentes[0].nombre == "Frasco"
    # Secciones no enviadas conservan defaults.
    assert payload.data.tecnico.fuente_alimentacion == []
    assert payload.shared.brand == "Pulmo-Med"


def test_shared_fields_coercion() -> None:
    """Las cadenas se coercionan a enum/date para sincronizar con equipment."""
    shared = SharedFields.model_validate(
        {
            "risk_class": "IIa",
            "status": "operational",
            "acquisition_date": "2010-04-16",
        }
    )
    assert shared.risk_class is RiskClass.IIA
    assert shared.status is EquipmentStatus.OPERATIONAL
    assert shared.acquisition_date == date(2010, 4, 16)


def test_life_sheet_data_json_serializable() -> None:
    """model_dump(mode=json) produce un dict apto para JSONB (fechas a str)."""
    data = LifeSheetData.model_validate(
        {"registro_historico": {"acta_recibo": "2010-04-16", "costo": 1500.0}}
    )
    dumped = data.model_dump(mode="json")
    assert dumped["registro_historico"]["acta_recibo"] == "2010-04-16"
    assert dumped["registro_historico"]["costo"] == 1500.0


def test_unknown_fields_ignored() -> None:
    """Campos desconocidos no rompen la validación (extra=ignore)."""
    data = LifeSheetData.model_validate(
        {"identificacion": {"campo_inventado": "x", "sede": "CNSR"}}
    )
    assert data.identificacion.sede == "CNSR"
    assert not hasattr(data.identificacion, "campo_inventado")
