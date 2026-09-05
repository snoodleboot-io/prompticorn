"""`prompticorn cache` (PRO-127).

Every test relocates the store with `PROMPTICORN_HOME`. A cache test that ran
against the real one would either report the developer's own blobs or, far
worse, delete them.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from prompticorn.cli import cli
from prompticorn.store import BlobStore, store_paths

CONTENT = b"# Testing Strategies\n"


@pytest.fixture
def store(monkeypatch, tmp_path: Path) -> BlobStore:
    monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "store"))
    return BlobStore()


def run(*args):
    return CliRunner().invoke(cli, list(args))


class TestStatus:
    def test_an_empty_cache_says_so(self, store: BlobStore):
        result = run("cache", "status")

        assert result.exit_code == 0, result.output
        assert "empty" in result.output

    def test_a_populated_cache_reports_the_count(self, store: BlobStore):
        store.put(CONTENT)
        store.put(b"another\n")

        result = run("cache", "status")

        assert result.exit_code == 0, result.output
        assert "2 blob(s)" in result.output

    def test_status_names_the_store_location(self, store: BlobStore):
        """So a confused user can see which store they are actually looking at."""
        result = run("cache", "status")

        assert str(store.directory) in result.output

    def test_status_writes_nothing(self, store: BlobStore):
        store.put(CONTENT)

        run("cache", "status")

        assert list(store.blobs()) == [store.put(CONTENT)]


class TestClear:
    def test_yes_clears_without_prompting(self, store: BlobStore):
        store.put(CONTENT)

        result = run("cache", "clear", "--yes")

        assert result.exit_code == 0, result.output
        assert list(store.blobs()) == []

    def test_declining_the_prompt_keeps_the_cache(self, store: BlobStore):
        """A destructive default would be wrong even for a cache."""
        digest = store.put(CONTENT)

        result = CliRunner().invoke(cli, ["cache", "clear"], input="n\n")

        assert result.exit_code != 0
        assert list(store.blobs()) == [digest]

    def test_confirming_the_prompt_clears(self, store: BlobStore):
        store.put(CONTENT)

        result = CliRunner().invoke(cli, ["cache", "clear"], input="y\n")

        assert result.exit_code == 0, result.output
        assert list(store.blobs()) == []

    def test_clearing_an_empty_cache_is_not_an_error(self, store: BlobStore):
        result = run("cache", "clear", "--yes")

        assert result.exit_code == 0, result.output

    def test_a_cleared_cache_still_works(self, store: BlobStore):
        """Purging must leave a usable store, not a broken one."""
        store.put(CONTENT)
        run("cache", "clear", "--yes")

        assert store.read(store.put(CONTENT)) == CONTENT


def test_the_cache_commands_never_touch_the_real_store(monkeypatch, tmp_path: Path):
    """Guards the fixture above: if PROMPTICORN_HOME stopped being honoured,
    these tests would start deleting the developer's own cache."""
    monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "isolated"))

    assert str(tmp_path / "isolated") in str(BlobStore().directory)
