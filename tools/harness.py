#!/usr/bin/env python3
"""Development harness: provision the environment, then verify against it (PRO-143).

Everything here is deliberately runnable before the project is installed, so it
imports nothing from ``prompticorn`` at module scope — ``up`` has to work on a
checkout that has never been synced. The two commands that do need the package
(``regen``, ``verify``) import it lazily, after ``up`` has had a chance to run.

Usage:
    uv run python tools/harness.py up
    uv run python tools/harness.py check [--fast] [--lane LANE ...]
    uv run python tools/harness.py verify
    uv run python tools/harness.py regen
    uv run python tools/harness.py watch [--interval SECONDS]
    uv run python tools/harness.py down
"""

from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from collections.abc import Iterable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / ".harness"
WATCH_PID = STATE_DIR / "watch.pid"

# The tracked .claude/ tree was NOT built from .prompticorn.yaml as written.
# It was built verbose, with persona filtering off, and nothing recorded that —
# so the first attempt to regenerate it flipped every emitted skill to the
# minimal variant and produced a huge wrong diff. Pinning it here is the whole
# point: the regeneration contract belongs in code, not in somebody's memory.
GENERATED_TREE_CONFIG: dict[str, object] = {
    "variant": "verbose",
    # None disables persona filtering entirely (an empty list would filter down
    # to the universal agents only, which is a different and wrong thing).
    "active_personas": None,
}

# Paths the generated-output build owns. Drift is measured over exactly these.
GENERATED_PATHS = (".claude", "CLAUDE.md")


@dataclass(frozen=True)
class Service:
    """One thing the environment needs, and how to prove it is there."""

    name: str
    purpose: str
    start: Sequence[str] | None  # None when the service can only be verified
    health: Sequence[str]
    stop: str


@dataclass
class LaneResult:
    name: str
    ok: bool
    seconds: float
    output: str


@dataclass
class Lane:
    """A verification lane, mirroring one CI job."""

    name: str
    command: Sequence[str]
    fast: bool = False
    env: dict[str, str] = field(default_factory=dict)
    # Exclusive lanes measure wall-clock and must not share the machine. They run
    # alone, after the concurrent batch, so their result reflects the code rather
    # than how busy the box was.
    exclusive: bool = False


# Lanes mirror .github/workflows/ci-cd.yml so a green `check` means a green CI.
# CI excludes tests/ from ruff; matching that here keeps the two from disagreeing.
#
# `fast` marks the lanes worth running on every edit. The split is measured, not
# guessed: lint 0.2s, format 0.2s, security 1.9s, types 14.3s — against unit-fast
# 320s and integration 667s. Profiling the unit suite found no hot spot to carve
# out (slowest single test 15.9s; the top 20 are ~110s of a 285s run), so the
# cost is spread across hundreds of builder invocations and cannot be trimmed
# into a fast lane. That is why `--fast` is the static tier only.
LANES: tuple[Lane, ...] = (
    Lane("lint", ("uv", "run", "ruff", "check", "--exclude=tests/", "."), fast=True),
    Lane("format", ("uv", "run", "ruff", "format", "--check", "--exclude=tests/", "."), fast=True),
    Lane("types", ("uv", "run", "pyright"), fast=True),
    Lane("security", ("uv", "run", "pytest", "tests/security", "-q"), fast=True),
    Lane("unit", ("uv", "run", "pytest", "tests/unit", "-q"), fast=False),
    Lane("integration", ("uv", "run", "pytest", "tests/integration", "-q"), fast=False),
    Lane(
        "slow",
        ("uv", "run", "pytest", "tests/slow", "-q", "--ignore=tests/slow/test_build_benchmarks.py"),
        fast=False,
    ),
    # Asserts a total build time under a fixed ceiling. Alone it takes ~51s; run
    # beside six saturating lanes it blew the 90s budget and failed for reasons
    # that had nothing to do with the diff. CI does not hit this — each lane is
    # its own runner there.
    Lane(
        "benchmarks",
        ("uv", "run", "pytest", "tests/slow/test_build_benchmarks.py", "-q"),
        fast=False,
        exclusive=True,
    ),
    # Not in either default set: a trimmed unit run for `watch`, reachable with
    # --lane when you want it deliberately.
    Lane(
        "unit-watch",
        (
            "uv",
            "run",
            "pytest",
            "tests/unit",
            "-q",
            "-m",
            "not slow",
            "--ignore=tests/unit/test_tool_output_golden.py",
        ),
        fast=False,
    ),
)

SERVICES: tuple[Service, ...] = (
    Service(
        name="uv",
        purpose="package manager and task runner for every other command",
        start=None,  # a missing uv is a blocker, not something we can install for you
        health=("uv", "--version"),
        stop="n/a (no process)",
    ),
    Service(
        name="python",
        purpose="interpreter the project runs on",
        start=None,
        health=("uv", "run", "python", "--version"),
        stop="n/a (no process)",
    ),
    Service(
        name="dev-dependencies",
        purpose="pytest, ruff, pyright and friends from the dev dependency group",
        start=("uv", "sync", "--dev"),
        health=("uv", "run", "python", "-c", "import pytest, yaml, jinja2, pydantic"),
        stop="rm -rf .venv",
    ),
    Service(
        name="package",
        purpose="prompticorn itself, importable from the synced environment",
        start=("uv", "sync", "--dev"),
        health=("uv", "run", "python", "-c", "import prompticorn; print(prompticorn.__name__)"),
        stop="rm -rf .venv",
    ),
    Service(
        name="pytest",
        purpose="test runner; collection is the health check, not mere presence",
        start=None,
        health=("uv", "run", "pytest", "--collect-only", "-q", "tests/unit"),
        stop="n/a (no process)",
    ),
    Service(
        name="ruff",
        purpose="linter and formatter",
        start=None,
        health=("uv", "run", "ruff", "--version"),
        stop="n/a (no process)",
    ),
    Service(
        name="pyright",
        purpose="type checker",
        start=None,
        health=("uv", "run", "pyright", "--version"),
        stop="n/a (no process)",
    ),
)


def _run(command: Sequence[str], *, env: dict[str, str] | None = None) -> tuple[int, str]:
    """Run a command from the repo root, returning ``(returncode, merged output)``."""
    merged = {**os.environ, **(env or {})}
    # uv warns and ignores a VIRTUAL_ENV pointing somewhere else, which is noise
    # in a worktree; drop it so the project environment is used without comment.
    merged.pop("VIRTUAL_ENV", None)
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=merged,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        return 127, f"{command[0]}: not found ({exc})"
    return completed.returncode, (completed.stdout or "") + (completed.stderr or "")


def _tail(text: str, lines: int = 15) -> str:
    kept = [line for line in text.strip().splitlines() if line.strip()]
    return "\n".join(f"      {line}" for line in kept[-lines:])


# --------------------------------------------------------------------------- up


def command_up(_: argparse.Namespace) -> int:
    """Provision and health-check every service, then print the manifest.

    Assumes nothing is already in place: each service is checked, and started if
    it declares a way to start. A service that cannot be brought up is reported
    as a blocker and fails the gate rather than being quietly skipped.
    """
    STATE_DIR.mkdir(exist_ok=True)
    rows: list[tuple[str, str, str]] = []
    blockers: list[tuple[str, str]] = []

    for service in SERVICES:
        code, output = _run(service.health)
        action = "already healthy"

        if code != 0 and service.start is not None:
            print(f"  starting {service.name} ...", flush=True)
            start_code, start_output = _run(service.start)
            if start_code != 0:
                blockers.append((service.name, start_output))
                rows.append((service.name, "FAILED TO START", service.stop))
                continue
            action = " ".join(service.start)
            code, output = _run(service.health)

        if code != 0:
            blockers.append((service.name, output))
            rows.append((service.name, "UNHEALTHY", service.stop))
            continue

        first = next((ln for ln in output.strip().splitlines() if ln.strip()), "ok")
        rows.append((service.name, f"{action} — {first.strip()[:60]}", service.stop))

    width = max(len(name) for name, _, _ in rows)
    print("\nEnvironment manifest")
    print(f"  {'SERVICE'.ljust(width)}  STATUS / HEALTH CHECK")
    for name, status, _ in rows:
        print(f"  {name.ljust(width)}  {status}")
    print("\n  Stop with:")
    for name, _, stop in rows:
        if stop.startswith("n/a"):
            continue
        print(f"    {name}: {stop}")

    if blockers:
        print("\nBLOCKED — these could not be brought up:")
        for name, output in blockers:
            print(f"  {name}:")
            print(_tail(output))
        print("\nNo verification lane should run against this environment.")
        return 1

    print("\nEnvironment ready. Next: uv run python tools/harness.py check --fast")
    return 0


# ------------------------------------------------------------------------ check


def _select_lanes(namespace: argparse.Namespace) -> list[Lane]:
    by_name = {lane.name: lane for lane in LANES}
    if namespace.lane:
        unknown = sorted(set(namespace.lane) - by_name.keys())
        if unknown:
            raise SystemExit(f"unknown lane(s): {', '.join(unknown)}")
        return [by_name[name] for name in namespace.lane]
    if namespace.fast:
        return [lane for lane in LANES if lane.fast]
    # The full sweep runs the real unit lane, not the trimmed watch variant.
    return [lane for lane in LANES if lane.name != "unit-watch"]


def _run_lanes(lanes: Iterable[Lane]) -> list[LaneResult]:
    lanes = list(lanes)

    def execute(lane: Lane) -> LaneResult:
        started = time.monotonic()
        code, output = _run(lane.command, env=lane.env)
        return LaneResult(lane.name, code == 0, time.monotonic() - started, output)

    shared = [lane for lane in lanes if not lane.exclusive]
    alone = [lane for lane in lanes if lane.exclusive]

    results: list[LaneResult] = []
    # Shared lanes are independent processes over a read-only checkout, so they
    # run concurrently; wall-clock is the slowest lane rather than their sum.
    if shared:
        with ThreadPoolExecutor(max_workers=len(shared)) as pool:
            results.extend(pool.map(execute, shared))
    # Exclusive lanes wait for a quiet machine, then run one at a time.
    for lane in alone:
        results.append(execute(lane))
    return results


def _report(results: Sequence[LaneResult]) -> int:
    width = max(len(result.name) for result in results)
    print("\nLane results")
    for result in sorted(results, key=lambda r: (r.ok, r.name)):
        mark = "PASS" if result.ok else "FAIL"
        print(f"  {mark}  {result.name.ljust(width)}  {result.seconds:6.1f}s")

    failures = [result for result in results if not result.ok]
    for failure in failures:
        print(f"\n--- {failure.name} ---")
        print(_tail(failure.output, lines=25))
    return 1 if failures else 0


def command_check(namespace: argparse.Namespace) -> int:
    lanes = _select_lanes(namespace)
    shared = [lane.name for lane in lanes if not lane.exclusive]
    alone = [lane.name for lane in lanes if lane.exclusive]
    if shared:
        print(f"Running {len(shared)} lane(s) concurrently: {', '.join(shared)}")
    if alone:
        print(f"Then {len(alone)} exclusive lane(s), alone: {', '.join(alone)}")
    return _report(_run_lanes(lanes))


# --------------------------------------------------------------- regen / verify


def _build_generated_tree(destination: Path) -> None:
    """Build the tracked generated tree into ``destination`` using the pinned config."""
    import yaml  # local: the package is only importable once `up` has synced

    from prompticorn.prompt_builder import get_prompt_builder

    config = yaml.safe_load((ROOT / ".prompticorn.yaml").read_text(encoding="utf-8"))
    config.update(GENERATED_TREE_CONFIG)
    get_prompt_builder("claude").build(destination, config, dry_run=False)


def _relative_files(root: Path) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for target in GENERATED_PATHS:
        path = root / target
        if path.is_file():
            files[target] = path.read_bytes()
        elif path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file():
                    files[child.relative_to(root).as_posix()] = child.read_bytes()
    return files


def command_verify(_: argparse.Namespace) -> int:
    """Fail if the tracked generated tree disagrees with what source produces.

    This is the check whose absence let `qa-tester` and four testing subagents sit
    in source, unemitted and unnoticed, for as long as they did.
    """
    with tempfile.TemporaryDirectory() as tmp:
        fresh_root = Path(tmp)
        _build_generated_tree(fresh_root)
        fresh = _relative_files(fresh_root)

    tracked = _relative_files(ROOT)

    # Compared verbatim. CLAUDE.md used to stamp the build date, so its
    # "Last Updated" line had to be dropped before comparing or the tree read as
    # dirty forever; PRO-116 removed the stamp, and the exemption went with it.
    # Keeping it would have left this check blind to the stamp coming back.
    missing = sorted(set(fresh) - set(tracked))
    extra = sorted(set(tracked) - set(fresh))
    changed = sorted(name for name in set(fresh) & set(tracked) if fresh[name] != tracked[name])

    if not (missing or extra or changed):
        print(f"Generated output is in sync ({len(tracked)} files).")
        return 0

    print("Generated output has drifted from source:")
    for label, names in (
        ("never emitted", missing),
        ("stale, not in source", extra),
        ("content differs", changed),
    ):
        if names:
            print(f"\n  {len(names)} {label}:")
            for name in names[:25]:
                print(f"    {name}")
            if len(names) > 25:
                print(f"    ... and {len(names) - 25} more")
    print("\nRegenerate with: uv run python tools/harness.py regen")
    return 1


def command_regen(_: argparse.Namespace) -> int:
    """Rebuild the generated tree and the golden corpus, in that order."""
    print("Rebuilding generated tree ...")
    _build_generated_tree(ROOT)

    print("Regenerating golden corpus ...")
    sys.path.insert(0, str(ROOT))
    from tests.golden_corpus import regenerate

    cells, files = regenerate()
    print(f"  {cells} matrix cells, {files} files hashed")
    print("\nReview both diffs before committing:")
    print("  git diff -- .claude CLAUDE.md")
    print("  git diff -- tests/golden/manifest.json")
    return 0


# ------------------------------------------------------------------ watch / down


def _snapshot(paths: Iterable[Path]) -> dict[Path, float]:
    seen: dict[Path, float] = {}
    for base in paths:
        for path in base.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            try:
                seen[path] = path.stat().st_mtime
            except OSError:  # pragma: no cover - file vanished mid-scan
                continue
    return seen


def command_watch(namespace: argparse.Namespace) -> int:
    """Re-run the fast unit lane whenever a source file changes.

    Polls mtimes rather than pulling in a filesystem-notification dependency; at
    a one-second interval the cost is irrelevant next to the test run it guards.
    """
    STATE_DIR.mkdir(exist_ok=True)
    WATCH_PID.write_text(str(os.getpid()), encoding="utf-8")
    watched = [ROOT / "prompticorn", ROOT / "tests"]
    lane = next(lane for lane in LANES if lane.name == "unit-watch")

    print(f"Watching {', '.join(p.name for p in watched)} (Ctrl-C or `harness.py down` to stop)")
    previous = _snapshot(watched)
    try:
        while True:
            time.sleep(namespace.interval)
            current = _snapshot(watched)
            if current == previous:
                continue
            changed = sorted(
                path.relative_to(ROOT).as_posix()
                for path in set(current) ^ set(previous)
                | {p for p in set(current) & set(previous) if current[p] != previous[p]}
            )
            previous = current
            print(f"\n{len(changed)} file(s) changed: {', '.join(changed[:5])}")
            result = _run_lanes([lane])[0]
            print(f"  {'PASS' if result.ok else 'FAIL'} in {result.seconds:.1f}s")
            if not result.ok:
                print(_tail(result.output, lines=20))
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        WATCH_PID.unlink(missing_ok=True)
    return 0


def command_down(_: argparse.Namespace) -> int:
    """Stop anything the harness started. Only the watcher outlives its command."""
    if not WATCH_PID.exists():
        print("Nothing to stop.")
        return 0
    pid = int(WATCH_PID.read_text(encoding="utf-8").strip())
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"Stopped watcher (pid {pid}).")
    except ProcessLookupError:
        print(f"Watcher (pid {pid}) was already gone.")
    WATCH_PID.unlink(missing_ok=True)
    return 0


# ------------------------------------------------------------------------- main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="harness", description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("up", help="provision and health-check the environment").set_defaults(
        handler=command_up
    )

    check = subparsers.add_parser("check", help="run verification lanes concurrently")
    check.add_argument(
        "--fast",
        action="store_true",
        help="static tier only (lint, format, types, security) — seconds, not minutes",
    )
    check.add_argument("--lane", action="append", help="run only this lane (repeatable)")
    check.set_defaults(handler=command_check)

    subparsers.add_parser("verify", help="fail if generated output drifted").set_defaults(
        handler=command_verify
    )
    subparsers.add_parser("regen", help="rebuild generated output and goldens").set_defaults(
        handler=command_regen
    )

    watch = subparsers.add_parser("watch", help="re-run the fast lane on change")
    watch.add_argument("--interval", type=float, default=1.0, help="poll seconds (default 1.0)")
    watch.set_defaults(handler=command_watch)

    subparsers.add_parser("down", help="stop anything the harness started").set_defaults(
        handler=command_down
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    if shutil.which("uv") is None:
        print("uv is not on PATH — install it first: https://docs.astral.sh/uv/", file=sys.stderr)
        return 1
    namespace = build_parser().parse_args(argv)
    return int(namespace.handler(namespace))


if __name__ == "__main__":
    raise SystemExit(main())
