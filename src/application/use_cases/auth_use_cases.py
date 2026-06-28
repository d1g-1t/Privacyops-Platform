from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import structlog

from src.application.dto.auth_dto import LoginRequest, TokenResponse, UserInfoResponse
from src.core.config import settings
from src.core.security import (
    create_paseto_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from src.domain.exceptions import AuthenticationError
from src.infrastructure.database.models import AuditEventModel, UserModel
from src.infrastructure.database.repositories.audit_repository import SqlAlchemyAuditRepository
from src.infrastructure.database.repositories.user_repository import SqlAlchemyUserRepository

logger = structlog.get_logger(__name__)


class AuthUseCases:
    def __init__(
        self,
        user_repo: SqlAlchemyUserRepository,
        audit_repo: SqlAlchemyAuditRepository,
    ) -> None:
        self._user_repo = user_repo
        self._audit = audit_repo

    async def login(self, request: LoginRequest) -> TokenResponse:
        user = await self._user_repo.get_by_email(request.email)
        if not user:
            raise AuthenticationError("Invalid credentials")

        if not verify_password(request.password, user.hashed_password):
            raise AuthenticationError("Invalid credentials")

        if not user.is_active:
            raise AuthenticationError("Account is deactivated")

        access_token = create_paseto_token(
            user_id=str(user.id),
            tenant_id=str(user.tenant_id),
            role=user.role,
        )
        refresh_token = create_refresh_token(
            secret=settings.paseto_secret_key,
            user_id=UUID(str(user.id)),
            tenant_id=UUID(str(user.tenant_id)),
            ttl_days=settings.refresh_token_ttl_days,
        )

        user.last_login_at = datetime.now(UTC)
        await self._user_repo.update(user)

        await self._audit.record(
            AuditEventModel(
                tenant_id=str(user.tenant_id),
                actor_user_id=str(user.id),
                resource_type="auth",
                resource_id=str(user.id),
                event_type="LOGIN",
                payload={"email": request.email},
            )
        )
        logger.info("user_logged_in", user_id=str(user.id))
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def me(self, user_id: UUID) -> UserInfoResponse:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise AuthenticationError("User not found")
        return UserInfoResponse(
            user_id=str(user.id),
            email=user.email,
            role=user.role,
            tenant_id=str(user.tenant_id),
        )

    async def register(
        self,
        tenant_id: UUID,
        email: str,
        password: str,
        role: str = "viewer",
    ) -> UserInfoResponse:
        existing = await self._user_repo.get_by_email(email)
        if existing:
            raise AuthenticationError("Email already registered")

        hashed = hash_password(password)
        user = UserModel(
            tenant_id=str(tenant_id),
            email=email,
            hashed_password=hashed,
            role=role,
            is_active=True,
        )
        saved = await self._user_repo.save(user)

        await self._audit.record(
            AuditEventModel(
                tenant_id=str(tenant_id),
                resource_type="user",
                resource_id=str(saved.id),
                event_type="REGISTERED",
                payload={"email": email, "role": role},
            )
        )
        logger.info("user_registered", user_id=str(saved.id))
        return UserInfoResponse(
            user_id=str(saved.id),
            email=saved.email,
            role=saved.role,
            tenant_id=str(saved.tenant_id),
        )
