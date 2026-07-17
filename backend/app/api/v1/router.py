"""Aggregator: combina los routers de cada módulo bajo /api/v1."""
from __future__ import annotations

from fastapi import APIRouter

from app.modules.access.routes import router as access_router
from app.modules.alerts.routes import router as alerts_router
from app.modules.audit.routes import router as audit_router
from app.modules.auth.routes import router as auth_router
from app.modules.calibrations.routes import router as calibrations_router
from app.modules.cases.routes import router as cases_router
from app.modules.clinics.routes import router as clinics_router
from app.modules.documents.routes import router as documents_router
from app.modules.equipment.routes import router as equipment_router
from app.modules.maintenance.routes import router as maintenance_router
from app.modules.public.routes import router as public_router
from app.modules.reports.routes import router as reports_router
from app.modules.search.routes import router as search_router
from app.modules.sectors.routes import router as sectors_router
from app.modules.standards.routes import router as standards_router
from app.modules.users.routes import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(clinics_router)
api_router.include_router(equipment_router)
api_router.include_router(cases_router)
api_router.include_router(calibrations_router)
api_router.include_router(maintenance_router)
api_router.include_router(documents_router)
api_router.include_router(standards_router)
api_router.include_router(alerts_router)
api_router.include_router(sectors_router)
api_router.include_router(reports_router)
api_router.include_router(access_router)
api_router.include_router(audit_router)
api_router.include_router(search_router)
api_router.include_router(public_router)
