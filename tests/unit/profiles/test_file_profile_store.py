"""Profiles on disk (PRO-130).

Two properties carry this. Versions are immutable, which is what makes
comparing two of them meaningful and rolling back a copy. And writes are atomic,
because a profile configures a repository — a truncated one would configure it
*wrongly* rather than fail, which is the quieter and worse outcome.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from prompticorn.profiles import (
    FileProfileStore,
    InvalidProfileError,
    InvalidProfileNameError,
    ProfileNotFoundError,
)

NOW = "2026-09-12T12:00:00Z"
PAYLOAD = {"spec": {"language": "python"}, "variant": "verbose", "ai_tool": "claude"}


@pytest.fixture
def store(tmp_path: Path) -> FileProfileStore:
    return FileProfileStore(root=tmp_path / "profiles")


class TestRoundTrip:
    def test_save_then_load_preserves_the_payload_exactly(self, store: FileProfileStore):
        store.save("backend", PAYLOAD, "house standard", NOW)

        assert store.load("backend").payload == PAYLOAD

    def test_metadata_survives(self, store: FileProfileStore):
        store.save("backend", PAYLOAD, "house standard", NOW)

        loaded = store.load("backend")

        assert (loaded.name, loaded.description, loaded.created_at) == (
            "backend",
            "house standard",
            NOW,
        )

    def test_the_first_version_is_one(self, store: FileProfileStore):
        """`v1` is what anyone expects the first thing to be called."""
        assert store.save("backend", PAYLOAD, "", NOW).version == 1

    def test_an_unknown_profile_raises(self, store: FileProfileStore):
        with pytest.raises(ProfileNotFoundError):
            store.load("never-saved")

    def test_an_unknown_version_raises(self, store: FileProfileStore):
        store.save("backend", PAYLOAD, "", NOW)

        with pytest.raises(ProfileNotFoundError):
            store.load("backend", version=7)


class TestImmutableVersions:
    def test_saving_again_produces_the_next_version(self, store: FileProfileStore):
        store.save("backend", PAYLOAD, "", NOW)

        assert store.save("backend", {"spec": {"language": "go"}}, "", NOW).version == 2

    def test_saving_never_destroys_an_earlier_version(self, store: FileProfileStore):
        """What makes `diff v1 v2` a comparison rather than a guess."""
        store.save("backend", PAYLOAD, "", NOW)
        store.save("backend", {"spec": {"language": "go"}}, "", NOW)

        assert store.load("backend", version=1).payload == PAYLOAD

    def test_load_defaults_to_the_newest(self, store: FileProfileStore):
        store.save("backend", PAYLOAD, "", NOW)
        store.save("backend", {"spec": {"language": "go"}}, "", NOW)

        assert store.load("backend").version == 2

    def test_versions_are_listed_ascending(self, store: FileProfileStore):
        for _ in range(3):
            store.save("backend", PAYLOAD, "", NOW)

        assert store.versions_of("backend") == (1, 2, 3)

    def test_a_claimed_version_is_not_reused(self, store: FileProfileStore):
        """Simulates the loser of a race: v2 already exists when save runs."""
        store.save("backend", PAYLOAD, "", NOW)
        store.path_for("backend", 2).write_text(
            yaml.safe_dump({"name": "backend", "version": 2, "payload": {"claimed": True}}),
            encoding="utf-8",
        )

        assert store.save("backend", PAYLOAD, "", NOW).version == 3
        assert store.load("backend", version=2).payload == {"claimed": True}


class TestAtomicity:
    def test_a_crash_before_replace_leaves_the_previous_version_intact(
        self, store: FileProfileStore, monkeypatch
    ):
        """Crash injection at the one moment that matters."""
        store.save("backend", PAYLOAD, "", NOW)

        def exploding(*_args, **_kwargs):
            raise OSError("disk full")

        monkeypatch.setattr(os, "replace", exploding)

        with pytest.raises(OSError):
            store.save("backend", {"spec": {"language": "go"}}, "", NOW)

        assert store.load("backend", version=1).payload == PAYLOAD

    def test_a_crash_leaves_no_empty_version_behind(self, store: FileProfileStore, monkeypatch):
        """The version number is claimed by creating the file, so between the
        claim and the write the path exists and is empty. A crash there must not
        leave a version that is listable, loadable, and says nothing."""
        store.save("backend", PAYLOAD, "", NOW)

        def exploding(*_args, **_kwargs):
            raise OSError("disk full")

        monkeypatch.setattr(os, "replace", exploding)

        with pytest.raises(OSError):
            store.save("backend", {"spec": {"language": "go"}}, "", NOW)

        assert store.versions_of("backend") == (1,)
        assert store.current_version("backend") == 1

    def test_a_crash_leaves_no_staged_file_behind(self, store: FileProfileStore, monkeypatch):
        def exploding(*_args, **_kwargs):
            raise OSError("disk full")

        monkeypatch.setattr(os, "replace", exploding)

        with pytest.raises(OSError):
            store.save("backend", PAYLOAD, "", NOW)

        assert list(store.directory_for("backend").glob("*.partial")) == []

    def test_no_partial_file_is_ever_readable_as_a_profile(self, store: FileProfileStore):
        """The staged file has a suffix that the version pattern does not match,
        so a leftover cannot be mistaken for a version."""
        store.save("backend", PAYLOAD, "", NOW)
        (store.directory_for("backend") / "v99.yaml.partial").write_text("junk", encoding="utf-8")

        assert store.versions_of("backend") == (1,)


class TestNames:
    @pytest.mark.parametrize(
        "name",
        ["../escape", "a/b", "", ".hidden", "-leading", "x" * 65, "with space", "na\\me"],
        ids=["traversal", "separator", "empty", "leading dot", "leading dash", "too long", "space", "backslash"],
    )
    def test_an_unusable_name_is_refused(self, store: FileProfileStore, name: str):
        """Names become directories. Sanitising instead of refusing would let
        `save` and `load` disagree about where a profile lives."""
        with pytest.raises(InvalidProfileNameError):
            store.save(name, PAYLOAD, "", NOW)

    @pytest.mark.parametrize("name", ["backend", "backend-api", "backend_api", "api.v2", "a1"])
    def test_a_reasonable_name_is_accepted(self, store: FileProfileStore, name: str):
        assert store.save(name, PAYLOAD, "", NOW).name == name

    def test_traversal_is_refused_on_read_too(self, store: FileProfileStore):
        with pytest.raises(InvalidProfileNameError):
            store.load("../../etc/passwd")


class TestListing:
    def test_names_are_sorted(self, store: FileProfileStore):
        for name in ("zeta", "alpha", "mid"):
            store.save(name, PAYLOAD, "", NOW)

        assert store.names() == ("alpha", "mid", "zeta")

    def test_an_absent_store_lists_nothing(self, tmp_path: Path):
        assert FileProfileStore(root=tmp_path / "never-created").names() == ()

    def test_versions_of_an_unknown_profile_is_empty(self, store: FileProfileStore):
        assert store.versions_of("never-saved") == ()


class TestCorruption:
    def test_an_unparseable_profile_is_reported_not_skipped(self, store: FileProfileStore):
        store.save("backend", PAYLOAD, "", NOW)
        store.path_for("backend", 1).write_text("{ not: valid: yaml:", encoding="utf-8")

        with pytest.raises(InvalidProfileError):
            store.load("backend")

    def test_a_valid_yaml_that_is_not_a_profile_is_reported(self, store: FileProfileStore):
        store.save("backend", PAYLOAD, "", NOW)
        store.path_for("backend", 1).write_text(yaml.safe_dump({"hello": 1}), encoding="utf-8")

        with pytest.raises(InvalidProfileError):
            store.load("backend")


class TestDeletion:
    def test_deleting_removes_every_version(self, store: FileProfileStore):
        store.save("backend", PAYLOAD, "", NOW)
        store.save("backend", PAYLOAD, "", NOW)

        assert store.delete("backend") == 2
        assert store.names() == ()

    def test_deleting_an_unknown_profile_raises(self, store: FileProfileStore):
        with pytest.raises(ProfileNotFoundError):
            store.delete("never-saved")


class TestStoreLocation:
    def test_the_default_root_follows_prompticorn_home(self, monkeypatch, tmp_path: Path):
        """A store relocatable for the cache but not for profiles is not
        relocatable, and a test that wrote to the real home would litter the
        developer's machine."""
        from prompticorn.store import store_paths

        monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "store"))

        assert FileProfileStore().root == tmp_path / "store" / "profiles"

    def test_the_root_is_resolved_late(self, monkeypatch, tmp_path: Path):
        """Built at import time, a store must not freeze the value the variable
        happened to have first."""
        from prompticorn.store import store_paths

        store = FileProfileStore()
        monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "one"))
        first = store.root
        monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "two"))

        assert store.root != first

    @pytest.mark.skipif(os.name == "nt", reason="POSIX mode bits")
    def test_a_created_profile_directory_is_owner_only(self, monkeypatch, tmp_path: Path):
        """Profiles can carry project detail worth keeping to oneself on a
        shared machine."""
        import stat

        from prompticorn.store import store_paths

        monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "store"))
        store = FileProfileStore()
        store.save("backend", PAYLOAD, "", NOW)

        mode = stat.S_IMODE(store.directory_for("backend").stat().st_mode)
        assert mode == store_paths.DIRECTORY_MODE
