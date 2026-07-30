"""Content addressing and resolution.

The seam between *what* content is wanted and *where* its bytes come from.
``UnitId`` is the addressing scheme; sources added in later work resolve those
IDs to bytes.
"""

from prompticorn.content.errors import ContentError, InvalidUnitIdError
from prompticorn.content.unit_id import UnitId
from prompticorn.content.unit_kind import UnitKind

__all__ = [
    "ContentError",
    "InvalidUnitIdError",
    "UnitId",
    "UnitKind",
]
