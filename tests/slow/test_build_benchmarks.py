"""Build-performance benchmarks (PRO-11).

Dependency-free timing guards for the generation pipeline. The ceilings are
deliberately loose — several times a healthy local run — so they catch a gross
performance regression (an accidental O(n^2), a per-agent full-tree rescan)
without flaking on slow or loaded CI runners. Actual timings are printed for
trend visibility. Marked ``slow`` so they run only in the Slow Tests job.
"""

import time
from pathlib import Path

import pytest

from prompticorn.prompt_builder import get_prompt_builder
from prompticorn.tools import MENU_ORDER

_CONFIG = {"spec": {"language": "python"}, "active_personas": ["software_engineer"]}
# Generous ceilings: a healthy full build is well under a second per tool.
_SINGLE_TOOL_CEILING_S = 20.0
_ALL_TOOLS_CEILING_S = 90.0


def _timed_build(tool: str, root: Path) -> float:
    start = time.perf_counter()
    get_prompt_builder(tool).build(root, {**_CONFIG, "variant": "minimal"}, dry_run=False)
    return time.perf_counter() - start


@pytest.mark.slow
def test_single_tool_build_is_fast(tmp_path, capsys):
    """A single full build stays well under a generous ceiling."""
    elapsed = _timed_build("claude", tmp_path)
    with capsys.disabled():
        print(f"\n[benchmark] claude minimal build: {elapsed:.3f}s")
    assert elapsed < _SINGLE_TOOL_CEILING_S, (
        f"claude build took {elapsed:.2f}s, over the {_SINGLE_TOOL_CEILING_S}s ceiling"
    )


@pytest.mark.slow
def test_all_tools_build_within_budget(tmp_path, capsys):
    """Building every tool once stays within a whole-suite ceiling."""
    timings: dict[str, float] = {}
    for tool in MENU_ORDER:
        timings[tool] = _timed_build(tool, tmp_path / tool)
    total = sum(timings.values())
    slowest = max(timings, key=timings.get)
    with capsys.disabled():
        print(
            f"\n[benchmark] all {len(timings)} tools: {total:.2f}s "
            f"(slowest {slowest} {timings[slowest]:.3f}s)"
        )
    assert total < _ALL_TOOLS_CEILING_S, (
        f"building all tools took {total:.1f}s, over the {_ALL_TOOLS_CEILING_S}s ceiling"
    )
