"""A captured configuration, ready to apply somewhere else (PRO-130).

A profile is the answer to "set this project up the way that one is". It holds
the manifest payload — the same keys `.prompticorn.yaml` carries — plus enough
metadata to tell two captures apart.

**Versions are immutable.** Saving produces N+1 rather than overwriting N, which
is what makes ``diff v3 v4`` a real comparison and rollback a copy rather than a
reconstruction.

**The digest is over a canonical form, not the bytes on disk.** A profile may be
hand-edited, and a reordered key or a new comment must not read as a changed
profile — otherwise every lock that references one churns on formatting. So the
digest sorts keys and drops everything that is presentation.
"""

from __future__ import annotations

import io
from collections.abc import Mapping, Sequence, Set
from dataclasses import dataclass
from typing import Any

import yaml

from prompticorn.content.digest import digest_text

NAME_KEY = "name"
VERSION_KEY = "version"
DESCRIPTION_KEY = "description"
CREATED_AT_KEY = "created_at"
PAYLOAD_KEY = "payload"

# The first version a profile is saved at. One rather than zero, because these
# numbers are shown to people and `v1` is the first thing anybody expects.
FIRST_VERSION = 1


@dataclass(frozen=True)
class Profile:
    """One immutable version of a captured configuration.

    Attributes:
        name: What the user calls it, e.g. ``backend``.
        version: Monotonic, starting at :data:`FIRST_VERSION`. Never reused.
        payload: The manifest content — ``repository``, ``spec``, ``project``,
            ``variant``, ``active_personas``, ``ai_tool``.
        description: Why this profile exists, in the author's words.
        created_at: ISO-8601 UTC, supplied by the caller rather than read from
            the clock here. The same rule the lock follows: a value read inside
            the model is a value a test cannot pin.
    """

    name: str
    version: int
    payload: dict[str, Any]
    description: str = ""
    created_at: str = ""

    def __post_init__(self) -> None:
        """Normalise the payload to plain Python containers.

        `ConfigHandler` reads manifests with ruamel, which returns
        `CommentedMap` and `CommentedSeq` so that comments and ordering survive
        a round trip. Those types carry presentation state and PyYAML's safe
        dumper refuses to represent them, so a profile captured straight from a
        manifest could be neither digested nor written. Converting once, here,
        means every consumer downstream sees ordinary dicts and lists.
        """
        object.__setattr__(self, "payload", plain_data(self.payload))

    def canonical_text(self) -> str:
        """The form the digest is taken over.

        Sorted keys, block style, no comments, LF. Deliberately not the form
        written to disk, which preserves whatever ordering and commentary the
        author used.
        """
        buffer = io.StringIO()
        yaml.safe_dump(
            self.payload,
            buffer,
            sort_keys=True,
            default_flow_style=False,
            allow_unicode=True,
            width=10_000,
        )
        return buffer.getvalue()

    def digest(self) -> str:
        """sha256 of the canonical payload.

        Covers the payload alone. Name, version and timestamp describe the
        capture rather than the configuration, and including them would make
        two identical setups saved a minute apart look like different things.
        """
        return digest_text(self.canonical_text())

    def to_mapping(self) -> dict[str, Any]:
        """Plain data for the writer. A fresh dict every call."""
        return {
            NAME_KEY: self.name,
            VERSION_KEY: self.version,
            DESCRIPTION_KEY: self.description,
            CREATED_AT_KEY: self.created_at,
            PAYLOAD_KEY: dict(self.payload),
        }

    @classmethod
    def from_mapping(cls, mapping: dict[str, Any]) -> Profile:
        """Rebuild from stored data.

        Raises:
            ValueError: If the document is not a profile. Raised rather than
                tolerated, because a half-understood profile applied to a
                project writes a half-correct manifest.
        """
        if not isinstance(mapping, dict):
            raise ValueError(f"profile must be a mapping, found {type(mapping).__name__}")
        payload = mapping.get(PAYLOAD_KEY)
        if not isinstance(payload, dict):
            raise ValueError("profile has no payload mapping")
        try:
            version = int(mapping[VERSION_KEY])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("profile has no usable version") from error
        name = mapping.get(NAME_KEY)
        if not isinstance(name, str) or not name:
            raise ValueError("profile has no name")
        return cls(
            name=name,
            version=version,
            payload=dict(payload),
            description=str(mapping.get(DESCRIPTION_KEY) or ""),
            created_at=str(mapping.get(CREATED_AT_KEY) or ""),
        )

    def __str__(self) -> str:
        return f"{self.name}@v{self.version}"


def plain_data(value: Any) -> Any:
    """Recursively convert mappings and sequences to dict, list and scalars.

    Strings are sequences too, and converting one to a list of characters is a
    corruption that looks like data — so they are returned untouched before the
    sequence branch is reached.
    """
    if isinstance(value, str | bytes):
        return value
    if isinstance(value, Mapping):
        return {plain_data(key): plain_data(item) for key, item in value.items()}
    if isinstance(value, Sequence):
        return [plain_data(item) for item in value]
    if isinstance(value, Set):
        return sorted(plain_data(item) for item in value)
    return value
