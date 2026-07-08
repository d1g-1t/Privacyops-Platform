from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from src.domain.value_objects.user_role import UserRole
from src.infrastructure.security.paseto_handler import get_current_user


def _require_role(*allowed_roles: UserRole) -> Callable[..., dict[str, Any]]:
    allowed = {r.value for r in allowed_roles}

    async def _dependency(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
        if user.get("role") not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required roles: {', '.join(allowed)}",
            )
        return user

    return _dependency


require_admin = _require_role(UserRole.ADMIN)
require_dpo = _require_role(UserRole.ADMIN, UserRole.DPO)
require_compliance = _require_role(UserRole.ADMIN, UserRole.DPO, UserRole.COMPLIANCE)
require_legal = _require_role(UserRole.ADMIN, UserRole.DPO, UserRole.COMPLIANCE, UserRole.LEGAL)
require_viewer = _require_role(
    UserRole.ADMIN, UserRole.DPO, UserRole.COMPLIANCE, UserRole.LEGAL, UserRole.ANALYST, UserRole.VIEWER
)
