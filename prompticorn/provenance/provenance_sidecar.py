"""`.prompticorn/provenance.json` — provenance for every output (PRO-112).

The **general** mechanism, not a fallback. Inline headers are a convenience for
formats that can carry a comment; this covers all of them, including the JSON
outputs that cannot. An audit trail that existed for markdown but not for JSON
would have its hole in exactly the place a reader is least able to spot by eye.

JSON rather than YAML because this file is machine-read and never hand-edited,
and because `json.dumps` with sorted keys is byte-stable without the anchor and
flow-style hazards the lock writer had to defend against.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from prompticorn.provenance.provenance_record import ProvenanceRecord
from prompticorn.text_writer import write_text

SIDECAR_FILENAME = "provenance.json"

_INDENT = 2


@dataclass(frozen=True)
class ProvenanceSidecar:
    """Provenance for every generated file, keyed by output path.

    Attributes:
        entries: Output path (POSIX, relative to the project root) to its record.
    """

    entries: dict[str, ProvenanceRecord]

    def render(self) -> str:
        """The canonical text. Sorted by path, so a rebuild produces no diff.

        Same reasoning as the lock: this file is committed alongside the outputs
        it describes, and one that reorders itself on every run is one reviewers
        stop reading.
        """
        payload = {path: self.entries[path].to_mapping() for path in sorted(self.entries)}
        return json.dumps(payload, indent=_INDENT, sort_keys=True) + "\n"

    def write(self, path: Path) -> bool:
        """Write the sidecar. Returns whether the contents changed."""
        rendered = self.render()
        if path.exists() and path.read_text(encoding="utf-8") == rendered:
            return False
        path.parent.mkdir(parents=True, exist_ok=True)
        write_text(path, rendered)
        return True

    @classmethod
    def parse(cls, raw_text: str) -> ProvenanceSidecar:
        """Read a sidecar back.

        Raises:
            ValueError: If it is not a mapping of path to record.
        """
        data = json.loads(raw_text)
        if not isinstance(data, dict):
            raise ValueError(f"provenance sidecar must be a mapping, found {type(data).__name__}")
        return cls(
            entries={path: ProvenanceRecord.from_mapping(record) for path, record in data.items()}
        )

    @classmethod
    def read(cls, path: Path) -> ProvenanceSidecar:
        """Read a sidecar from disk, or an empty one when absent."""
        if not path.is_file():
            return cls(entries={})
        return cls.parse(path.read_text(encoding="utf-8"))

    def record_for(self, output_path: str) -> ProvenanceRecord | None:
        """The record for one output, or None if it is not covered."""
        return self.entries.get(output_path)

    @property
    def paths(self) -> tuple[str, ...]:
        """Every covered output path, sorted."""
        return tuple(sorted(self.entries))
