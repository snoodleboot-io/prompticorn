"""Where machine-local state lives (PRO-127).

Two properties, and both are the kind that rot quietly. `PROMPTICORN_HOME` has
to be honoured by *every* path, not the ones somebody remembered — a store
relocatable for the cache but not the index is not relocatable. And the mode has
to be applied to directories that already exist, because the ones worth
tightening are the ones created before the rule did.
"""

from __future__ import annotations

import stat
import sys
from pathlib import Path

import pytest

from prompticorn.store import store_paths

ALL_PATHS = (
    store_paths.cas_root,
    store_paths.cas_staging,
    store_paths.database_path,
    store_paths.profiles_root,
    store_paths.user_content_root,
)


class TestHome:
    def test_defaults_under_the_user_home(self, monkeypatch):
        monkeypatch.delenv(store_paths.HOME_VARIABLE, raising=False)

        assert store_paths.home() == Path.home() / store_paths.DEFAULT_HOME_NAME

    def test_the_environment_variable_wins(self, monkeypatch, tmp_path: Path):
        monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "elsewhere"))

        assert store_paths.home() == tmp_path / "elsewhere"

    def test_a_tilde_in_the_override_is_expanded(self, monkeypatch):
        monkeypatch.setenv(store_paths.HOME_VARIABLE, "~/custom-store")

        assert store_paths.home() == Path.home() / "custom-store"

    def test_the_override_is_read_on_every_call(self, monkeypatch, tmp_path: Path):
        """Caching it would freeze whichever value happened to be set when the
        first module imported this one."""
        monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "first"))
        first = store_paths.home()
        monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "second"))

        assert first != store_paths.home()

    def test_an_empty_override_falls_back_rather_than_using_the_cwd(self, monkeypatch):
        """PROMPTICORN_HOME= in a shell profile must not put the store at ``.``."""
        monkeypatch.setenv(store_paths.HOME_VARIABLE, "")

        assert store_paths.home() == Path.home() / store_paths.DEFAULT_HOME_NAME


class TestEveryPathHonoursTheOverride:
    @pytest.mark.parametrize("resolve", ALL_PATHS, ids=lambda f: f.__name__)
    def test_path_sits_under_the_configured_home(self, resolve, monkeypatch, tmp_path: Path):
        monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "store"))

        assert (tmp_path / "store") in resolve().parents or resolve() == tmp_path / "store"

    def test_staging_lives_inside_the_cas(self, monkeypatch, tmp_path: Path):
        """The final move must be a rename within one filesystem to be atomic.
        Staging under /tmp can be on another device, where os.replace degrades
        to a copy and stops being atomic at all."""
        monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "store"))

        assert store_paths.cas_root() in store_paths.cas_staging().parents


class TestPermissions:
    @pytest.mark.skipif(sys.platform == "win32", reason="POSIX mode bits")
    def test_a_created_directory_is_owner_only(self, tmp_path: Path):
        created = store_paths.ensure_directory(tmp_path / "store" / "cas")

        assert stat.S_IMODE(created.stat().st_mode) == store_paths.DIRECTORY_MODE

    @pytest.mark.skipif(sys.platform == "win32", reason="POSIX mode bits")
    def test_an_existing_permissive_directory_is_tightened(self, tmp_path: Path):
        """The store records every repository on this machine, and in time
        credentials for the sources it pulls from. A directory created under a
        loose umask by an older version is exactly the one worth fixing."""
        loose = tmp_path / "store"
        loose.mkdir(mode=0o755)

        store_paths.ensure_directory(loose)

        assert stat.S_IMODE(loose.stat().st_mode) == store_paths.DIRECTORY_MODE

    def test_creating_an_existing_directory_is_not_an_error(self, tmp_path: Path):
        store_paths.ensure_directory(tmp_path / "store")

        assert store_paths.ensure_directory(tmp_path / "store").is_dir()

    def test_parents_are_created(self, tmp_path: Path):
        assert store_paths.ensure_directory(tmp_path / "a" / "b" / "c").is_dir()
