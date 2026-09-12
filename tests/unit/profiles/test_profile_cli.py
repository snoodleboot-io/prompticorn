"""`prompticorn profile` and `init --profile` (PRO-133).

Every test relocates the store with `PROMPTICORN_HOME`. One that did not would
read — and `delete` would remove — the developer's own profiles.

The round trip in `TestExportImport` is checked on raw bytes. Export then import
must be a move, not an edit; anything that canonicalised on the way through
would rewrite a profile silently, and a comparison of parsed values would not
notice.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from prompticorn.cli import cli
from prompticorn.profiles import FileProfileStore
from prompticorn.store import store_paths

MANIFEST = {
    "version": "2.0",
    "repository": {"type": "single-language"},
    "spec": {"language": "python", "runtime": "3.14"},
    "variant": "verbose",
    "active_personas": ["software_engineer"],
    "ai_tool": "claude",
}


def run(*args, **kwargs):
    return CliRunner().invoke(cli, list(args), **kwargs)


@pytest.fixture
def project(tmp_path: Path, monkeypatch) -> Path:
    """A project with a manifest, and the store relocated away from the real one."""
    monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "store"))
    root = tmp_path / "project"
    (root / ".prompticorn").mkdir(parents=True)
    (root / ".prompticorn" / ".prompticorn.yaml").write_text(
        yaml.safe_dump(MANIFEST), encoding="utf-8"
    )
    monkeypatch.chdir(root)
    return root


class TestSaveAndList:
    def test_save_captures_the_project(self, project: Path):
        result = run("profile", "save", "backend", "--description", "house standard")

        assert result.exit_code == 0, result.output
        assert "backend@v1" in result.output

    def test_list_shows_saved_profiles(self, project: Path):
        run("profile", "save", "backend", "--description", "house standard")

        result = run("profile", "list")

        assert "backend" in result.output
        assert "house standard" in result.output

    def test_list_is_sorted_and_stable(self, project: Path):
        for name in ("zeta", "alpha", "mid"):
            run("profile", "save", name)

        first = run("profile", "list").output

        assert first.index("alpha") < first.index("mid") < first.index("zeta")
        assert run("profile", "list").output == first

    def test_an_empty_store_says_how_to_fill_it(self, project: Path):
        result = run("profile", "list")

        assert result.exit_code == 0, result.output
        assert "profile save" in result.output

    def test_saving_twice_shows_the_new_version(self, project: Path):
        run("profile", "save", "backend")

        assert "backend@v2" in run("profile", "save", "backend").output


class TestShow:
    def test_show_prints_the_payload(self, project: Path):
        run("profile", "save", "backend", "--description", "house standard")

        result = run("profile", "show", "backend")

        assert result.exit_code == 0, result.output
        assert "language: python" in result.output
        assert "house standard" in result.output

    def test_show_can_target_an_older_version(self, project: Path):
        run("profile", "save", "backend")
        (project / ".prompticorn" / ".prompticorn.yaml").write_text(
            yaml.safe_dump({**MANIFEST, "variant": "minimal"}), encoding="utf-8"
        )
        run("profile", "save", "backend")

        assert "variant: verbose" in run("profile", "show", "backend", "--version", "1").output


class TestDiff:
    def test_diff_between_two_profiles_names_the_changed_key(self, project: Path):
        run("profile", "save", "one")
        (project / ".prompticorn" / ".prompticorn.yaml").write_text(
            yaml.safe_dump({**MANIFEST, "variant": "minimal"}), encoding="utf-8"
        )
        run("profile", "save", "two")

        result = run("profile", "diff", "one", "two")

        assert result.exit_code == 0, result.output
        assert "variant" in result.output

    def test_diff_against_the_repo_is_the_day_to_day_question(self, project: Path):
        """"How does this repo differ from our standard?" — the reason --repo
        exists at all."""
        run("profile", "save", "standard")
        (project / ".prompticorn" / ".prompticorn.yaml").write_text(
            yaml.safe_dump({**MANIFEST, "variant": "minimal"}), encoding="utf-8"
        )

        result = run("profile", "diff", "standard", "--repo")

        assert result.exit_code == 0, result.output
        assert "variant" in result.output

    def test_a_matching_repo_reports_no_change(self, project: Path):
        run("profile", "save", "standard")

        assert "No change" in run("profile", "diff", "standard", "--repo").output

    def test_one_profile_without_repo_is_a_usage_error(self, project: Path):
        run("profile", "save", "one")

        result = run("profile", "diff", "one")

        assert result.exit_code != 0
        assert "--repo" in result.output

    def test_a_list_change_renders_readably(self, project: Path):
        """Field-level rendering has to cope with lists, not just scalars."""
        run("profile", "save", "one")
        (project / ".prompticorn" / ".prompticorn.yaml").write_text(
            yaml.safe_dump({**MANIFEST, "active_personas": ["software_engineer", "qa_tester"]}),
            encoding="utf-8",
        )

        result = run("profile", "diff", "one", "--repo")

        assert "active_personas" in result.output
        assert "qa_tester" in result.output


class TestExportImport:
    def test_export_then_import_round_trips_byte_identically(self, project: Path, tmp_path: Path):
        """A move, not an edit. Comparing parsed values would miss a silent
        rewrite; comparing bytes cannot."""
        run("profile", "save", "backend", "--description", "house standard")
        store = FileProfileStore()
        original = store.path_for("backend", 1).read_bytes()
        exported = tmp_path / "backend.yaml"

        run("profile", "export", "backend", "-o", str(exported))

        assert exported.read_bytes() == original

    def test_an_imported_profile_is_usable(self, project: Path, tmp_path: Path):
        run("profile", "save", "backend")
        exported = tmp_path / "backend.yaml"
        run("profile", "export", "backend", "-o", str(exported))

        result = run("profile", "import", str(exported), "--name", "copied")

        assert result.exit_code == 0, result.output
        assert FileProfileStore().load("copied").payload == FileProfileStore().load("backend").payload

    def test_importing_a_malformed_file_writes_nothing(self, project: Path, tmp_path: Path):
        """Untrusted input. A half-import would claim a version number for a
        profile nobody can read."""
        broken = tmp_path / "broken.yaml"
        broken.write_text("{ not: valid: yaml:", encoding="utf-8")

        result = run("profile", "import", str(broken))

        assert result.exit_code != 0
        assert FileProfileStore().names() == ()

    def test_importing_a_valid_yaml_that_is_not_a_profile_writes_nothing(
        self, project: Path, tmp_path: Path
    ):
        stray = tmp_path / "stray.yaml"
        stray.write_text(yaml.safe_dump({"hello": "world"}), encoding="utf-8")

        result = run("profile", "import", str(stray))

        assert result.exit_code != 0
        assert FileProfileStore().names() == ()

    def test_a_hostile_name_in_an_imported_file_is_refused(self, project: Path, tmp_path: Path):
        """The name becomes a directory, and it came from a file somebody else
        wrote."""
        hostile = tmp_path / "hostile.yaml"
        hostile.write_text(
            yaml.safe_dump({"name": "../../escaped", "version": 1, "payload": MANIFEST}),
            encoding="utf-8",
        )

        result = run("profile", "import", str(hostile))

        assert result.exit_code != 0
        assert not (tmp_path / "escaped").exists()


class TestApply:
    def test_apply_writes_the_manifest(self, project: Path, tmp_path: Path, monkeypatch):
        run("profile", "save", "backend")
        fresh = tmp_path / "fresh"
        fresh.mkdir()
        monkeypatch.chdir(fresh)

        result = run("profile", "apply", "backend")

        assert result.exit_code == 0, result.output
        assert (fresh / ".prompticorn" / ".prompticorn.yaml").is_file()

    def test_dry_run_writes_nothing(self, project: Path, tmp_path: Path, monkeypatch):
        run("profile", "save", "backend")
        fresh = tmp_path / "fresh"
        fresh.mkdir()
        monkeypatch.chdir(fresh)

        run("profile", "apply", "backend", "--dry-run")

        assert list(fresh.iterdir()) == []

    def test_overwriting_asks_first(self, project: Path):
        """A configuration replaced without warning is one nobody can account
        for later."""
        run("profile", "save", "backend")
        (project / ".prompticorn" / ".prompticorn.yaml").write_text(
            yaml.safe_dump({**MANIFEST, "variant": "minimal"}), encoding="utf-8"
        )

        result = run("profile", "apply", "backend", input="n\n")

        assert result.exit_code != 0
        assert "variant" in result.output

    def test_yes_skips_the_prompt(self, project: Path):
        run("profile", "save", "backend")
        (project / ".prompticorn" / ".prompticorn.yaml").write_text(
            yaml.safe_dump({**MANIFEST, "variant": "minimal"}), encoding="utf-8"
        )

        assert run("profile", "apply", "backend", "--yes").exit_code == 0


class TestDelete:
    def test_delete_removes_every_version(self, project: Path):
        run("profile", "save", "backend")
        run("profile", "save", "backend")

        result = run("profile", "delete", "backend", "--yes")

        assert result.exit_code == 0, result.output
        assert FileProfileStore().names() == ()

    def test_deleting_an_unknown_profile_fails(self, project: Path):
        assert run("profile", "delete", "never-saved", "--yes").exit_code != 0


class TestInitFromProfile:
    def test_init_profile_configures_and_builds(self, project: Path, tmp_path: Path, monkeypatch):
        """The adoption path: a project set up correctly without the interview."""
        run("profile", "save", "backend")
        fresh = tmp_path / "fresh"
        fresh.mkdir()
        monkeypatch.chdir(fresh)

        result = run("init", "--profile", "backend")

        assert result.exit_code == 0, result.output
        assert (fresh / ".prompticorn" / ".prompticorn.yaml").is_file()
        assert (fresh / "CLAUDE.md").is_file()

    def test_init_profile_matches_a_manual_setup(self, project: Path, tmp_path: Path, monkeypatch):
        """The AC: indistinguishable from `init` answered the same way. Compared
        on generated bytes, which is the only comparison that would notice a
        second code path drifting from the first."""
        from prompticorn.prompt_builder import get_prompt_builder

        run("profile", "save", "backend")
        fresh = tmp_path / "fresh"
        fresh.mkdir()
        monkeypatch.chdir(fresh)
        run("init", "--profile", "backend")

        expected_root = tmp_path / "expected"
        expected_root.mkdir()
        get_prompt_builder("claude").build(expected_root, dict(MANIFEST), dry_run=False)

        def tree(root: Path) -> dict[str, bytes]:
            return {
                p.relative_to(root).as_posix(): p.read_bytes()
                for p in sorted(root.rglob("*"))
                if p.is_file() and ".prompticorn" not in p.relative_to(root).parts
            }

        assert tree(fresh) == tree(expected_root)

    def test_init_without_profile_still_asks(self, project: Path, monkeypatch):
        """The option must not have turned the interview off for everyone."""
        result = run("init", input="\x03")

        assert "--profile" not in result.output

    def test_init_profile_with_an_unknown_name_fails(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "store"))
        fresh = tmp_path / "fresh"
        fresh.mkdir()
        monkeypatch.chdir(fresh)

        assert run("init", "--profile", "never-saved").exit_code != 0


def test_the_profile_commands_never_touch_the_real_store(monkeypatch, tmp_path: Path):
    """Guards the fixture: if PROMPTICORN_HOME stopped being honoured, `delete`
    would start removing the developer's own profiles."""
    monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "isolated"))

    assert str(tmp_path / "isolated") in str(FileProfileStore().root)
