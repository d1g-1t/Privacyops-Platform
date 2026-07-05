from __future__ import annotations

from typing import Any

from fastapi import Depends, HTTPException, status

from src.domain.value_objects.user_role import UserRole
from src.infrastructure.security.paseto_handler import get_current_user


class RequireRole:

    def __init__(self, *allowed_roles: UserRole) -> None:
        self._allowed = {r.value for r in allowed_roles}

    async def __call__(self, user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
        if user.get("role") not in self._allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required roles: {', '.join(self._allowed)}",
            )
        return user


require_admin = RequireRole(UserRole.ADMIN)
require_dpo = RequireRole(UserRole.ADMIN, UserRole.DPO)
require_compliance = RequireRole(UserRole.ADMIN, UserRole.DPO, UserRole.COMPLIANCE)
require_legal = RequireRole(UserRole.ADMIN, UserRole.DPO, UserRole.COMPLIANCE, UserRole.LEGAL)
require_viewer = RequireRole(
    UserRole.ADMIN, UserRole.DPO, UserRole.COMPLIANCE, UserRole.LEGAL, UserRole.ANALYST, UserRole.VIEWER
)
