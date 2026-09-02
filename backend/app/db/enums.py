"""Enums de dominio."""
from __future__ import annotations

from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"  # Super admin global (ve/gestiona todas las clínicas)
    CLINIC_ADMIN = "clinic_admin"  # Admin de una clínica (scoped a su clínica)
    ENGINEER = "engineer"
    CLIENT = "client"
    SERVICE = "service"
    SUPPORT = "support"


class EquipmentStatus(StrEnum):
    OPERATIONAL = "operational"
    OUT_OF_SERVICE = "out_of_service"
    UNDER_MAINTENANCE = "under_maintenance"
    RETIRED = "retired"


class RiskClass(StrEnum):
    """Clasificación de riesgo (INVIMA / FDA / IEC 62366 simplificado)."""

    I = "I"
    IIA = "IIa"
    IIB = "IIb"
    III = "III"


class CaseType(StrEnum):
    CORRECTIVE = "corrective"
    PREVENTIVE = "preventive"
    CALIBRATION = "calibration"
    INSTALLATION = "installation"
    INSPECTION = "inspection"
    MISHANDLING = "mishandling"  # Daño por mal manejo


class CaseStatus(StrEnum):
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    WAITING_PARTS = "waiting_parts"
    WAITING_CLIENT = "waiting_client"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class CasePriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CaseCompletion(StrEnum):
    """Estado final del servicio realizado en el caso."""

    COMPLETE = "complete"
    INCOMPLETE = "incomplete"


class TecnovigilanciaStage(StrEnum):
    """Etapa del proceso de tecnovigilancia (evento adverso con el dispositivo)."""

    DETECTION = "detection"
    REPORT = "report"
    INVESTIGATION = "investigation"
    CORRECTIVE_ACTION = "corrective_action"
    FOLLOW_UP = "follow_up"
    CLOSED = "closed"


# Satisfacción del servicio: escala Likert de 7 puntos (1 = Muy insatisfecho …
# 7 = Muy satisfecho). Sustituye al enum de 3 caritas `case_satisfaction`, que
# quedó obsoleto en la migración 0015 (ver infra/supabase/migrations).
SATISFACTION_MIN = 1
SATISFACTION_MAX = 7

SATISFACTION_LABELS: dict[int, str] = {
    1: "Muy insatisfecho",
    2: "Insatisfecho",
    3: "Algo insatisfecho",
    4: "Neutral",
    5: "Algo satisfecho",
    6: "Satisfecho",
    7: "Muy satisfecho",
}

#: Agrupación para KPIs: 5-7 positivo, 4 neutral, 1-3 negativo.
SATISFACTION_POSITIVE = (5, 6, 7)
SATISFACTION_NEUTRAL = (4,)
SATISFACTION_NEGATIVE = (1, 2, 3)


class AlertType(StrEnum):
    PREVENTIVE_DUE = "preventive_due"
    CALIBRATION_DUE = "calibration_due"
    WARRANTY_EXPIRING = "warranty_expiring"
    CASE_SLA = "case_sla"
    CUSTOM = "custom"


class AlertSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class DocumentType(StrEnum):
    MANUAL = "manual"
    CERTIFICATE = "certificate"
    REPORT = "report"
    STANDARD = "standard"
    INVOICE = "invoice"
    LIFE_SHEET = "life_sheet"
    PHOTO = "photo"
    SIGNATURE = "signature"
    TECNOVIGILANCIA = "tecnovigilancia"
    OTHER = "other"
