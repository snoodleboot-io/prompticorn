"""Validation of the v2 manifest keys (PRO-109).

Schema v2 is **purely additive**: ``artifacts:``, ``sources:`` and, later,
``policy:``. Absent keys mean exactly today's behaviour, which is why a v1
config keeps building byte-identical output.

Validation lives here rather than in ``ConfigHandler`` because it is a different
job. ``ConfigHandler`` reads and writes a YAML file; this decides whether what it
read makes sense, and says where it does not. Keeping them apart is what lets the
manifest gain keys without the file handler learning about each one.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from prompticorn.manifest.artifact_declaration import ArtifactDeclaration
from prompticorn.manifest.errors import ManifestSchemaError, ManifestVersionError
from prompticorn.manifest.schema_values import describe_kind
from prompticorn.manifest.source_declaration import SourceDeclaration

ARTIFACTS_KEY = "artifacts"
SOURCES_KEY = "sources"
VERSION_KEY = "version"

SCHEMA_VERSION_V1 = "1.0"
SCHEMA_VERSION_V2 = "2.0"

# Versions this build can read. A manifest declaring anything else is newer than
# this installation, which is an upgrade problem rather than a syntax problem.
SUPPORTED_SCHEMA_VERSIONS = (SCHEMA_VERSION_V1, SCHEMA_VERSION_V2)


@dataclass(frozen=True)
class ManifestSchema:
    """The validated v2 additions to a manifest.

    Attributes:
        artifacts: Declared artifact dependencies, in the order written.
        sources: Declared sources, in the order written.
    """

    artifacts: tuple[ArtifactDeclaration, ...] = ()
    sources: tuple[SourceDeclaration, ...] = ()

    @classmethod
    def parse(cls, config: dict[str, Any]) -> ManifestSchema:
        """Validate the v2 keys of a loaded config.

        A config with neither key yields an empty schema — the v1 case, and the
        overwhelmingly common one.

        Args:
            config: The loaded configuration mapping.

        Returns:
            The validated additions.

        Raises:
            ManifestSchemaError: With the path of the offending key.
            ManifestVersionError: If the manifest is newer than this build.
        """
        cls._check_version(config)

        sources = cls._parse_sources(config)
        artifacts = cls._parse_artifacts(config)
        cls._check_source_references(artifacts, sources)

        return cls(artifacts=artifacts, sources=sources)

    @staticmethod
    def _check_version(config: dict[str, Any]) -> None:
        """Reject a manifest this build is too old to read.

        Note that ``version`` was inert before this ticket — written by the
        templates, read by nothing. This is its first consumer, so an absent key
        is treated as v1 rather than as an error.
        """
        declared = config.get(VERSION_KEY)
        if declared is None:
            return
        if not isinstance(declared, str):
            raise ManifestSchemaError(
                VERSION_KEY, f"expected a string, got {describe_kind(declared)}"
            )
        if declared not in SUPPORTED_SCHEMA_VERSIONS:
            raise ManifestVersionError(declared, SUPPORTED_SCHEMA_VERSIONS)

    @classmethod
    def _parse_sources(cls, config: dict[str, Any]) -> tuple[SourceDeclaration, ...]:
        entries = cls._entries(config, SOURCES_KEY)
        sources = tuple(
            SourceDeclaration.parse(entry, f"{SOURCES_KEY}[{index}]")
            for index, entry in enumerate(entries)
        )
        cls._reject_duplicates([source.name for source in sources], SOURCES_KEY, "source", "name")
        return sources

    @classmethod
    def _parse_artifacts(cls, config: dict[str, Any]) -> tuple[ArtifactDeclaration, ...]:
        entries = cls._entries(config, ARTIFACTS_KEY)
        artifacts = tuple(
            ArtifactDeclaration.parse(entry, f"{ARTIFACTS_KEY}[{index}]")
            for index, entry in enumerate(entries)
        )
        # A list of mappings makes duplicates syntactically legal, unlike a
        # mapping keyed by coordinate. Two entries for one artifact have no
        # defined winner, so this is rejected rather than silently resolved.
        cls._reject_duplicates(
            [artifact.name for artifact in artifacts], ARTIFACTS_KEY, "artifact", "name"
        )
        return artifacts

    @staticmethod
    def _entries(config: dict[str, Any], key: str) -> list[Any]:
        """The list under ``key``, or empty when absent.

        An explicit ``null`` counts as absent: YAML authors write it to mean
        "nothing here", and it is the shape left behind by commenting out every
        entry under a key.
        """
        raw = config.get(key)
        if raw is None:
            return []
        if not isinstance(raw, list):
            raise ManifestSchemaError(key, f"expected a list, got {describe_kind(raw)}")
        return raw

    @staticmethod
    def _reject_duplicates(names: list[str], key: str, noun: str, field: str) -> None:
        seen: set[str] = set()
        for index, name in enumerate(names):
            if name in seen:
                raise ManifestSchemaError(
                    f"{key}[{index}].{field}",
                    f"duplicate {noun} {name!r}; it is declared more than once and "
                    "there is no defined winner",
                )
            seen.add(name)

    @staticmethod
    def _check_source_references(
        artifacts: tuple[ArtifactDeclaration, ...],
        sources: tuple[SourceDeclaration, ...],
    ) -> None:
        """Every named source must be declared.

        Checked here because it is the only layer that sees both lists. A
        reference to an undeclared source would otherwise fail much later, at
        resolution, with nothing pointing back at the manifest line that caused it.
        """
        declared = {source.name for source in sources}
        for index, artifact in enumerate(artifacts):
            if artifact.source is None or artifact.source in declared:
                continue
            known = ", ".join(sorted(declared)) if declared else "none are declared"
            raise ManifestSchemaError(
                f"{ARTIFACTS_KEY}[{index}].source",
                f"references undeclared source {artifact.source!r} (declared sources: {known})",
            )
