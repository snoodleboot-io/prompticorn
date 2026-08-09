"""One entry under the manifest's ``artifacts:`` key (PRO-109).

This is the first real consumer of
:class:`~prompticorn.artifact.artifact_requirement.ArtifactRequirement` — the
manifest is where a version *range* is declared, as opposed to the exact version
a lock records. The declaration is deliberately a thin, validated wrapper: the
grammar of a coordinate and a range already belongs to the artifact module, and
restating it here would give the project two definitions to keep in step.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from prompticorn.artifact.artifact_requirement import ArtifactRequirement
from prompticorn.artifact.errors import ArtifactError
from prompticorn.artifact.version_range import VersionRange
from prompticorn.manifest.errors import ManifestSchemaError
from prompticorn.manifest.schema_values import (
    optional_string,
    reject_unknown_keys,
    require_mapping,
    required_string,
)

NAME_KEY = "name"
VERSION_KEY = "version"
SOURCE_KEY = "source"

_KNOWN_KEYS = frozenset({NAME_KEY, VERSION_KEY, SOURCE_KEY})


@dataclass(frozen=True)
class ArtifactDeclaration:
    """A declared dependency on some acceptable version of an artifact.

    Attributes:
        requirement: The coordinate and version range, already parsed and
            validated by the artifact module.
        source: Name of the source to fetch from, or None to use the default
            stack. When set, it must name a declared source — checked by
            :class:`~prompticorn.manifest.manifest_schema.ManifestSchema`, which
            is the only layer that can see both lists.
    """

    requirement: ArtifactRequirement
    source: str | None = None

    @classmethod
    def parse(cls, raw: Any, key_path: str) -> ArtifactDeclaration:
        """Parse and validate one ``artifacts:`` entry.

        Args:
            raw: The YAML value, unvalidated.
            key_path: Where this entry sits, e.g. ``artifacts[1]``.

        Returns:
            The parsed declaration.

        Raises:
            ManifestSchemaError: With the offending key path.
        """
        mapping = require_mapping(raw, key_path, _KNOWN_KEYS)
        reject_unknown_keys(mapping, key_path, _KNOWN_KEYS)

        name = required_string(mapping, NAME_KEY, key_path)
        version = required_string(mapping, VERSION_KEY, key_path)
        source = optional_string(mapping, SOURCE_KEY, key_path)

        return cls(requirement=cls._build_requirement(name, version, key_path), source=source)

    @staticmethod
    def _build_requirement(name: str, version: str, key_path: str) -> ArtifactRequirement:
        """Combine the two fields into a requirement, re-typing failures.

        The artifact module's errors are phrased for someone holding a
        requirement string. A manifest author is holding two YAML keys, so the
        error is re-raised against whichever key is actually at fault — with the
        underlying reason preserved rather than discarded.
        """
        try:
            VersionRange.parse(version)
        except ArtifactError as exc:
            raise ManifestSchemaError(f"{key_path}.{VERSION_KEY}", str(exc)) from exc

        try:
            return ArtifactRequirement.parse(f"{name}@{version}")
        except ArtifactError as exc:
            # The range already parsed, so anything left is the coordinate.
            raise ManifestSchemaError(f"{key_path}.{NAME_KEY}", str(exc)) from exc

    @property
    def name(self) -> str:
        """The declared coordinate, always namespace-qualified."""
        return self.requirement.coordinate

    def __str__(self) -> str:
        rendered = self.requirement.render()
        return f"{rendered} from {self.source}" if self.source else rendered
