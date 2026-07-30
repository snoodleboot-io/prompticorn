"""Content addressing and resolution.

The seam between *what* content is wanted and *where* its bytes come from.
``UnitId`` is the addressing scheme; a ``ContentSource`` resolves those IDs to
text. Consumers depend on the interface, never on a filesystem path.
"""

from prompticorn.content.builtin_content_source import BuiltinContentSource
from prompticorn.content.content_source import ContentSource
from prompticorn.content.content_unit import BUILTIN_LAYER, ContentUnit
from prompticorn.content.digest import canonical_text, digest_bytes, digest_text
from prompticorn.content.errors import (
    ContentError,
    InvalidUnitIdError,
    SourceUnavailableError,
    UnitNotFoundError,
)
from prompticorn.content.unit_id import UnitId
from prompticorn.content.unit_kind import UnitKind

__all__ = [
    "BUILTIN_LAYER",
    "BuiltinContentSource",
    "ContentError",
    "ContentSource",
    "ContentUnit",
    "InvalidUnitIdError",
    "SourceUnavailableError",
    "UnitId",
    "UnitKind",
    "UnitNotFoundError",
    "canonical_text",
    "digest_bytes",
    "digest_text",
]
