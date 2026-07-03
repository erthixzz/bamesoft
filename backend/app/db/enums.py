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
    OTHER = "other"
