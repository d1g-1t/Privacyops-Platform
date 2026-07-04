from __future__ import annotations

from fastapi import APIRouter

from src.presentation.api.v1.activities import router as activities_router
from src.presentation.api.v1.analytics import router as analytics_router
from src.presentation.api.v1.audit import router as audit_router
from src.presentation.api.v1.auth import router as auth_router
from src.presentation.api.v1.consents import router as consents_router
from src.presentation.api.v1.dsr import router as dsr_router
from src.presentation.api.v1.health import router as health_router
from src.presentation.api.v1.incidents import router as incidents_router
from src.presentation.api.v1.processors import router as processors_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(activities_router)
api_v1_router.include_router(consents_router)
api_v1_router.include_router(dsr_router)
api_v1_router.include_router(processors_router)
api_v1_router.include_router(incidents_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(audit_router)
