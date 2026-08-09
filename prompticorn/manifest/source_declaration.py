"""One entry under the manifest's ``sources:`` key (PRO-109)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from prompticorn.manifest.errors import ManifestSchemaError
from prompticorn.manifest.schema_values import (
    reject_unknown_keys,
    require_mapping,
    required_string,
)
from prompticorn.manifest.source_type import SourceType

NAME_KEY = "name"
TYPE_KEY = "type"

_KNOWN_KEYS = frozenset({NAME_KEY, TYPE_KEY})


@dataclass(frozen=True)
class SourceDeclaration:
    """A named source that artifacts may be fetched from.

    Declaring a source does not yet wire it into resolution — the resolver stack
    is the lockfile milestone's business. This ticket validates the declaration
    so a manifest written today still reads correctly when resolution arrives,
    rather than needing a format change then.

    Attributes:
        name: How artifacts refer to this source.
        type: Which kind of source it is.
    """

    name: str
    type: SourceType

    @classmethod
    def parse(cls, raw: Any, key_path: str) -> SourceDeclaration:
        """Parse and validate one ``sources:`` entry.

        Args:
            raw: The YAML value, unvalidated.
            key_path: Where this entry sits, e.g. ``sources[0]``, so any error
                points the author at the right line.

        Returns:
            The parsed declaration.

        Raises:
            ManifestSchemaError: With the offending key path.
        """
        mapping = require_mapping(raw, key_path, _KNOWN_KEYS)
        reject_unknown_keys(mapping, key_path, _KNOWN_KEYS)

        name = required_string(mapping, NAME_KEY, key_path)
        type_token = required_string(mapping, TYPE_KEY, key_path)

        try:
            source_type = SourceType(type_token)
        except ValueError:
            raise ManifestSchemaError(
                f"{key_path}.{TYPE_KEY}",
                f"unknown source type {type_token!r}; expected one of: {SourceType.known()}",
            ) from None

        return cls(name=name, type=source_type)
