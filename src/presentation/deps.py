from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.cache.redis_cache import RedisCache
from src.infrastructure.database.session import get_session
from src.infrastructure.database.repositories.activity_repository import SqlAlchemyActivityRepository
from src.infrastructure.database.repositories.audit_repository import SqlAlchemyAuditRepository
from src.infrastructure.database.repositories.consent_repository import SqlAlchemyConsentRepository
from src.infrastructure.database.repositories.dsr_repository import SqlAlchemyDSRRepository
from src.infrastructure.database.repositories.evidence_repository import SqlAlchemyEvidenceRepository
from src.infrastructure.database.repositories.incident_repository import SqlAlchemyIncidentRepository
from src.infrastructure.database.repositories.processor_repository import SqlAlchemyProcessorRepository
from src.infrastructure.database.repositories.user_repository import SqlAlchemyUserRepository
from src.infrastructure.security.paseto_handler import get_current_user_payload
from src.application.use_cases.activity_use_cases import ActivityUseCases
from src.application.use_cases.analytics_use_cases import AnalyticsUseCases
from src.application.use_cases.auth_use_cases import AuthUseCases
from src.application.use_cases.consent_use_cases import ConsentUseCases
from src.application.use_cases.dsr_use_cases import DSRUseCases
from src.application.use_cases.incident_use_cases import IncidentUseCases
from src.application.use_cases.processor_use_cases import ProcessorUseCases


DbSession = Annotated[AsyncSession, Depends(get_session)]


async def _get_redis(request: Request) -> RedisCache:
    return request.app.state.redis_cache


def _activity_repo(session: DbSession) -> SqlAlchemyActivityRepository:
    return SqlAlchemyActivityRepository(session)


def _audit_repo(session: DbSession) -> SqlAlchemyAuditRepository:
    return SqlAlchemyAuditRepository(session)


def _consent_repo(session: DbSession) -> SqlAlchemyConsentRepository:
    return SqlAlchemyConsentRepository(session)


def _dsr_repo(session: DbSession) -> SqlAlchemyDSRRepository:
    return SqlAlchemyDSRRepository(session)


def _evidence_repo(session: DbSession) -> SqlAlchemyEvidenceRepository:
    return SqlAlchemyEvidenceRepository(session)


def _incident_repo(session: DbSession) -> SqlAlchemyIncidentRepository:
    return SqlAlchemyIncidentRepository(session)


def _processor_repo(session: DbSession) -> SqlAlchemyProcessorRepository:
    return SqlAlchemyProcessorRepository(session)


def _user_repo(session: DbSession) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session)


def get_activity_use_cases(
    session: DbSession,
    redis: RedisCache = Depends(_get_redis),
) -> ActivityUseCases:
    return ActivityUseCases(
        repo=SqlAlchemyActivityRepository(session),
        audit_repo=SqlAlchemyAuditRepository(session),
        cache=redis,
    )


def get_auth_use_cases(session: DbSession) -> AuthUseCases:
    return AuthUseCases(
        user_repo=SqlAlchemyUserRepository(session),
        audit_repo=SqlAlchemyAuditRepository(session),
    )


def get_consent_use_cases(session: DbSession) -> ConsentUseCases:
    return ConsentUseCases(
        repo=SqlAlchemyConsentRepository(session),
        audit_repo=SqlAlchemyAuditRepository(session),
    )


def get_dsr_use_cases(session: DbSession) -> DSRUseCases:
    return DSRUseCases(
        repo=SqlAlchemyDSRRepository(session),
        audit_repo=SqlAlchemyAuditRepository(session),
    )


def get_incident_use_cases(session: DbSession) -> IncidentUseCases:
    return IncidentUseCases(
        repo=SqlAlchemyIncidentRepository(session),
        audit_repo=SqlAlchemyAuditRepository(session),
    )


def get_processor_use_cases(session: DbSession) -> ProcessorUseCases:
    return ProcessorUseCases(
        repo=SqlAlchemyProcessorRepository(session),
        audit_repo=SqlAlchemyAuditRepository(session),
    )


def get_analytics_use_cases(
    session: DbSession,
    redis: RedisCache = Depends(_get_redis),
) -> AnalyticsUseCases:
    return AnalyticsUseCases(
        activity_repo=SqlAlchemyActivityRepository(session),
        consent_repo=SqlAlchemyConsentRepository(session),
        dsr_repo=SqlAlchemyDSRRepository(session),
        incident_repo=SqlAlchemyIncidentRepository(session),
        processor_repo=SqlAlchemyProcessorRepository(session),
        cache=redis,
    )


CurrentUserPayload = Annotated[dict, Depends(get_current_user_payload)]


def get_current_user_id(payload: CurrentUserPayload) -> UUID:
    return UUID(payload["sub"])


def get_current_tenant_id(payload: CurrentUserPayload) -> UUID:
    return UUID(payload["tenant_id"])


CurrentUserId = Annotated[UUID, Depends(get_current_user_id)]
CurrentTenantId = Annotated[UUID, Depends(get_current_tenant_id)]
