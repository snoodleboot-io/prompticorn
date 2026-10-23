"""One entry under the manifest's ``sources:`` key (PRO-109)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from prompticorn.manifest.errors import ManifestSchemaError
from prompticorn.manifest.schema_values import (
    optional_string,
    reject_unknown_keys,
    require_mapping,
    required_string,
)
from prompticorn.manifest.source_type import SourceType

NAME_KEY = "name"
TYPE_KEY = "type"
URL_KEY = "url"
PATH_KEY = "path"

_KNOWN_KEYS = frozenset({NAME_KEY, TYPE_KEY, URL_KEY, PATH_KEY})


@dataclass(frozen=True)
class SourceDeclaration:
    """A named source that artifacts may be fetched from.

    Resolved through by the lock resolver since PRO-151: an artifact that names
    this source is fetched from it rather than from the bundled tree.

    Attributes:
        name: How artifacts refer to this source.
        type: Which kind of source it is.
        location: Where it is — the ``url`` of a git source or the ``path`` of a
            directory source. None for ``builtin``, which is the package itself.
    """

    name: str
    type: SourceType
    location: str | None = None

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

        location = cls._location(mapping, source_type, key_path)
        return cls(name=name, type=source_type, location=location)

    @staticmethod
    def _location(mapping: dict[str, Any], source_type: SourceType, key_path: str) -> str | None:
        """The one location key this type needs, and no other.

        A ``url`` on a ``local-dir`` source is refused rather than ignored. An
        ignored key is one the author believes is doing something, and the day
        they notice it is not is the day the wrong source was used.
        """
        expected = source_type.location_key
        for key in (URL_KEY, PATH_KEY):
            if key != expected and key in mapping:
                raise ManifestSchemaError(
                    f"{key_path}.{key}",
                    f"a {source_type.value!r} source does not take {key!r}"
                    + (f"; it takes {expected!r}" if expected else ""),
                )
        if expected is None:
            return None
        location = optional_string(mapping, expected, key_path)
        if location is None:
            raise ManifestSchemaError(
                f"{key_path}.{expected}",
                f"a {source_type.value!r} source needs {expected!r} to say where it is",
            )
        return location
