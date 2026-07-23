"""Base repository helpers."""

from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")


class Repository(Generic[ModelT]):
    """Minimal async repository for common persistence operations."""

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, instance: ModelT) -> ModelT:
        """Persist and refresh a model instance."""
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get(self, id_: str) -> ModelT | None:
        """Fetch one instance by primary key."""
        return await self.session.get(self.model, id_)

    async def list(self, stmt: Select[tuple[ModelT]] | None = None) -> Sequence[ModelT]:
        """Return model instances for a select statement."""
        result = await self.session.execute(stmt or select(self.model))
        return result.scalars().all()

