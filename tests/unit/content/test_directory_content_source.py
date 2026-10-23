"""A layer read from a directory somebody authored by hand (PRO-165).

The bundled tree is generated and reviewed; an override directory is neither.
Everything here is about inputs the package cannot vouch for: a file that is not
a unit, and a directory that cannot be read. Both used to be answered with
"this layer has no content in it", which is the one answer that is never true.
"""

from __future__ import annotations

import os
import stat
from collections.abc import Iterator
from pathlib import Path

import pytest

from prompticorn.content.builtin_content_source import BuiltinContentSource
from prompticorn.content.content_resolver import ContentResolver
from prompticorn.content.directory_content_source import DirectoryContentSource
from prompticorn.content.errors import SkippedContentWarning, SourceUnavailableError
from prompticorn.content.unit_id import UnitId

LAYER = "project"


def write(root: Path, relative: str, text: str = "body\n") -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def source(root: Path) -> DirectoryContentSource:
    return DirectoryContentSource(root=root, layer=LAYER)


@pytest.mark.unit
class TestAFileThatIsNotAUnit:
    """`.prompticorn/content/agents/core/README.md` is a natural thing to commit,
    and before this it took down every command that enumerates content."""

    def test_an_unaddressable_name_does_not_raise(self, tmp_path: Path) -> None:
        write(tmp_path, "agents/core/README.md")

        with pytest.warns(SkippedContentWarning):
            units = list(source(tmp_path).units())

        assert units == []

    def test_the_warning_names_the_file_and_the_layer(self, tmp_path: Path) -> None:
        """Both, because neither alone is actionable: a project with an org layer
        above it has two directories that could hold the same relative path."""
        write(tmp_path, "agents/core/README.md")

        with pytest.warns(SkippedContentWarning) as caught:
            list(source(tmp_path).units())

        message = str(caught[0].message)
        assert "agents/core/README.md" in message
        assert LAYER in message

    def test_the_warning_names_the_unit_the_file_would_have_been(self, tmp_path: Path) -> None:
        """The skip is only safe because it is legible. Somebody who misspelled an
        override has to be able to see which unit they were reaching for."""
        write(tmp_path, "agents/core/README.md")

        with pytest.warns(SkippedContentWarning, match="convention/core/README"):
            list(source(tmp_path).units())

    def test_the_valid_units_beside_it_are_still_discovered(self, tmp_path: Path) -> None:
        """Skipping must cost the one file, not the rest of the layer. Discovery
        is a generator, so an exception anywhere in it discarded everything."""
        write(tmp_path, "agents/core/README.md")
        write(tmp_path, "agents/core/system.md")
        write(tmp_path, "skills/demo/minimal/SKILL.md")

        with pytest.warns(SkippedContentWarning):
            rendered = sorted(unit.id.render() for unit in source(tmp_path).units())

        assert rendered == ["convention/core/system", "skill/demo/minimal"]

    @pytest.mark.parametrize(
        ("relative", "would_be"),
        [
            ("agents/core/README.md", "convention/core/README"),
            ("agents/My Agent/prompt.md", "agent/My Agent"),
            ("skills/Demo/minimal/SKILL.md", "skill/Demo/minimal"),
            ("workflows/demo/Minimal/workflow.md", "workflow/demo/Minimal"),
            ("agents/debug/subagents/Root Cause/minimal/prompt.md", "Root Cause"),
            ("configurations/Personas.yaml", "configuration/Personas"),
        ],
    )
    def test_every_discovery_site_skips_rather_than_raises(
        self, tmp_path: Path, relative: str, would_be: str
    ) -> None:
        """Parametrised over the shapes because discovery has five separate
        walkers and fixing one of them fixes nothing."""
        write(tmp_path, relative)

        with pytest.warns(SkippedContentWarning, match=would_be):
            assert list(source(tmp_path).units()) == []

    def test_a_resolver_over_the_layer_still_serves_the_lower_layers(self, tmp_path: Path) -> None:
        """The end the user sees: an unaddressable file in an override layer must
        not stop the bundled library from resolving."""
        write(tmp_path, "agents/core/README.md")
        resolver = ContentResolver(sources=(source(tmp_path), BuiltinContentSource()))

        with pytest.warns(SkippedContentWarning):
            units = resolver.units()

        assert units
        assert all(unit.layer == "builtin" for unit in units)


@pytest.mark.unit
class TestABundledTreeWithABadName:
    """The same code serves the bundled layer, where such a name is a packaging
    bug rather than an author's file. It is still not worth crashing over, and
    the warning says which layer it came from."""

    def test_the_bundled_layer_names_itself_in_the_warning(self, tmp_path: Path) -> None:
        write(tmp_path, "agents/core/README.md")

        with pytest.warns(SkippedContentWarning, match="builtin"):
            list(BuiltinContentSource(root=tmp_path).units())


@pytest.mark.unit
class TestPresentButUnreadable:
    """Absent, empty and unreadable are three states. The first two are ordinary;
    the third was being reported as the second."""

    @pytest.fixture
    def unreadable(self, tmp_path: Path) -> Iterator[Path]:
        if os.geteuid() == 0:
            pytest.skip("running as root: mode bits do not deny access")
        root = tmp_path / "content"
        write(root, "skills/demo/minimal/SKILL.md")
        root.chmod(0o000)
        yield root
        root.chmod(stat.S_IRWXU)

    def test_an_unreadable_layer_is_reported_rather_than_read_as_empty(
        self, unreadable: Path
    ) -> None:
        with pytest.raises(SourceUnavailableError):
            list(source(unreadable).units())

    def test_the_error_names_the_layer_and_the_directory(self, unreadable: Path) -> None:
        with pytest.raises(SourceUnavailableError) as caught:
            list(source(unreadable).units())

        assert caught.value.source == LAYER
        assert str(unreadable) in caught.value.reason

    def test_reading_a_unit_from_an_unreadable_layer_is_not_a_miss(self, unreadable: Path) -> None:
        """A miss would send the resolver to the next layer, which is how a
        broken layer becomes a build that looks fine."""
        with pytest.raises(SourceUnavailableError):
            source(unreadable).read(UnitId.parse("skill/demo/minimal"))

    def test_an_absent_directory_is_still_an_empty_layer(self, tmp_path: Path) -> None:
        """The case that must keep working: most projects have no override
        directory, and building must not be a tax on them."""
        absent = tmp_path / "nothing-here"

        assert source(absent).is_present is False
        assert list(source(absent).units()) == []

    def test_an_empty_directory_is_an_empty_layer(self, tmp_path: Path) -> None:
        """Present, readable and holding nothing. Distinct from unreadable, and
        must stay quiet."""
        empty = tmp_path / "content"
        empty.mkdir()

        assert source(empty).is_present is True
        assert list(source(empty).units()) == []


@pytest.mark.unit
class TestTheUnreadableCaseIsRealOnThisMachine:
    """Guards the premise. Running as root makes every directory readable, and
    the tests above would then pass while proving nothing."""

    def test_mode_000_actually_denies_listing(self, tmp_path: Path) -> None:
        if os.geteuid() == 0:
            pytest.skip("running as root: mode bits do not deny access")
        blocked = tmp_path / "blocked"
        blocked.mkdir()
        blocked.chmod(0o000)
        try:
            with pytest.raises(OSError):
                list(blocked.iterdir())
        finally:
            blocked.chmod(stat.S_IRWXU)
