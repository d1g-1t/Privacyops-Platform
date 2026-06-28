from __future__ import annotations

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

M = TypeVar("M")


class SqlAlchemyBaseRepository(Generic[M]):
    model_class: type[M]

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def _session(self) -> AsyncSession:
        return self._session_factory()

    async def get_by_id(self, entity_id: UUID) -> M | None:
        async with self._session_factory() as session:
            return await session.get(self.model_class, str(entity_id))

    async def list_by_tenant(
        self,
        tenant_id: UUID,
        *,
        offset: int = 0,
        limit: int = 50,
        filters: dict[str, Any] | None = None,
    ) -> list[M]:
        async with self._session_factory() as session:
            stmt = (
                select(self.model_class)
                .where(self.model_class.tenant_id == str(tenant_id))
                .offset(offset)
                .limit(limit)
                .order_by(self.model_class.created_at.desc())
            )
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model_class, key):
                        stmt = stmt.where(getattr(self.model_class, key) == value)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def count_by_tenant(
        self,
        tenant_id: UUID,
        *,
        filters: dict[str, Any] | None = None,
    ) -> int:
        async with self._session_factory() as session:
            stmt = (
                select(func.count())
                .select_from(self.model_class)
                .where(self.model_class.tenant_id == str(tenant_id))
            )
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model_class, key):
                        stmt = stmt.where(getattr(self.model_class, key) == value)
            result = await session.execute(stmt)
            return result.scalar_one()

    async def save(self, entity: M) -> M:
        async with self._session_factory() as session:
            session.add(entity)
            await session.commit()
            await session.refresh(entity)
            return entity

    async def update(self, entity: M) -> M:
        async with self._session_factory() as session:
            merged = await session.merge(entity)
            await session.commit()
            await session.refresh(merged)
            return merged

    async def delete(self, entity_id: UUID) -> None:
        async with self._session_factory() as session:
            obj = await session.get(self.model_class, str(entity_id))
            if obj:
                await session.delete(obj)
                await session.commit()
