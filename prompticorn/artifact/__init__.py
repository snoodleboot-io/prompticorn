"""Artifact identity and versioning.

The layer above content addressing. ``ArtifactId`` identifies *what an org
released* (``local/acme-sec@2.1.0``); ``UnitId`` — over in
:mod:`prompticorn.content` — addresses *where bytes live inside* it
(``agent/architect/minimal``). An artifact contains one or more units, and the
two types are never interchangeable.

``ArtifactRequirement`` is the manifest form (a version range);
``ArtifactId`` is the lock form (an exact version); ``PinnedArtifact`` pairs an
id with the digest of its content.
"""

from prompticorn.artifact.artifact_id import ArtifactId
from prompticorn.artifact.artifact_requirement import ArtifactRequirement
from prompticorn.artifact.comparison_operator import ComparisonOperator
from prompticorn.artifact.errors import (
    ArtifactError,
    InvalidArtifactIdError,
    InvalidDigestError,
    InvalidSemanticVersionError,
    InvalidVersionRangeError,
)
from prompticorn.artifact.naming import DEFAULT_NAMESPACE
from prompticorn.artifact.pinned_artifact import PinnedArtifact
from prompticorn.artifact.semantic_version import SemanticVersion
from prompticorn.artifact.version_constraint import VersionConstraint
from prompticorn.artifact.version_range import VersionRange

__all__ = [
    "DEFAULT_NAMESPACE",
    "ArtifactError",
    "ArtifactId",
    "ArtifactRequirement",
    "ComparisonOperator",
    "InvalidArtifactIdError",
    "InvalidDigestError",
    "InvalidSemanticVersionError",
    "InvalidVersionRangeError",
    "PinnedArtifact",
    "SemanticVersion",
    "VersionConstraint",
    "VersionRange",
]
