"""Aggregator de modelos — usado por Alembic para autogenerate.

Importar este módulo registra todos los modelos en `Base.metadata`. No
importar desde otros módulos del backend para evitar ciclos.
"""
from __future__ import annotations

from app.db.base import Base  # noqa: F401
from app.modules.access.models import ClinicFeature, RolePermission  # noqa: F401
from app.modules.alerts.models import Alert  # noqa: F401
from app.modules.calibrations.models import Calibration  # noqa: F401
from app.modules.cases.models import Case, CaseActivity  # noqa: F401
from app.modules.clinics.models import Clinic, Location  # noqa: F401
from app.modules.documents.models import Document  # noqa: F401
from app.modules.equipment.models import (  # noqa: F401
    Equipment,
    EquipmentCategory,
    EquipmentLifeSheet,
)
from app.modules.maintenance.models import MaintenanceSchedule  # noqa: F401
from app.modules.sectors.models import Sector  # noqa: F401
from app.modules.standards.models import EquipmentStandard, Standard  # noqa: F401
from app.modules.users.models import User  # noqa: F401
