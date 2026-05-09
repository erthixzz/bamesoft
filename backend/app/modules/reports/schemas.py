from __future__ import annotations

from pydantic import BaseModel


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


class ComplianceItem(BaseModel):
    standard_code: str
    standard_name: str
    coverage_pct: float
    equipment_with: int
    equipment_total: int


class ComplianceReport(BaseModel):
    items: list[ComplianceItem]
    total: int
