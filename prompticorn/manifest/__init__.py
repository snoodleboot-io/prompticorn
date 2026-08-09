"""Manifest schema — what a project declares in ``.prompticorn.yaml``.

Schema v2 adds ``artifacts:`` (a coordinate plus a version range) and
``sources:``. Both are additive: a manifest with neither key behaves exactly as
it did under v1, which is what lets existing configs keep producing
byte-identical output.

The manifest declares *ranges*; the lockfile records the exact versions they
resolved to. That split is why ``artifacts:`` parses into ``ArtifactRequirement``
rather than ``ArtifactId``.
"""

from prompticorn.manifest.artifact_declaration import ArtifactDeclaration
from prompticorn.manifest.errors import (
    ManifestError,
    ManifestSchemaError,
    ManifestVersionError,
)
from prompticorn.manifest.manifest_schema import (
    SCHEMA_VERSION_V1,
    SCHEMA_VERSION_V2,
    SUPPORTED_SCHEMA_VERSIONS,
    ManifestSchema,
)
from prompticorn.manifest.source_declaration import SourceDeclaration
from prompticorn.manifest.source_type import SourceType

__all__ = [
    "SCHEMA_VERSION_V1",
    "SCHEMA_VERSION_V2",
    "SUPPORTED_SCHEMA_VERSIONS",
    "ArtifactDeclaration",
    "ManifestError",
    "ManifestSchema",
    "ManifestSchemaError",
    "ManifestVersionError",
    "SourceDeclaration",
    "SourceType",
]
