from __future__ import annotations

from dependency_injector import containers, providers

from src.core.config import Settings
from src.infrastructure.cache.redis_cache import RedisCache
from src.infrastructure.database.session import async_session_factory, create_async_engine
from src.infrastructure.database.repositories.activity_repository import (
    SqlAlchemyActivityRepository,
)
from src.infrastructure.database.repositories.audit_repository import (
    SqlAlchemyAuditRepository,
)
from src.infrastructure.database.repositories.consent_repository import (
    SqlAlchemyConsentRepository,
)
from src.infrastructure.database.repositories.dsr_repository import (
    SqlAlchemyDSRRepository,
)
from src.infrastructure.database.repositories.evidence_repository import (
    SqlAlchemyEvidenceRepository,
)
from src.infrastructure.database.repositories.incident_repository import (
    SqlAlchemyIncidentRepository,
)
from src.infrastructure.database.repositories.processor_repository import (
    SqlAlchemyProcessorRepository,
)
from src.infrastructure.database.repositories.user_repository import (
    SqlAlchemyUserRepository,
)


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["src.presentation", "src.application"],
    )

    config = providers.Singleton(Settings)

    db_engine = providers.Singleton(
        create_async_engine,
        url=config.provided.database_url,
    )
    db_session_factory = providers.Singleton(
        async_session_factory,
        engine=db_engine,
    )

    redis_cache = providers.Singleton(
        RedisCache,
        url=config.provided.redis_url,
    )

    activity_repo = providers.Factory(
        SqlAlchemyActivityRepository,
        session_factory=db_session_factory,
    )
    consent_repo = providers.Factory(
        SqlAlchemyConsentRepository,
        session_factory=db_session_factory,
    )
    dsr_repo = providers.Factory(
        SqlAlchemyDSRRepository,
        session_factory=db_session_factory,
    )
    processor_repo = providers.Factory(
        SqlAlchemyProcessorRepository,
        session_factory=db_session_factory,
    )
    incident_repo = providers.Factory(
        SqlAlchemyIncidentRepository,
        session_factory=db_session_factory,
    )
    evidence_repo = providers.Factory(
        SqlAlchemyEvidenceRepository,
        session_factory=db_session_factory,
    )
    audit_repo = providers.Factory(
        SqlAlchemyAuditRepository,
        session_factory=db_session_factory,
    )
    user_repo = providers.Factory(
        SqlAlchemyUserRepository,
        session_factory=db_session_factory,
    )
