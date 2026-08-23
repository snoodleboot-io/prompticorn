"""Shared golden-corpus machinery: the matrix, the manifest, and the diff (PRO-102).

Lives outside ``tests/unit`` so the regeneration entry point and the assertion test
share one definition of the corpus. If these two ever drift, the baseline stops
being a baseline.

The corpus snapshots every builder's generated output across
tool x variant x repository-type x language, as ``{relative_path: sha256}``.
Hashes rather than file bodies: the full matrix is ~136 builds of ~100 files each,
which is not something to commit. The trade-off is that a mismatch reports *which*
paths changed, not the line-level content — regenerate and inspect the working tree
for that.

Regenerate with::

    uv run python -m tests.golden_corpus
"""

from __future__ import annotations

import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Any

from prompticorn.prompt_builder import get_prompt_builder
from prompticorn.provenance.output_format import OutputFormat
from prompticorn.provenance.provenance_emitter import SIDECAR_DIRECTORY
from prompticorn.provenance.provenance_header import ProvenanceHeader
from prompticorn.provenance.provenance_sidecar import SIDECAR_FILENAME
from prompticorn.tools import supported_tool_ids

FIXTURE = Path(__file__).parent / "golden" / "manifest.json"

_SIDECAR_PATH = f"{SIDECAR_DIRECTORY}/{SIDECAR_FILENAME}"

# The two sidecar fields that move without the build having changed.
#
# ``version`` is stamped into ``__about__.py`` by a release build, so a checkout
# where that has happened would otherwise disagree with a clean one.
#
# ``digest`` was masked because it restated a date the corpus normalized away at
# the file level, so the instability just moved down a level and CI went red at
# a day boundary. PRO-116 removed the last build-time timestamp from emitted
# output, so that reason is gone — the mask stays only because a sidecar digest
# is a restatement of content the corpus already hashes per file, and nothing is
# lost by dropping it. ``unit`` and ``layer`` are attribution that exists nowhere
# else in the corpus, and those stay pinned.
_SIDECAR_MASKS: tuple[tuple[re.Pattern[bytes], bytes], ...] = (
    (re.compile(rb'"version": "[^"]*"'), b'"version": "VERSION"'),
    (re.compile(rb'"digest": "[^"]*"'), b'"digest": "DIGEST"'),
)

VARIANTS = ("minimal", "verbose")

# The configuration matrix. Deliberately representative rather than exhaustive:
# enough to cover the layout and convention branches without a corpus nobody reads.
#
# `python-single` is byte-for-byte the config the pre-PRO-102 baseline used, so the
# widened corpus is a strict superset of what it replaced.
CONFIGS: dict[str, dict[str, Any]] = {
    # Single language, no repository block — the original baseline.
    "python-single": {
        "spec": {"language": "python"},
        "active_personas": ["software_engineer"],
    },
    # A different language family: exercises the JS/TS runtime split and the
    # typescript convention branch.
    "typescript-single": {
        "repository": {"type": "single-language"},
        "spec": {"language": "typescript", "runtime": "node-22"},
        "active_personas": ["software_engineer"],
    },
    # A third convention branch, and the language whose filename mismatch caused
    # PRO-93 (go vs golang).
    "go-single": {
        "repository": {"type": "single-language"},
        "spec": {"language": "go", "runtime": "1.24"},
        "active_personas": ["software_engineer"],
    },
    # Monorepo: a list spec with per-folder languages, plus a wider persona set so
    # agent filtering is exercised too. This is the branch the old corpus never hit.
    "monorepo": {
        "repository": {"type": "multi-language-monorepo"},
        "spec": [
            {
                "folder": "backend/api",
                "type": "backend",
                "subtype": "api",
                "language": "python",
                "runtime": "3.14",
            },
            {
                "folder": "frontend/ui",
                "type": "frontend",
                "subtype": "ui",
                "language": "typescript",
                "runtime": "node-22",
            },
        ],
        "active_personas": ["software_engineer", "qa_tester", "devops_engineer"],
    },
}


def corpus_keys() -> list[str]:
    """Every ``config::tool::variant`` key, sorted for a stable corpus."""
    return sorted(
        f"{config_id}::{tool}::{variant}"
        for config_id in CONFIGS
        for tool in supported_tool_ids()
        for variant in VARIANTS
    )


def split_key(key: str) -> tuple[str, str, str]:
    config_id, tool, variant = key.split("::")
    return config_id, tool, variant


def normalize(raw: bytes, relative: str) -> bytes:
    """Strip out everything that is not the file's content.

    One thing varies without the output having changed: the provenance header
    (PRO-112), which every non-JSON output carries. It embeds the artifact
    version and a digest of the body it sits on, so a corpus that hashed it
    would re-baseline on a version bump and would otherwise merely restate a
    hash it already has.

    Removing it via ``ProvenanceHeader.strip`` rather than a local regex keeps
    one definition of what a header is. What provenance the corpus still pins it
    pins through the sidecar, which is itself an output: the set of covered
    paths, and each one's ``unit`` and ``layer``. That is the attribution the
    corpus adds; the digests are masked, for the reason given on
    ``_SIDECAR_MASKS``.
    """
    if relative == _SIDECAR_PATH:
        for pattern, replacement in _SIDECAR_MASKS:
            raw = pattern.sub(replacement, raw)
        return raw
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw
    return ProvenanceHeader.strip(text, OutputFormat.of(relative)).encode("utf-8")


def digest(path: Path, relative: str) -> str:
    """sha256 of a file's content, with the varying parts normalized out.

    Dates used to be masked here, because CLAUDE.md stamped ``datetime.now()``
    into a "Last Updated" line. PRO-116 removed that — no emitted file carries a
    build-time timestamp any more — and the mask went with it. Removing it is
    what makes the corpus able to *notice* one being reintroduced, which a mask
    would hide by construction.
    """
    return hashlib.sha256(normalize(path.read_bytes(), relative)).hexdigest()


def manifest(root: Path) -> dict[str, str]:
    """``{relative_posix_path: digest}`` for every file under ``root``.

    Enumeration is sorted so the corpus does not depend on filesystem ordering.
    """
    return {
        relative: digest(path, relative)
        for path, relative in (
            (path, path.relative_to(root).as_posix())
            for path in sorted(root.rglob("*"))
            if path.is_file()
        )
    }


def build_manifest(key: str) -> dict[str, str]:
    """Build one matrix cell in a temp directory and return its manifest."""
    config_id, tool, variant = split_key(key)
    config = {**CONFIGS[config_id], "variant": variant}
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        get_prompt_builder(tool).build(root, config, dry_run=False)
        return manifest(root)


def describe_difference(expected: dict[str, str], actual: dict[str, str]) -> str:
    """A readable account of how two manifests differ.

    The point of failure output is to say what moved. Listing paths by category
    beats dumping two hash tables and leaving the reader to diff them.
    """
    added = sorted(actual.keys() - expected.keys())
    removed = sorted(expected.keys() - actual.keys())
    changed = sorted(p for p in expected.keys() & actual.keys() if expected[p] != actual[p])

    lines: list[str] = []
    if added:
        lines.append(f"  {len(added)} added:")
        lines += [f"    + {p}" for p in added]
    if removed:
        lines.append(f"  {len(removed)} removed:")
        lines += [f"    - {p}" for p in removed]
    if changed:
        lines.append(f"  {len(changed)} changed (content differs):")
        lines += [f"    ~ {p}" for p in changed]
    if not lines:
        lines.append("  (manifests differ but no path-level difference — check ordering)")
    lines.append("")
    lines.append("  To accept these changes, regenerate and review the fixture diff:")
    lines.append("    uv run python -m tests.golden_corpus")
    return "\n".join(lines)


def regenerate() -> tuple[int, int]:
    """Rebuild the whole corpus and write the fixture. Returns (cells, files)."""
    corpus = {key: build_manifest(key) for key in corpus_keys()}
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(json.dumps(corpus, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return len(corpus), sum(len(m) for m in corpus.values())


def load() -> dict[str, dict[str, str]]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


if __name__ == "__main__":  # pragma: no cover - operator entry point
    cells, files = regenerate()
    print(f"Regenerated {FIXTURE.relative_to(Path(__file__).parent.parent)}")
    print(f"  {cells} matrix cells, {files} files hashed")
    print("Review with: git diff -- tests/golden/manifest.json")
