"""From a manifest's ``sources:`` entry to a source object (PRO-151).

The one place that knows which class implements which declared type. The
resolver asks for "the source this declaration describes" and never names a
class, so adding a source type is a new branch here and a new class — not a
change to resolution.
"""

from __future__ import annotations

from pathlib import Path

from prompticorn.manifest.source_declaration import SourceDeclaration
from prompticorn.manifest.source_type import SourceType
from prompticorn.sources.artifact_source import ArtifactSource
from prompticorn.sources.git_source import GitSource
from prompticorn.sources.local_directory_source import LocalDirectorySource


def build_artifact_source(
    declaration: SourceDeclaration, project_root: Path
) -> ArtifactSource | None:
    """The source a declaration describes, or None for the bundled tree.

    Args:
        declaration: A parsed ``sources:`` entry.
        project_root: What a relative ``path`` is relative to. The manifest
            lives in the project, so its paths mean what they would mean to
            someone reading it there — not whatever directory the CLI happened
            to be launched from.

    Returns:
        None for ``builtin``, which resolves through the bundled content stack
        rather than through an artifact source.
    """
    if declaration.type is SourceType.BUILTIN:
        return None
    location = declaration.location
    # The schema guarantees a location for every non-builtin type; asserting it
    # here turns a schema regression into an immediate, local failure.
    assert location is not None, (
        f"{declaration.type.value} source {declaration.name!r} has no location"
    )

    if declaration.type is SourceType.GIT:
        return GitSource(location, name=declaration.name)
    if declaration.type is SourceType.LOCAL_DIR:
        path = Path(location).expanduser()
        if not path.is_absolute():
            path = project_root / path
        return LocalDirectorySource(path, name=declaration.name)
    raise ValueError(f"no source implementation for type {declaration.type.value!r}")
