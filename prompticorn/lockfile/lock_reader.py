"""Reading a lock back into the model (PRO-110).

Every failure here is reported against the file, not the user's typing: the lock
is generated, so a fault in it is a tooling problem and the message says what to
do about it rather than asking the reader to fix YAML by hand.

The one exception is a lock from a **newer** prompticorn, which is not a fault at
all. That gets its own error precisely so the advice can be the opposite of
"regenerate" — see :class:`~prompticorn.lockfile.errors.LockSchemaVersionError`.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from prompticorn.artifact.artifact_id import ArtifactId
from prompticorn.artifact.errors import ArtifactError
from prompticorn.artifact.pinned_artifact import PinnedArtifact
from prompticorn.content.errors import InvalidUnitIdError
from prompticorn.content.unit_id import UnitId
from prompticorn.lockfile.errors import LockCorruptError, LockSchemaVersionError
from prompticorn.lockfile.lock_file import (
    ARTIFACTS_KEY,
    LOCK_VERSION_KEY,
    OUTPUTS_KEY,
    PROMPTICORN_VERSION_KEY,
    RESOLVED_AT_KEY,
    SUPPORTED_LOCK_VERSIONS,
    UNITS_KEY,
    LockFile,
)
from prompticorn.lockfile.locked_artifact import DIGEST_KEY as ARTIFACT_DIGEST_KEY
from prompticorn.lockfile.locked_artifact import IDENTITY_KEY, SOURCE_KEY, LockedArtifact
from prompticorn.lockfile.locked_output import DIGEST_KEY as OUTPUT_DIGEST_KEY
from prompticorn.lockfile.locked_output import PATH_KEY, LockedOutput
from prompticorn.lockfile.locked_unit import DIGEST_KEY as UNIT_DIGEST_KEY
from prompticorn.lockfile.locked_unit import ID_KEY, LAYER_KEY, LockedUnit

_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")


class LockReader:
    """Parses ``.prompticorn/prompticorn.lock`` into a :class:`LockFile`."""

    @classmethod
    def read(cls, path: Path) -> LockFile:
        """Read and validate a lock file.

        Args:
            path: The lock file.

        Returns:
            The parsed lock.

        Raises:
            LockCorruptError: If it cannot be read as a lock.
            LockSchemaVersionError: If it is newer than this build.
        """
        location = str(path)
        try:
            raw_text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise LockCorruptError(location, f"could not be read ({exc})") from exc

        return cls.parse(raw_text, location)

    @classmethod
    def parse(cls, raw_text: str, location: str) -> LockFile:
        """Parse lock text. Separate from :meth:`read` so tests need no file."""
        try:
            data = yaml.safe_load(raw_text)
        except yaml.YAMLError as exc:
            raise LockCorruptError(location, f"is not valid YAML ({exc})") from exc

        if data is None:
            raise LockCorruptError(location, "is empty")
        if not isinstance(data, dict):
            raise LockCorruptError(location, f"is not a mapping (found {type(data).__name__})")

        # Checked before anything else: a newer lock may legitimately contain
        # keys this build has never heard of, and reporting those as corruption
        # would send the user to regenerate a file they should not touch.
        cls._check_schema_version(data, location)

        return LockFile(
            prompticorn_version=_required_string(data, PROMPTICORN_VERSION_KEY, location),
            resolved_at=cls._read_resolved_at(data, location),
            artifacts=tuple(cls._read_artifacts(data, location)),
            units=tuple(cls._read_units(data, location)),
            outputs=tuple(cls._read_outputs(data, location)),
            lock_version=_required_string(data, LOCK_VERSION_KEY, location),
        )

    @staticmethod
    def _check_schema_version(data: dict[str, Any], location: str) -> None:
        declared = data.get(LOCK_VERSION_KEY)
        if declared is None:
            raise LockCorruptError(location, f"is missing {LOCK_VERSION_KEY!r}")
        if not isinstance(declared, str):
            raise LockCorruptError(
                location, f"{LOCK_VERSION_KEY!r} must be a string, found {type(declared).__name__}"
            )
        if declared not in SUPPORTED_LOCK_VERSIONS:
            raise LockSchemaVersionError(location, declared, SUPPORTED_LOCK_VERSIONS)

    @staticmethod
    def _read_resolved_at(data: dict[str, Any], location: str) -> str:
        value = _required_string(data, RESOLVED_AT_KEY, location)
        try:
            # Constructing the model validates the timestamp spelling, which is
            # load-bearing for re-lock stability rather than cosmetic.
            LockFile(prompticorn_version="0.0.0", resolved_at=value)
        except ValueError as exc:
            raise LockCorruptError(location, str(exc)) from exc
        return value

    @classmethod
    def _read_artifacts(cls, data: dict[str, Any], location: str) -> list[LockedArtifact]:
        artifacts = []
        for index, entry in enumerate(_sequence(data, ARTIFACTS_KEY, location)):
            where = f"{ARTIFACTS_KEY}[{index}]"
            mapping = _mapping(entry, where, location)
            identity = _required_string(mapping, IDENTITY_KEY, location, where)
            digest = _digest(mapping, ARTIFACT_DIGEST_KEY, location, where)
            source = mapping.get(SOURCE_KEY)
            if source is not None and not isinstance(source, str):
                raise LockCorruptError(location, f"{where}.{SOURCE_KEY} must be a string")
            try:
                artifact_id = ArtifactId.parse(identity)
            except ArtifactError as exc:
                raise LockCorruptError(location, f"{where}.{IDENTITY_KEY}: {exc}") from exc
            artifacts.append(
                LockedArtifact(
                    pinned=PinnedArtifact(artifact_id=artifact_id, digest=digest), source=source
                )
            )
        return artifacts

    @classmethod
    def _read_units(cls, data: dict[str, Any], location: str) -> list[LockedUnit]:
        units = []
        for index, entry in enumerate(_sequence(data, UNITS_KEY, location)):
            where = f"{UNITS_KEY}[{index}]"
            mapping = _mapping(entry, where, location)
            raw_id = _required_string(mapping, ID_KEY, location, where)
            try:
                unit_id = UnitId.parse(raw_id)
            except InvalidUnitIdError as exc:
                raise LockCorruptError(location, f"{where}.{ID_KEY}: {exc}") from exc
            units.append(
                LockedUnit(
                    id=unit_id,
                    layer=_required_string(mapping, LAYER_KEY, location, where),
                    digest=_digest(mapping, UNIT_DIGEST_KEY, location, where),
                )
            )
        return units

    @classmethod
    def _read_outputs(cls, data: dict[str, Any], location: str) -> list[LockedOutput]:
        outputs = []
        for index, entry in enumerate(_sequence(data, OUTPUTS_KEY, location)):
            where = f"{OUTPUTS_KEY}[{index}]"
            mapping = _mapping(entry, where, location)
            outputs.append(
                LockedOutput(
                    path=_required_string(mapping, PATH_KEY, location, where),
                    digest=_digest(mapping, OUTPUT_DIGEST_KEY, location, where),
                )
            )
        return outputs


def _sequence(data: dict[str, Any], key: str, location: str) -> list[Any]:
    """A list under ``key``. Absent counts as empty; a non-list is corruption."""
    raw = data.get(key)
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise LockCorruptError(location, f"{key!r} must be a list, found {type(raw).__name__}")
    return raw


def _mapping(entry: Any, where: str, location: str) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise LockCorruptError(location, f"{where} must be a mapping, found {type(entry).__name__}")
    return entry


def _required_string(
    data: dict[str, Any], key: str, location: str, where: str | None = None
) -> str:
    path = f"{where}.{key}" if where else repr(key)
    value = data.get(key)
    if value is None:
        raise LockCorruptError(location, f"is missing {path}")
    if not isinstance(value, str):
        raise LockCorruptError(location, f"{path} must be a string, found {type(value).__name__}")
    return value


def _digest(data: dict[str, Any], key: str, location: str, where: str) -> str:
    """A digest must look like one.

    A malformed digest is worse than an absent one: verification appears to be
    happening while never matching anything.
    """
    value = _required_string(data, key, location, where)
    if not _DIGEST_RE.match(value):
        raise LockCorruptError(
            location, f"{where}.{key} is not a sha256 digest (64 lowercase hex characters)"
        )
    return value
