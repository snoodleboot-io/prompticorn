"""`LocalDirectorySource` (PRO-124).

Runs the shared contract, then the things only a filesystem source can get
wrong: escaping the root, a digest that no longer matches the tree, and a
directory that is simply not an artifact.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from prompticorn.artifact.artifact_digest import artifact_digest
from prompticorn.artifact.artifact_id import ArtifactId
from prompticorn.artifact.semantic_version import SemanticVersion
from prompticorn.content.digest import digest_text
from prompticorn.sources import (
    ArtifactNotFoundError,
    DigestMismatchError,
    LocalDirectorySource,
    SourceUnavailableError,
    VersionNotFoundError,
)
from tests.unit.sources.artifact_source_contract import ArtifactSourceContract

SKILL_BODY = "# Testing Strategies\n\nThree shapes get argued about.\n"


def publish(root: Path, name: str, version: str, body: str = SKILL_BODY) -> ArtifactId:
    """Write one artifact with a correct manifest, and return its identity."""
    directory = root / "local" / name / version
    skill = directory / "skills" / "testing-strategies" / "minimal"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(body, encoding="utf-8")

    unit_id = "skill/testing-strategies/minimal"
    digest = artifact_digest([(unit_id, digest_text(body))])
    (directory / "artifact.yaml").write_text(
        yaml.safe_dump({"digest": digest}), encoding="utf-8"
    )
    return ArtifactId(namespace="local", name=name, version=SemanticVersion.parse(version))


@pytest.fixture
def populated(tmp_path: Path) -> Path:
    root = tmp_path / "registry"
    root.mkdir()
    for version in ("1.0.0", "1.2.0", "2.0.0", "2.10.0", "2.9.0"):
        publish(root, "house-standards", version)
    publish(root, "other-artifact", "0.1.0")
    return root


class TestContract(ArtifactSourceContract):
    @pytest.fixture
    def source(self, populated: Path) -> LocalDirectorySource:
        return LocalDirectorySource(populated)

    @pytest.fixture
    def known(self, populated: Path) -> ArtifactId:
        return ArtifactId(
            namespace="local", name="house-standards", version=SemanticVersion.parse("2.0.0")
        )


class TestVersionResolution:
    def test_a_range_resolves_to_the_highest_match(self, populated: Path):
        """A range says "anything compatible"; the useful answer is the newest."""
        source = LocalDirectorySource(populated)

        resolved = source.resolve_version("local/house-standards", ">=1.2.0,<3.0.0")

        assert resolved.version.render() == "2.10.0"

    def test_versions_sort_numerically_not_lexically(self, populated: Path):
        """2.10.0 sorts below 2.9.0 as text and above it as a version. Getting
        this wrong silently resolves a range to an older release."""
        source = LocalDirectorySource(populated)

        assert source.resolve_version("local/house-standards", ">=2.0.0").version.render() == "2.10.0"

    def test_an_unsatisfiable_range_names_what_is_available(self, populated: Path):
        """"No match" without the alternatives leaves the reader nowhere to go."""
        source = LocalDirectorySource(populated)

        with pytest.raises(VersionNotFoundError) as caught:
            source.resolve_version("local/house-standards", ">=9.0.0")

        assert "2.10.0" in str(caught.value)

    def test_an_unknown_coordinate_raises_rather_than_returning_nothing(self, populated: Path):
        source = LocalDirectorySource(populated)

        with pytest.raises(VersionNotFoundError):
            source.resolve_version("local/no-such-artifact", ">=1.0.0")


class TestIntegrity:
    def test_a_tampered_unit_fails_the_fetch(self, tmp_path: Path):
        """The check that makes a source trustworthy. Editing content after
        publication must not go unnoticed, or the digest is decoration."""
        root = tmp_path / "registry"
        root.mkdir()
        identity = publish(root, "house-standards", "1.0.0")
        skill = root / "local" / "house-standards" / "1.0.0" / "skills" / "testing-strategies"
        (skill / "minimal" / "SKILL.md").write_text("tampered\n", encoding="utf-8")

        with pytest.raises(DigestMismatchError):
            LocalDirectorySource(root).fetch(identity)

    def test_the_mismatch_names_both_digests(self, tmp_path: Path):
        root = tmp_path / "registry"
        root.mkdir()
        identity = publish(root, "house-standards", "1.0.0")
        skill = root / "local" / "house-standards" / "1.0.0" / "skills" / "testing-strategies"
        (skill / "minimal" / "SKILL.md").write_text("tampered\n", encoding="utf-8")

        with pytest.raises(DigestMismatchError) as caught:
            LocalDirectorySource(root).fetch(identity)

        assert caught.value.expected != caught.value.actual

    def test_a_manifest_without_a_digest_is_unusable_not_trusted(self, tmp_path: Path):
        """Treating a missing digest as "nothing to check" would make the
        integrity guarantee opt-out for anyone who omits one line."""
        root = tmp_path / "registry"
        directory = root / "local" / "thing" / "1.0.0"
        directory.mkdir(parents=True)
        (directory / "artifact.yaml").write_text(yaml.safe_dump({"note": "hi"}), encoding="utf-8")

        with pytest.raises(SourceUnavailableError):
            LocalDirectorySource(root).fetch(
                ArtifactId(namespace="local", name="thing", version=SemanticVersion.parse("1.0.0"))
            )


class TestPathSafety:
    def test_a_symlinked_version_directory_is_not_listed(self, tmp_path: Path):
        """Publishing a symlink is the cheapest way to make a tool read
        somewhere it should not."""
        root = tmp_path / "registry"
        outside = tmp_path / "outside" / "local" / "evil" / "1.0.0"
        outside.mkdir(parents=True)
        (outside / "artifact.yaml").write_text(yaml.safe_dump({"digest": "x"}), encoding="utf-8")
        (root / "local" / "evil").mkdir(parents=True)
        (root / "local" / "evil" / "1.0.0").symlink_to(outside, target_is_directory=True)

        assert list(LocalDirectorySource(root).list_artifacts()) == []

    def test_a_symlinked_artifact_cannot_be_fetched(self, tmp_path: Path):
        root = tmp_path / "registry"
        outside = tmp_path / "outside" / "local" / "evil" / "1.0.0"
        outside.mkdir(parents=True)
        (outside / "artifact.yaml").write_text(yaml.safe_dump({"digest": "x"}), encoding="utf-8")
        (root / "local" / "evil").mkdir(parents=True)
        (root / "local" / "evil" / "1.0.0").symlink_to(outside, target_is_directory=True)

        with pytest.raises(ArtifactNotFoundError):
            LocalDirectorySource(root).fetch(
                ArtifactId(namespace="local", name="evil", version=SemanticVersion.parse("1.0.0"))
            )

    def test_a_missing_root_is_unavailable_not_empty(self, tmp_path: Path):
        """An empty listing would read as "this source has nothing", which is a
        different and much quieter problem than "this source is not there"."""
        with pytest.raises(SourceUnavailableError):
            list(LocalDirectorySource(tmp_path / "absent").list_artifacts())

    def test_a_file_where_the_root_should_be_is_unavailable(self, tmp_path: Path):
        target = tmp_path / "not-a-dir"
        target.write_text("", encoding="utf-8")

        with pytest.raises(SourceUnavailableError):
            list(LocalDirectorySource(target).list_artifacts())


class TestTolerance:
    def test_stray_files_do_not_break_enumeration(self, populated: Path):
        """A source is a shared directory. Refusing to list anything because
        somebody left a README in it would make it unusable for one dead file."""
        (populated / "README.md").write_text("hello\n", encoding="utf-8")
        (populated / "local" / "house-standards" / "notes.txt").write_text("x", encoding="utf-8")

        assert len(list(LocalDirectorySource(populated).list_artifacts())) == 6

    def test_a_directory_that_is_not_a_version_is_skipped(self, populated: Path):
        (populated / "local" / "house-standards" / "draft").mkdir()
        (populated / "local" / "house-standards" / "draft" / "artifact.yaml").write_text(
            yaml.safe_dump({"digest": "x"}), encoding="utf-8"
        )

        assert len(list(LocalDirectorySource(populated).list_artifacts())) == 6

    def test_a_version_directory_without_a_manifest_is_not_an_artifact(self, populated: Path):
        (populated / "local" / "house-standards" / "3.0.0").mkdir()

        assert len(list(LocalDirectorySource(populated).list_artifacts())) == 6
