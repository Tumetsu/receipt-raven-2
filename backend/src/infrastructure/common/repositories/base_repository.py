"""Generic repository base collapsing the common find/save/delete boilerplate.

Simple single-table repositories share one shape: look a row up by id, persist
through a create-vs-update sentinel on the domain id (0 means "not stored
yet"), and delete by id. ``BaseRepository`` provides those operations, so a
concrete repository only implements the queries that are genuinely its own.

When rows become owned by a user, add an ownership filter here (one overridable
``_scoped`` hook applied to every select) rather than in each repository.
"""

from typing import Any, Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.common.entity import EntityId


class _DomainEntity(Protocol):
    """A domain entity carrying a strongly-typed id."""

    @property
    def id(self) -> EntityId: ...


class EntityMapper[TDomain: _DomainEntity, TOrm](Protocol):
    """Bidirectional ORM <-> domain mapper used by :class:`BaseRepository`."""

    def to_domain(self, orm_model: TOrm, /) -> TDomain: ...

    def to_orm(self, domain_entity: TDomain, orm_model: TOrm | None = ..., /) -> TOrm: ...


class BaseRepository[TDomain: _DomainEntity, TOrm]:
    """Common CRUD for simple, single-table entity repositories."""

    def __init__(
        self,
        db: AsyncSession,
        orm_class: type[TOrm],
        mapper: EntityMapper[TDomain, TOrm],
    ) -> None:
        self.db = db
        self._orm_class: Any = orm_class
        self._mapper = mapper

    async def find_by_id(self, entity_id: EntityId, /) -> TDomain | None:
        """Load a single row by id, or ``None`` when absent."""
        orm_model = await self.db.get(self._orm_class, entity_id.value)
        return self._mapper.to_domain(orm_model) if orm_model is not None else None

    async def find_by_ids(self, entity_ids: list[int], /) -> list[TDomain]:
        """Load the rows for the given ids (empty input yields an empty list)."""
        if not entity_ids:
            return []
        stmt = select(self._orm_class).where(self._orm_class.id.in_(entity_ids))
        result = await self.db.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def save(self, entity: TDomain, /) -> TDomain:
        """Insert a new entity (id sentinel ``0``) or update the existing row."""
        if entity.id.value == 0:
            orm_model = self._mapper.to_orm(entity)
            self.db.add(orm_model)
            await self.db.commit()
            await self.db.refresh(orm_model)
            return self._mapper.to_domain(orm_model)

        existing = await self.db.get(self._orm_class, entity.id.value)
        if existing is None:
            raise ValueError(f"{self._orm_class.__name__} {entity.id.value} not found")
        self._mapper.to_orm(entity, existing)
        await self.db.commit()
        await self.db.refresh(existing)
        return self._mapper.to_domain(existing)

    async def delete(self, entity_id: EntityId, /) -> bool:
        """Delete a row by id, returning whether a row was removed."""
        orm_model = await self.db.get(self._orm_class, entity_id.value)
        if orm_model is None:
            return False
        await self.db.delete(orm_model)
        await self.db.commit()
        return True
