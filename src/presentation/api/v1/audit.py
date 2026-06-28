from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.repositories.audit_repository import SqlAlchemyAuditRepository
from src.infrastructure.database.session import get_session
from src.infrastructure.security.rbac import require_admin
from src.presentation.deps import CurrentTenantId

router = APIRouter(prefix="/audit", tags=["audit"], dependencies=[require_admin])


@router.get("", response_class=ORJSONResponse)
async def list_audit_events(
    tenant_id: CurrentTenantId,
    session: AsyncSession = Depends(get_session),
    resource_type: str | None = Query(None),
    resource_id: UUID | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    repo = SqlAlchemyAuditRepository(session)
    events = await repo.list_by_tenant(tenant_id, offset=offset, limit=limit)

    # Client-side filtering (for simplicity; production would push to query)
    if resource_type:
        events = [e for e in events if e.resource_type == resource_type]
    if resource_id:
        events = [e for e in events if str(e.resource_id) == str(resource_id)]

    return [
        {
            "id": str(e.id),
            "tenant_id": str(e.tenant_id),
            "actor_user_id": str(e.actor_user_id) if e.actor_user_id else None,
            "resource_type": e.resource_type,
            "resource_id": str(e.resource_id) if e.resource_id else None,
            "event_type": e.event_type,
            "payload": e.payload,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in events
    ]
