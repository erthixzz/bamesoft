from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class DashboardKPIs(BaseModel):
    equipment_total: int
    equipment_operational: int
    equipment_out_of_service: int
    cases_open: int
    cases_in_progress: int
    cases_closed_30d: int
    preventive_due_30d: int
    calibrations_due_30d: int
    avg_close_time_hours: float | None = None
    # Conteo de casos por cada estado (open, assigned, in_progress, …).
    cases_by_status: dict[str, int] = Field(default_factory=dict)


class ComplianceItem(BaseModel):
    standard_code: str
    standard_name: str
    coverage_pct: float
    equipment_with: int
    equipment_total: int


class ComplianceReport(BaseModel):
    items: list[ComplianceItem]
    total: int


class ProductivityRow(BaseModel):
    """Métricas de productividad por ingeniero (en el rango consultado)."""

    engineer_id: str | None = None
    engineer_name: str
    attended: int = 0
    completed: int = 0
    incomplete: int = 0
    closed: int = 0
    # Tiempos promedio (horas) de cada tramo del flujo de servicio.
    avg_response_hours: float | None = None  # asignado → tomado
    avg_to_start_hours: float | None = None  # tomado → inicio de trabajo
    avg_work_hours: float | None = None  # inicio → fin
    fcr_count: int = 0  # resueltos completos a la primera (FCR)
    fcr_pct: float = 0.0
    # Satisfacción (Likert 1-7) de quien recibe el servicio, solo casos cerrados.
    sat_count: int = 0  # respuestas con calificación
    sat_avg: float | None = None  # promedio sobre 7
    sat_positive: int = 0  # 5-7 (algo satisfecho → muy satisfecho)
    sat_neutral: int = 0  # 4 (neutral)
    sat_negative: int = 0  # 1-3 (algo insatisfecho → muy insatisfecho)


class ProductivityReport(BaseModel):
    items: list[ProductivityRow]
    attended: int = 0
    completed: int = 0
    incomplete: int = 0
    fcr_count: int = 0
    fcr_pct: float = 0.0
    sat_count: int = 0
    sat_avg: float | None = None
    sat_positive: int = 0
    sat_neutral: int = 0
    sat_negative: int = 0


class DailyPoint(BaseModel):
    day: str
    reported: int = 0
    closed: int = 0


class ReporterRow(BaseModel):
    user_id: str | None = None
    name: str
    count: int = 0


class OperationsReport(BaseModel):
    """Operación de casos: llamadas/día, incompletos, en espera, por reportante."""

    reported_total: int = 0
    closed_total: int = 0
    complete_total: int = 0
    incomplete_total: int = 0
    active_total: int = 0
    waiting_total: int = 0
    cancelled_total: int = 0
    waiting_now: int = 0
    daily: list[DailyPoint] = Field(default_factory=list)
    by_reporter: list[ReporterRow] = Field(default_factory=list)


class EquipmentReportRow(BaseModel):
    """Servicio agregado por equipo (en el rango consultado)."""

    equipment_id: str
    code: str
    name: str
    sector_name: str | None = None
    cases_total: int = 0
    completed: int = 0
    incomplete: int = 0
    corrective: int = 0
    preventive: int = 0
    avg_work_hours: float | None = None
    total_operation_minutes: int = 0
    last_service_at: datetime | None = None


class EquipmentReport(BaseModel):
    items: list[EquipmentReportRow] = Field(default_factory=list)
    total: int = 0


class ServiceRow(BaseModel):
    """Detalle de un servicio: qué se hizo, quién y los tiempos del flujo."""

    case_id: str
    code: str
    title: str
    equipment_label: str
    engineer_name: str | None = None
    type: str
    status: str
    completion: str | None = None
    #: Satisfacción en escala Likert de 7 puntos (1-7); None si aún sin calificar.
    satisfaction_score: int | None = None
    is_tecnovigilancia: bool = False
    tecnovigilancia_stage: str | None = None
    work_performed: str | None = None
    operation_minutes: int | None = None
    opened_at: datetime | None = None
    assigned_at: datetime | None = None
    accepted_at: datetime | None = None
    work_started_at: datetime | None = None
    finished_at: datetime | None = None
    closed_at: datetime | None = None


class ServicesReport(BaseModel):
    items: list[ServiceRow] = Field(default_factory=list)
    total: int = 0


class NamedCount(BaseModel):
    label: str
    value: int = 0


class BreakdownReport(BaseModel):
    """Distribuciones para gráficas (rango + clínica)."""

    by_status: list[NamedCount] = Field(default_factory=list)
    by_type: list[NamedCount] = Field(default_factory=list)
    by_priority: list[NamedCount] = Field(default_factory=list)
    by_sector: list[NamedCount] = Field(default_factory=list)
    monthly: list[NamedCount] = Field(default_factory=list)  # label = 'YYYY-MM'
    #: Satisfacción Likert: label = '1'…'7'; siempre los 7 puntos (0 si no hay).
    by_satisfaction: list[NamedCount] = Field(default_factory=list)


class TecnovigilanciaRow(BaseModel):
    """Un caso marcado como evento de tecnovigilancia."""

    case_id: str
    code: str
    title: str
    equipment_label: str
    sector_name: str | None = None
    engineer_name: str | None = None
    status: str
    priority: str
    stage: str | None = None
    description: str | None = None
    marked_at: datetime | None = None
    opened_at: datetime | None = None
    closed_at: datetime | None = None


class TecnovigilanciaReport(BaseModel):
    """Casos de tecnovigilancia del rango, con su distribución por etapa."""

    items: list[TecnovigilanciaRow] = Field(default_factory=list)
    total: int = 0
    #: Marcados pero aún no cerrados en el proceso de tecnovigilancia.
    open_total: int = 0
    by_stage: list[NamedCount] = Field(default_factory=list)
    #: Equipos con más eventos de tecnovigilancia en el rango.
    by_equipment: list[NamedCount] = Field(default_factory=list)
