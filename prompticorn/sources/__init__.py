"""Where artifacts come from.

An :class:`ArtifactSource` lists, resolves and fetches artifacts. A fetch is
always integrity-checked by the base class, so every implementation — the local
directory here, a git source later, a hosted registry in EE — inherits the same
guarantee rather than being trusted to reimplement it.

Named ``ArtifactSource`` rather than ``Source`` because ``ContentSource``
already answers the same question one level down, for units rather than
artifacts.
"""

from prompticorn.sources.artifact_content_source import ArtifactContentSource
from prompticorn.sources.artifact_source import ArtifactSource
from prompticorn.sources.errors import (
    ArtifactNotFoundError,
    DigestMismatchError,
    SourceError,
    SourceUnavailableError,
    VersionNotFoundError,
)
from prompticorn.sources.fetched_artifact import FetchedArtifact
from prompticorn.sources.local_directory_source import (
    DIGEST_KEY,
    MANIFEST_FILENAME,
    LocalDirectorySource,
)

__all__ = [
    "DIGEST_KEY",
    "MANIFEST_FILENAME",
    "ArtifactContentSource",
    "ArtifactNotFoundError",
    "ArtifactSource",
    "DigestMismatchError",
    "FetchedArtifact",
    "LocalDirectorySource",
    "SourceError",
    "SourceUnavailableError",
    "VersionNotFoundError",
]
