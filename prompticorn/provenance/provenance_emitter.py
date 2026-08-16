"""Attaching provenance to the files a build wrote (PRO-112).

This runs as a **pass over finished output**, not as a hook inside each writer.
Fifteen layouts write their own files and several builders write more besides, so
a hook would have to be installed in every one of them and would be missing from
the next one somebody adds. A pass over the set of paths the build emitted is
installed once and cannot be forgotten.

Position matters. The pass must run **after every other rewrite** — in
particular after ``{{PRIMARY_AGENTS_LIST}}`` resolution, which edits files in
place once they are already written. A digest taken before that edit describes
bytes that no longer exist on disk, which is worse than no digest at all: it
fails verification for a reason invisible to whoever reads the file.

Attribution comes from the caller because only the caller knows it. By the time
a path reaches this module it is a string like ``.claude/agents/code.md``; which
authored unit produced it is knowable at the write site and nowhere else.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from prompticorn.provenance.output_format import OutputFormat
from prompticorn.provenance.provenance_header import ProvenanceHeader
from prompticorn.provenance.provenance_record import ProvenanceRecord
from prompticorn.provenance.provenance_sidecar import SIDECAR_FILENAME, ProvenanceSidecar

SIDECAR_DIRECTORY = ".prompticorn"

# Outputs assembled from many units (a root AGENTS.md, Roo's .roomodes) have no
# single source unit. Naming them ``generated/...`` says so, rather than picking
# one of their inputs and implying the file came only from that.
GENERATED_UNIT_PREFIX = "generated"

_WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class ProvenanceEmitter:
    """Writes inline headers and the sidecar for one build's outputs.

    Attributes:
        layer: Which content layer supplied the units — "which layer won".
        version: The artifact version the units came from.
    """

    layer: str
    version: str

    def emit(self, output: Path, attribution: Mapping[str, str]) -> list[str]:
        """Attach provenance to every attributed output under ``output``.

        Args:
            output: The build's root directory. Paths are relative to it.
            attribution: Output path (POSIX, relative to ``output``) to the unit
                id it was generated from.

        Returns:
            The paths this pass itself wrote, for the caller to report.
        """
        entries: dict[str, ProvenanceRecord] = {}
        for relative in sorted(attribution):
            record = self._attach(output / relative, relative, attribution[relative])
            if record is not None:
                entries[relative] = record

        sidecar_relative = f"{SIDECAR_DIRECTORY}/{SIDECAR_FILENAME}"
        ProvenanceSidecar(entries=entries).write(output / sidecar_relative)
        return [sidecar_relative]

    def _attach(self, path: Path, relative: str, unit: str) -> ProvenanceRecord | None:
        """Header one file and return its record, or None if it has no provenance.

        Returns None for anything unreadable rather than raising. A build that
        already succeeded should not be failed retroactively by the bookkeeping
        pass that describes it; a file missing from the sidecar is a visible
        omission, an aborted build is a regression.
        """
        if not path.is_file():
            return None
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return None

        output_format = OutputFormat.of(relative)
        # Stripping first makes the pass idempotent: re-running over an already
        # headed file digests the same body and rewrites the same bytes, so a
        # rebuild produces no diff.
        body = ProvenanceHeader.strip(text, output_format)
        record = ProvenanceRecord(
            unit=_header_safe(unit),
            layer=self.layer,
            version=self.version,
            digest=ProvenanceHeader.body_digest(body, output_format),
        )

        headed = ProvenanceHeader.render(body, record, output_format)
        if headed != text:
            path.write_text(headed, encoding="utf-8")
        return record


def _header_safe(unit: str) -> str:
    """A unit id that survives the header's whitespace-separated encoding.

    ``ProvenanceRecord.to_header_body`` neither quotes nor escapes values, so a
    unit containing whitespace would render a header that parses back as
    something else. Every id the builders produce is already safe; collapsing
    here means an unusual name degrades to a slightly odd id rather than to a
    silently unparseable file.
    """
    return _WHITESPACE_RE.sub("_", unit.strip())
