from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from src.infrastructure.database.models import UserModel
from src.infrastructure.database.repositories.base import SqlAlchemyBaseRepository


class SqlAlchemyUserRepository(SqlAlchemyBaseRepository[UserModel]):
    model_class = UserModel

    async def get_by_email(self, email: str) -> UserModel | None:
        async with self._session_factory() as session:
            stmt = select(UserModel).where(UserModel.email == email)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_id(self, entity_id: UUID) -> UserModel | None:
        async with self._session_factory() as session:
            return await session.get(UserModel, str(entity_id))
