"""From a declared source to the object that implements it (PRO-151).

The factory is the only place that maps a declared type to a class, so it is the
only place that can turn an impossible declaration into a sentence rather than a
stack trace from inside a constructor.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from prompticorn.manifest.source_declaration import SourceDeclaration
from prompticorn.manifest.source_type import SourceType
from prompticorn.sources.git_source import GitSource
from prompticorn.sources.local_directory_source import LocalDirectorySource
from prompticorn.sources.source_factory import build_artifact_source


def test_a_builtin_source_has_no_artifact_source() -> None:
    """``builtin`` resolves through the bundled content stack instead."""
    declaration = SourceDeclaration(name="bundled", type=SourceType.BUILTIN)

    assert build_artifact_source(declaration, Path(".")) is None


def test_a_git_source_is_built_from_its_url() -> None:
    declaration = SourceDeclaration(name="house", type=SourceType.GIT, location="git@x:y/z.git")

    source = build_artifact_source(declaration, Path("."))

    assert isinstance(source, GitSource)
    assert source.url == "git@x:y/z.git" and source.name == "house"


def test_a_relative_directory_is_relative_to_the_project(tmp_path: Path) -> None:
    """The manifest lives in the project, so its paths mean what they mean to
    someone reading it there — not to whatever directory the CLI ran from."""
    declaration = SourceDeclaration(name="shared", type=SourceType.LOCAL_DIR, location="../shared")

    source = build_artifact_source(declaration, tmp_path / "project")

    assert isinstance(source, LocalDirectorySource)
    assert source.root == tmp_path / "project" / "../shared"


def test_a_non_builtin_source_with_no_location_raises_rather_than_asserts() -> None:
    """PRO-164. This was an `assert`, which `python -O` strips.

    The schema guarantees the location, so reaching here means the schema
    regressed — and under -O the invariant resurfaced as an AttributeError about
    None having no `.encode`, several frames away from the source that has no
    location. A ValueError names it.
    """
    declaration = SourceDeclaration(name="house", type=SourceType.GIT, location=None)

    with pytest.raises(ValueError, match="house.*no location"):
        build_artifact_source(declaration, Path("."))
