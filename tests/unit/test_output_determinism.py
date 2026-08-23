"""Emitted output does not depend on when or where it was built (PRO-116).

The reproducibility matrix rests entirely on this. A generated tree that varies
with the wall clock cannot be locked on one machine and verified on another —
and the failure is invisible until two runs straddle a day boundary, which is
how it reached CI in PRO-112 and again here.

`CLAUDE.md` stamped ``datetime.now()`` into a "Last Updated" line until PRO-116.
That was ``datetime.now()``, not ``utcnow()``, so two runners in different
timezones disagreed at the *same instant* — not merely across a day.

Two tests, guarding the property from opposite ends. `test_a_date_boundary_does_
not_change_the_output` measures it, which is the only way to be sure. The source
scan catches a reintroduction on the platform where the measurement cannot run,
and names the offending line instead of leaving a digest mismatch to be traced
back by hand.
"""

from __future__ import annotations

import ast
import os
import tempfile
import time
from pathlib import Path

import pytest

from prompticorn.prompt_builder import get_prompt_builder

PACKAGE = Path(__file__).resolve().parents[2] / "prompticorn"

# The modules that turn source content into emitted files. `cli.py` is
# deliberately absent: it reads the clock to stamp the lock's ``resolved_at``,
# and the lock is bookkeeping about a build rather than part of one.
EMIT_PATH = (
    "builders",
    "prompt_builder.py",
    "prompt_builders",
    "provenance",
    "skills_packager.py",
)

# Reading any of these makes output depend on when the build ran.
_CLOCK_CALLS = frozenset(
    {"now", "utcnow", "today", "time", "time_ns", "localtime", "gmtime", "monotonic"}
)
_CLOCK_MODULES = frozenset({"datetime", "date", "time", "calendar"})

CONFIG = {
    "repository": {"type": "single-language"},
    "spec": {"language": "python"},
    "active_personas": ["software_engineer"],
    "variant": "minimal",
}

# Two real timezones that are on different calendar dates at the same instant:
# Kiritimati is UTC+14 and Midway UTC-11, 25 hours apart.
_EAST = "Pacific/Kiritimati"
_WEST = "Pacific/Midway"


def _emit_path_modules() -> list[Path]:
    modules: list[Path] = []
    for entry in EMIT_PATH:
        target = PACKAGE / entry
        if target.is_file():
            modules.append(target)
        else:
            modules.extend(path for path in target.rglob("*.py") if "__pycache__" not in path.parts)
    return sorted(modules)


def _clock_reads(module: Path) -> list[str]:
    """``module:line`` for every call that reads the clock."""
    tree = ast.parse(module.read_text(encoding="utf-8"))
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr not in _CLOCK_CALLS:
            continue
        owner = node.func.value
        name = owner.id if isinstance(owner, ast.Name) else getattr(owner, "attr", None)
        if name in _CLOCK_MODULES:
            found.append(f"{module.name}:{node.lineno} ({name}.{node.func.attr})")
    return found


def _build(tool: str) -> dict[str, bytes]:
    """Build one tool into a throwaway directory and return its files."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        get_prompt_builder(tool).build(root, dict(CONFIG), dry_run=False)
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }


def _build_under(timezone: str, tool: str) -> tuple[str, dict[str, bytes]]:
    """Build with ``TZ`` set, returning the local date it saw and the output."""
    previous = os.environ.get("TZ")
    os.environ["TZ"] = timezone
    time.tzset()
    try:
        return time.strftime("%Y-%m-%d"), _build(tool)
    finally:
        if previous is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = previous
        time.tzset()


class TestNothingInTheEmitPathReadsTheClock:
    def test_no_emitting_module_reads_the_clock(self):
        offenders = {
            module.relative_to(PACKAGE).as_posix(): reads
            for module in _emit_path_modules()
            if (reads := _clock_reads(module))
        }

        assert not offenders, (
            "these make emitted output depend on when the build ran, which "
            f"breaks lock/verify across a day boundary: {offenders}"
        )

    def test_the_scan_actually_finds_something(self, tmp_path: Path):
        """A scanner that silently matches nothing would pass forever."""
        planted = tmp_path / "planted.py"
        planted.write_text(
            "from datetime import datetime\n\nstamp = datetime.now().strftime('%Y-%m-%d')\n",
            encoding="utf-8",
        )

        assert _clock_reads(planted) == ["planted.py:3 (datetime.now)"]

    def test_the_emit_path_is_where_the_test_thinks_it_is(self):
        """Guards the paths above: an empty scan must mean clean, not missing."""
        modules = _emit_path_modules()
        assert len(modules) > 10
        assert PACKAGE / "prompt_builder.py" in modules


class TestOutputDoesNotDependOnTheClock:
    def test_two_builds_produce_the_same_bytes(self):
        """The base case. Anything that fails here fails everywhere else too."""
        assert _build("claude") == _build("claude")

    @pytest.mark.skipif(not hasattr(time, "tzset"), reason="TZ switching needs a POSIX tzset")
    def test_a_date_boundary_does_not_change_the_output(self):
        """Measured rather than reasoned about, because reasoning is what
        missed it the first time.

        The two zones are 25 hours apart, so they are on different calendar
        dates *simultaneously*. Before PRO-116 this produced two different
        CLAUDE.md files on one machine in one second.
        """
        east_date, east = _build_under(_EAST, "claude")
        west_date, west = _build_under(_WEST, "claude")

        assert east_date != west_date, "the two zones must straddle a date, or this proves nothing"
        assert east == west
