"""Tests for the development harness (PRO-143).

The harness provisions the environment and runs the verification lanes, so its
own logic has to be trustworthy without shelling out to the real toolchain. What
is covered here is the decision-making — lane selection, drift normalization,
failure reporting, change detection — not the subprocess calls themselves.
"""

import importlib.util
import sys
from argparse import Namespace
from pathlib import Path

import pytest

_HARNESS_PATH = Path(__file__).resolve().parents[2] / "tools" / "harness.py"


def _load_harness():
    """Import tools/harness.py by path — `scripts` is not an installed package."""
    spec = importlib.util.spec_from_file_location("_harness_under_test", _HARNESS_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


harness = _load_harness()


class TestLaneSelection:
    def test_fast_is_the_static_tier_only(self):
        """Measured: the test lanes run in minutes (unit 320s, integration 667s),
        so a `--fast` containing any of them would not be fast."""
        names = {lane.name for lane in harness._select_lanes(Namespace(fast=True, lane=None))}
        assert names == {"lint", "format", "types", "security"}

    def test_full_sweep_runs_the_real_unit_lane_not_the_watch_variant(self):
        """unit-watch is a subset of unit; running both would duplicate the work."""
        names = {lane.name for lane in harness._select_lanes(Namespace(fast=False, lane=None))}
        assert "unit" in names and "unit-watch" not in names
        assert {"integration", "slow"} <= names

    def test_explicit_lane_selection_wins_over_fast(self):
        lanes = harness._select_lanes(Namespace(fast=True, lane=["slow"]))
        assert [lane.name for lane in lanes] == ["slow"]

    def test_watch_lane_is_reachable_but_never_selected_by_default(self):
        """`watch` depends on it by name, so it must exist; neither default set
        should pick it up and duplicate the unit lane."""
        assert any(lane.name == "unit-watch" for lane in harness.LANES)
        for namespace in (Namespace(fast=True, lane=None), Namespace(fast=False, lane=None)):
            selected = {lane.name for lane in harness._select_lanes(namespace)}
            assert "unit-watch" not in selected

    def test_unknown_lane_is_rejected_rather_than_silently_dropped(self):
        with pytest.raises(SystemExit, match="nope"):
            harness._select_lanes(Namespace(fast=False, lane=["unit", "nope"]))

    def test_every_lane_shells_out_through_uv(self):
        """A lane that bypasses uv would run against whatever interpreter is
        ambient, which is exactly what `up` exists to stop."""
        assert all(lane.command[0] == "uv" for lane in harness.LANES)


class TestDriftNormalization:
    def test_build_date_is_not_treated_as_drift(self):
        older = b"# Config\n**Last Updated:** 2026-01-01  \n**Agent Count:** 26\n"
        newer = b"# Config\n**Last Updated:** 2026-08-09  \n**Agent Count:** 26\n"
        assert harness.normalize_generated("CLAUDE.md", older) == harness.normalize_generated(
            "CLAUDE.md", newer
        )

    def test_real_content_change_still_registers(self):
        before = b"**Last Updated:** 2026-01-01\n**Agent Count:** 24\n"
        after = b"**Last Updated:** 2026-01-01\n**Agent Count:** 26\n"
        assert harness.normalize_generated("CLAUDE.md", before) != harness.normalize_generated(
            "CLAUDE.md", after
        )

    def test_other_files_are_compared_verbatim(self):
        blob = b"**Last Updated:** 2026-01-01\nbody\n"
        assert harness.normalize_generated(".claude/agents/code-agent.md", blob) == blob


class TestReporting:
    def test_all_passing_reports_success(self, capsys):
        results = [
            harness.LaneResult("lint", True, 1.0, ""),
            harness.LaneResult("unit", True, 2.0, ""),
        ]
        assert harness._report(results) == 0
        assert "FAIL" not in capsys.readouterr().out

    def test_any_failure_fails_the_sweep_and_shows_its_output(self, capsys):
        results = [
            harness.LaneResult("lint", True, 1.0, ""),
            harness.LaneResult("unit", False, 2.0, "E   assert 1 == 2"),
        ]
        assert harness._report(results) == 1
        out = capsys.readouterr().out
        assert "FAIL  unit" in out
        assert "assert 1 == 2" in out

    def test_tail_keeps_the_end_of_long_output(self):
        tail = harness._tail("\n".join(str(n) for n in range(100)), lines=3)
        assert tail.split() == ["97", "98", "99"]


class TestGeneratedTreeContract:
    def test_persona_filtering_is_disabled_not_empty(self):
        """None skips filtering; [] filters down to universal agents only. The
        tracked tree was built with filtering off, and the difference is 10 agents."""
        assert harness.GENERATED_TREE_CONFIG["active_personas"] is None

    def test_variant_is_pinned_to_what_produced_the_tracked_tree(self):
        assert harness.GENERATED_TREE_CONFIG["variant"] == "verbose"

    def test_generated_paths_cover_both_the_tree_and_the_routing_file(self):
        assert set(harness.GENERATED_PATHS) == {".claude", "CLAUDE.md"}


class TestFileCollection:
    def test_collects_nested_files_and_top_level_file(self, tmp_path, monkeypatch):
        (tmp_path / ".claude" / "agents").mkdir(parents=True)
        (tmp_path / ".claude" / "agents" / "a.md").write_bytes(b"agent")
        (tmp_path / "CLAUDE.md").write_bytes(b"routing")
        (tmp_path / "unrelated.txt").write_bytes(b"ignored")

        collected = harness._relative_files(tmp_path)
        assert collected == {".claude/agents/a.md": b"agent", "CLAUDE.md": b"routing"}

    def test_missing_paths_are_simply_absent(self, tmp_path):
        assert harness._relative_files(tmp_path) == {}


class TestWatchSnapshot:
    def test_detects_a_modified_file(self, tmp_path):
        source = tmp_path / "mod.py"
        source.write_text("x = 1")
        first = harness._snapshot([tmp_path])

        import os

        os.utime(source, (0, 0))
        assert harness._snapshot([tmp_path]) != first

    def test_ignores_bytecode_caches(self, tmp_path):
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__pycache__" / "junk.py").write_text("x = 1")
        assert harness._snapshot([tmp_path]) == {}

    def test_only_python_sources_are_watched(self, tmp_path):
        (tmp_path / "notes.md").write_text("prose")
        assert harness._snapshot([tmp_path]) == {}
