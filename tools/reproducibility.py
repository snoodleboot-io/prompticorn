#!/usr/bin/env python3
"""The cross-platform reproducibility check (PRO-116).

Every reproducibility claim in the artifact-model work rests on one assertion:
a tree locked on one operating system rebuilds to the same bytes on another. A
unit test on Linux proves none of it — path separators, line endings,
filesystem case sensitivity and directory iteration order all differ across the
three platforms, and each one has produced a real non-determinism bug in tools
of this shape.

So this runs in two halves, in two CI jobs:

    uv run python tools/reproducibility.py seed --root repro-project
    uv run python tools/reproducibility.py check --reference repro-project

``seed`` runs on Linux: it creates a scratch project, builds it, and locks it.
The result is uploaded as an artifact. ``check`` runs on Linux, macOS and
Windows: it copies that tree, regenerates it from the lock alone, verifies it,
and then compares every byte against the tree Linux produced.

The comparison is over raw bytes, deliberately. Reading the files back would
translate line endings away and pass on a tree that is CRLF on disk — which is
precisely the failure ``prompticorn.text_writer`` exists to prevent, and the one
this job is here to catch if it ever comes back.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# A small, representative project. Small because the artifact crosses three
# runners; representative because it exercises the branch that emits both a
# directory tree and a root document.
MANIFEST = """\
version: '2.0'
repository:
  type: single-language
spec:
  language: python
variant: verbose
active_personas:
  - software_engineer
ai_tool: claude
"""

CONFIG_DIRECTORY = ".prompticorn"
MANIFEST_FILENAME = ".prompticorn.yaml"


def files_of(root: Path) -> dict[str, bytes]:
    """Every file under ``root``, keyed by POSIX-relative path.

    POSIX keys because the comparison spans platforms: a Windows tree keyed by
    backslash paths would differ from a Linux one in every entry, which would
    look like total failure rather than like the bug it is not.
    """
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def differences(reference: dict[str, bytes], actual: dict[str, bytes]) -> list[str]:
    """A readable account of how two trees differ, empty when they match."""
    missing = sorted(set(reference) - set(actual))
    extra = sorted(set(actual) - set(reference))
    changed = sorted(
        name for name in set(reference) & set(actual) if reference[name] != actual[name]
    )

    report: list[str] = []
    for label, names in (
        ("missing on this platform", missing),
        ("produced only on this platform", extra),
        ("byte-for-byte different", changed),
    ):
        if names:
            report.append(f"{len(names)} {label}:")
            report.extend(f"    {name}" for name in names[:25])
            if len(names) > 25:
                report.append(f"    ... and {len(names) - 25} more")
    for name in changed[:3]:
        report.append(f"\nfirst difference in {name}:")
        report.append(f"    reference: {_excerpt(reference[name], actual[name])}")
        report.append(f"    this run:  {_excerpt(actual[name], reference[name])}")
    return report


def _excerpt(blob: bytes, other: bytes) -> str:
    """The bytes around the first position at which two files diverge.

    Printed as a repr so a stray ``\\r`` is visible — the difference this job is
    most likely to find is one that renders identically.
    """
    position = next(
        (
            index
            for index, (left, right) in enumerate(zip(blob, other, strict=False))
            if left != right
        ),
        min(len(blob), len(other)),
    )
    start = max(0, position - 30)
    return repr(blob[start : position + 30])


def _prompticorn(*arguments: str, cwd: Path) -> int:
    """Run the installed CLI in ``cwd`` and echo what it said.

    The encoding is named on both sides. The CLI writes UTF-8 (see
    ``prompticorn.console``), so decoding with ``text=True`` would use the
    parent's locale — cp1252 on a Windows runner — and mangle or reject the
    tick marks it is quoting back.
    """
    completed = subprocess.run(
        [sys.executable, "-c", "from prompticorn.cli import cli; cli()", *arguments],
        cwd=cwd,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    return completed.returncode


def command_seed(namespace: argparse.Namespace) -> int:
    """Create, build and lock the reference project."""
    root = Path(namespace.root).resolve()
    if root.exists():
        shutil.rmtree(root)
    (root / CONFIG_DIRECTORY).mkdir(parents=True)
    (root / CONFIG_DIRECTORY / MANIFEST_FILENAME).write_text(
        MANIFEST, encoding="utf-8", newline="\n"
    )

    for arguments in (("build",), ("lock",), ("verify",)):
        code = _prompticorn(*arguments, cwd=root)
        if code != 0:
            print(f"seed failed: `prompticorn {' '.join(arguments)}` exited {code}")
            return code

    print(f"Seeded {root} with {len(files_of(root))} files.")
    return 0


def command_check(namespace: argparse.Namespace) -> int:
    """Regenerate a copy of the reference tree and compare it byte for byte."""
    reference_root = Path(namespace.reference).resolve()
    if not reference_root.is_dir():
        print(f"no reference tree at {reference_root}")
        return 1

    reference = files_of(reference_root)
    if not reference:
        print(f"the reference tree at {reference_root} is empty — nothing was compared")
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "work"
        shutil.copytree(reference_root, work)

        code = _prompticorn("regenerate", cwd=work)
        if code != 0:
            print(f"`prompticorn regenerate` exited {code} on {sys.platform}")
            return code

        report = differences(reference, files_of(work))

    if report:
        print(f"Regenerated tree differs from the reference on {sys.platform}:\n")
        print("\n".join(report))
        return 1

    print(f"Reproduced all {len(reference)} files byte-for-byte on {sys.platform}.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    seed = commands.add_parser("seed", help="create, build and lock the reference project")
    seed.add_argument("--root", required=True, help="directory to create the project in")
    seed.set_defaults(handler=command_seed)

    check = commands.add_parser("check", help="regenerate a copy and compare it byte for byte")
    check.add_argument("--reference", required=True, help="the seeded project to reproduce")
    check.set_defaults(handler=command_check)

    return parser


def main(argv: list[str] | None = None) -> int:
    # This script re-prints the CLI's output, so it needs the same treatment the
    # CLI gives itself: on a Windows runner its own stdout is a pipe, and a
    # quoted tick mark would abort the check rather than fail it.
    from prompticorn.console import configure_output_streams

    configure_output_streams()

    namespace = build_parser().parse_args(argv)
    return namespace.handler(namespace)


if __name__ == "__main__":
    raise SystemExit(main())
