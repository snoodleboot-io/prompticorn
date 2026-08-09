"""v1 → v2 manifest migration (PRO-109).

Three properties matter here and none of them is the version number itself:

- an existing config keeps producing **byte-identical output**,
- the migration is **idempotent**, and
- a save after a load does not eat the author's **comments**.

The last one is the sharp edge. ``ruamel`` preserves comments only while the
object graph stays its own ``CommentedMap``; a migration that assigned a plain
``dict`` anywhere would pass every other test here and silently destroy user
files.
"""

import io

import pytest
from ruamel.yaml import YAML

from prompticorn.config_handler import ConfigHandler
from prompticorn.manifest import SCHEMA_VERSION_V2
from prompticorn.prompt_builder import get_prompt_builder
from tests.golden_corpus import manifest

# A v1 config carrying the things a real user file carries: comments in three
# positions, a deliberately non-alphabetical key order, and a list.
V1_WITH_COMMENTS = """\
# Prompticorn configuration for the payments service.
# Owned by the platform team.
version: '1.0'
repository:
  type: single-language
  mappings: {}
spec:
  language: python  # pinned deliberately; see ADR-14
  runtime: '3.14'
  linters:
    - ruff  # keep first
    - pyright
variant: minimal
# Personas drive which agents get emitted.
active_personas:
  - software_engineer
"""


def _write(tmp_path, text: str):
    config_path = tmp_path / ".prompticorn.yaml"
    config_path.write_text(text, encoding="utf-8")
    return config_path


# ── AC 2: idempotency ──────────────────────────────────────────────────────────


def test_migration_stamps_the_current_schema_version() -> None:
    config = {"version": "1.0", "spec": {"language": "python"}}

    ConfigHandler._migrate_v1_to_v2(config)

    assert config["version"] == SCHEMA_VERSION_V2


def test_migration_is_idempotent() -> None:
    """AC 2: running it twice is a no-op."""
    config = {"version": "1.0", "spec": {"language": "python"}}

    ConfigHandler._migrate_v1_to_v2(config)
    after_once = dict(config)
    ConfigHandler._migrate_v1_to_v2(config)

    assert config == after_once


def test_migration_leaves_a_v2_config_untouched() -> None:
    config = {"version": SCHEMA_VERSION_V2, "spec": {"language": "python"}}
    before = dict(config)

    ConfigHandler._migrate_v1_to_v2(config)

    assert config == before


def test_migration_changes_nothing_but_the_version() -> None:
    """v2 is purely additive, so there is no shape to rewrite."""
    config = {"version": "1.0", "spec": {"language": "python"}, "variant": "minimal"}

    ConfigHandler._migrate_v1_to_v2(config)

    assert config == {**config, "spec": {"language": "python"}, "variant": "minimal"}
    assert set(config) == {"version", "spec", "variant"}


def test_an_absent_version_is_migrated_too() -> None:
    """Configs predating the key are v1 by definition."""
    config = {"spec": {"language": "python"}}

    ConfigHandler._migrate_v1_to_v2(config)

    assert config["version"] == SCHEMA_VERSION_V2


def test_an_empty_config_is_left_alone() -> None:
    """A missing file loads as {}; stamping it would invent a config."""
    config: dict = {}

    ConfigHandler._migrate_v1_to_v2(config)

    assert config == {}


def test_loading_applies_the_migration(tmp_path) -> None:
    config_path = _write(tmp_path, "version: '1.0'\nspec:\n  language: python\n")

    assert ConfigHandler.load_config(config_path)["version"] == SCHEMA_VERSION_V2


def test_loading_repeatedly_is_stable(tmp_path) -> None:
    """The file is not rewritten on load, so every load sees v1 and migrates."""
    config_path = _write(tmp_path, V1_WITH_COMMENTS)

    first = ConfigHandler.load_config(config_path)
    second = ConfigHandler.load_config(config_path)

    assert first == second
    assert config_path.read_text(encoding="utf-8") == V1_WITH_COMMENTS


# ── AC 4: ruamel round-trip preserves comments and key order ───────────────────


def test_save_after_load_preserves_comments(tmp_path) -> None:
    """AC 4, and the reason the migration touches exactly one scalar.

    A migration that replaced any mapping with a plain dict would pass every
    other test in this file and silently delete these comments.
    """
    config_path = _write(tmp_path, V1_WITH_COMMENTS)

    config = ConfigHandler.load_config(config_path)
    ConfigHandler.save_config(config, config_path)
    written = config_path.read_text(encoding="utf-8")

    assert "# Prompticorn configuration for the payments service." in written
    assert "# Owned by the platform team." in written
    assert "# pinned deliberately; see ADR-14" in written
    assert "# keep first" in written
    assert "# Personas drive which agents get emitted." in written


def test_save_after_load_preserves_key_order(tmp_path) -> None:
    """AC 4: the author's ordering is theirs, not ours to normalise."""
    config_path = _write(tmp_path, V1_WITH_COMMENTS)

    config = ConfigHandler.load_config(config_path)
    ConfigHandler.save_config(config, config_path)

    reloaded = YAML().load(config_path.read_text(encoding="utf-8"))
    assert list(reloaded) == ["version", "repository", "spec", "variant", "active_personas"]


def test_save_after_load_changes_only_the_version_line(tmp_path) -> None:
    """The strongest form of AC 4: diff the file, expect exactly one line moved."""
    config_path = _write(tmp_path, V1_WITH_COMMENTS)

    ConfigHandler.save_config(ConfigHandler.load_config(config_path), config_path)
    written = config_path.read_text(encoding="utf-8")

    before = [line for line in V1_WITH_COMMENTS.splitlines() if not line.startswith("version:")]
    after = [line for line in written.splitlines() if not line.startswith("version:")]
    assert before == after
    assert "version: '2.0'" in written


def test_the_comment_guard_would_actually_catch_a_regression(tmp_path) -> None:
    """Proves the assertions above are load-bearing rather than vacuous.

    Rebuilding the mapping as a plain dict — the mistake this design avoids — must
    visibly lose the comments.
    """
    config_path = _write(tmp_path, V1_WITH_COMMENTS)
    plain = dict(ConfigHandler.load_config(config_path))

    stream = io.StringIO()
    YAML().dump(plain, stream)

    assert "# Owned by the platform team." not in stream.getvalue()


# ── AC 5: both repository shapes ───────────────────────────────────────────────

MONOREPO_V1 = """\
version: '1.0'
repository:
  type: multi-language-monorepo
  mappings: {}
spec:
  - folder: backend/api   # the python side
    type: backend
    language: python
  - folder: frontend/ui
    type: frontend
    language: typescript
variant: minimal
"""


@pytest.mark.parametrize(
    ("source", "expected_type"),
    [(V1_WITH_COMMENTS, "single-language"), (MONOREPO_V1, "multi-language-monorepo")],
)
def test_migration_covers_both_repository_shapes(tmp_path, source: str, expected_type: str) -> None:
    """AC 5: `spec` is a dict in one shape and a list in the other."""
    config_path = _write(tmp_path, source)

    config = ConfigHandler.load_config(config_path)

    assert config["version"] == SCHEMA_VERSION_V2
    assert config["repository"]["type"] == expected_type


def test_monorepo_comments_survive_a_round_trip(tmp_path) -> None:
    """The list-shaped spec has its own comment-attachment behaviour in ruamel."""
    config_path = _write(tmp_path, MONOREPO_V1)

    ConfigHandler.save_config(ConfigHandler.load_config(config_path), config_path)

    assert "# the python side" in config_path.read_text(encoding="utf-8")


# ── AC 1: a v1 config still produces byte-identical output ─────────────────────


@pytest.mark.parametrize("tool", ["claude", "cursor"])
def test_a_v1_config_builds_byte_identically_to_a_v2_one(tmp_path, tool: str) -> None:
    """AC 1, stated as the property that actually matters.

    v2 is additive, so a config that gains only the version stamp must generate
    exactly the same bytes. This is the guard against the migration leaking into
    output — the golden corpus catches it repo-wide, this catches it here.
    """
    config_v1 = {"version": "1.0", "spec": {"language": "python"}, "variant": "minimal"}
    config_v2 = {**config_v1, "version": SCHEMA_VERSION_V2}

    roots = []
    for index, config in enumerate((config_v1, config_v2)):
        root = tmp_path / f"build{index}"
        root.mkdir()
        get_prompt_builder(tool).build(root, config, dry_run=False)
        roots.append(manifest(root))

    assert roots[0] == roots[1]
    assert roots[0], "build produced no files; the comparison would be vacuous"


def test_declaring_artifacts_does_not_change_output(tmp_path) -> None:
    """The new keys are inert until the lockfile milestone consumes them.

    If this ever fails, `artifacts:` has started influencing generation early —
    which would make the manifest and the lock disagree about what was built.
    """
    base = {"version": SCHEMA_VERSION_V2, "spec": {"language": "python"}, "variant": "minimal"}
    with_artifacts = {
        **base,
        "sources": [{"name": "acme", "type": "builtin"}],
        "artifacts": [{"name": "acme/sec", "version": ">=2.1,<3", "source": "acme"}],
    }

    roots = []
    for index, config in enumerate((base, with_artifacts)):
        root = tmp_path / f"out{index}"
        root.mkdir()
        get_prompt_builder("claude").build(root, config, dry_run=False)
        roots.append(manifest(root))

    assert roots[0] == roots[1]
