from __future__ import annotations

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


class ProductivityReport(BaseModel):
    items: list[ProductivityRow]
    attended: int = 0
    completed: int = 0
    incomplete: int = 0
    fcr_count: int = 0
    fcr_pct: float = 0.0


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
    waiting_now: int = 0
    daily: list[DailyPoint] = Field(default_factory=list)
    by_reporter: list[ReporterRow] = Field(default_factory=list)
