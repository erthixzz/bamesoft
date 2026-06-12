"""Schemas de la Hoja de Vida de Equipo Biomédico (formato MNT-FR-023).

El cuerpo del formato (`LifeSheetData`) se persiste como JSONB. Los campos
compartidos con el equipo (`SharedFields`) se sincronizan contra la fila de
`equipment` en cada guardado, evitando duplicar la fuente de verdad.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.enums import EquipmentStatus, RiskClass


class _Section(BaseModel):
    """Base permisiva: todos los campos opcionales, ignora extras desconocidos."""

    model_config = ConfigDict(extra="ignore")


class Contacto(_Section):
    nombre: str | None = None
    telefono: str | None = None
    correo: str | None = None
    pais: str | None = None


class Componente(_Section):
    nombre: str | None = None
    marca: str | None = None
    modelo: str | None = None
    serie: str | None = None


class Identificacion(_Section):
    activo_fijo: str | None = None
    registro_tipo: str | None = None  # RS | PC | NR
    registro_numero: str | None = None
    codigo_prestador: str | None = None
    sede: str | None = None
    distintivo: str | None = None
    descripcion: str | None = None


class Equipo(_Section):
    tipo: str | None = None  # p.ej. "Aspirador portátil"
    referencia_lote: str | None = None
    servicio: str | None = None
    ubicacion_texto: str | None = None
    movilidad: str | None = None  # movil | fijo


class RegistroHistorico(_Section):
    forma_adquisicion: str | None = None  # compra | comodato | donacion | alquiler
    documento_adquisicion: str | None = None  # orden_compra | factura | contrato
    acta_recibo: date | None = None
    fecha_instalacion: date | None = None
    inicio_operacion: date | None = None
    fecha_fabricacion: date | None = None
    tec_predominante: list[str] = Field(default_factory=list)
    costo: float | None = None
    moneda: str | None = "COP"
    vida_util_anios: int | None = None
    proveedor: Contacto = Field(default_factory=Contacto)
    representante: Contacto = Field(default_factory=Contacto)
    fabricante: Contacto = Field(default_factory=Contacto)


class Rangos(_Section):
    voltaje: str | None = None
    corriente: str | None = None
    potencia: str | None = None
    humedad: str | None = None
    temperatura: str | None = None
    frecuencia: str | None = None
    presion: str | None = None
    velocidad: str | None = None


class Tecnico(_Section):
    fuente_alimentacion: list[str] = Field(default_factory=list)
    voltaje_max: str | None = None
    voltaje_min: str | None = None
    corriente_max: str | None = None
    corriente_min: str | None = None
    potencia: str | None = None
    frecuencia: str | None = None
    presion: str | None = None
    velocidad: str | None = None
    peso: str | None = None
    temperatura: str | None = None
    otros: str | None = None
    rangos: Rangos = Field(default_factory=Rangos)
    accesorios: str | None = None
    recomendaciones: str | None = None


class ApoyoTecnico(_Section):
    manuales: list[str] = Field(default_factory=list)  # operacion | mtto | partes
    planos: list[str] = Field(default_factory=list)  # electronico | electrico | ...
    clas_biomedica: list[str] = Field(default_factory=list)


class Mantenimiento(_Section):
    frec_mantenimiento: str | None = None
    requiere_calibracion: bool | None = None
    frec_calibracion: str | None = None


class LifeSheetData(_Section):
    identificacion: Identificacion = Field(default_factory=Identificacion)
    equipo: Equipo = Field(default_factory=Equipo)
    registro_historico: RegistroHistorico = Field(default_factory=RegistroHistorico)
    tecnico: Tecnico = Field(default_factory=Tecnico)
    apoyo_tecnico: ApoyoTecnico = Field(default_factory=ApoyoTecnico)
    componentes: list[Componente] = Field(default_factory=list)
    mantenimiento: Mantenimiento = Field(default_factory=Mantenimiento)


class SharedFields(BaseModel):
    """Campos que viven en `equipment` y se sincronizan al guardar la hoja."""

    name: str | None = None
    brand: str | None = None
    model: str | None = None
    serial_number: str | None = None
    manufacturer: str | None = None
    risk_class: RiskClass | None = None
    status: EquipmentStatus | None = None
    location_id: uuid.UUID | None = None
    acquisition_date: date | None = None
    warranty_until: date | None = None
    image_url: str | None = None
    notes: str | None = None


class LifeSheetUpdate(BaseModel):
    data: LifeSheetData = Field(default_factory=LifeSheetData)
    formato_codigo: str | None = None
    formato_fecha: str | None = None
    shared: SharedFields = Field(default_factory=SharedFields)


class ClinicHeader(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    logo_url: str | None = None


class LifeSheetOut(BaseModel):
    """Hoja de vida + datos compartidos del equipo + encabezado de la clínica."""

    equipment_id: uuid.UUID
    code: str
    formato_codigo: str
    formato_fecha: str | None = None
    clinic: ClinicHeader | None = None
    shared: SharedFields
    data: LifeSheetData
    created_at: datetime | None = None
    updated_at: datetime | None = None
