"""
Base class for Aggregate Roots.

An Aggregate Root is the entry point to an aggregate: a cluster of domain
objects treated as one unit. All external references go through the root, and
the root enforces every invariant of the aggregate.

Example:
    @dataclass
    class Note(AggregateRoot[NoteId]):
        id: NoteId
        title: str

        def rename(self, title: str) -> None:
            if not title.strip():
                raise ValidationError("Note title cannot be empty")
            self.title = title
"""

from .entity import Entity, EntityId


class AggregateRoot[IdType: EntityId](Entity[IdType]):
    """
    Base class for Aggregate Roots in the domain model.

    Aggregate Roots are:
    - The entry point to an aggregate (cluster of related entities)
    - Responsible for maintaining invariants
    - The only entity referenced from outside the aggregate, and only by id
    """
