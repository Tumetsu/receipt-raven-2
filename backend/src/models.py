"""ORM model aggregator.

ORM models live per module under ``src/infrastructure/<module>/orm/``. This
module imports every one of them so they are registered on ``Base.metadata``,
which Alembic autogenerate and the test database read. Add each new model here.
"""

from src.database import Base
from src.infrastructure.notes.orm.note_model import NoteModel

__all__ = ["Base", "NoteModel"]
