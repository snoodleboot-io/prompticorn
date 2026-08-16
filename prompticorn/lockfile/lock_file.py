"""The lock model: what a build resolved to (PRO-110).

``.prompticorn/prompticorn.lock`` is generated, committed, and read far more
often than it is written. Everything about its shape is chosen so that a re-lock
over unchanged inputs produces **zero diff** — churn in a committed generated
file is a review tax, and a file that always shows up dirty is a file people stop
reading.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Any

from prompticorn.lockfile.locked_artifact import LockedArtifact
from prompticorn.lockfile.locked_output import LockedOutput
from prompticorn.lockfile.locked_unit import LockedUnit

LOCK_VERSION_KEY = "lock_version"
PROMPTICORN_VERSION_KEY = "prompticorn_version"
MANIFEST_DIGEST_KEY = "manifest_digest"
RESOLVED_AT_KEY = "resolved_at"
ARTIFACTS_KEY = "artifacts"
UNITS_KEY = "units"
OUTPUTS_KEY = "outputs"

LOCK_SCHEMA_VERSION = "1.0"
SUPPORTED_LOCK_VERSIONS = (LOCK_SCHEMA_VERSION,)

# ISO-8601, UTC, second precision. Pinned to one spelling because the field is
# compared byte-for-byte on re-lock: an offset like `+00:00` and a `Z` denote the
# same instant but are different bytes, which would defeat the whole design.
RESOLVED_AT_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


@dataclass(frozen=True)
class LockFile:
    """A complete resolution result.

    Attributes:
        prompticorn_version: The version that produced this lock, so a later
            reader can tell whether a difference is its own doing.
        resolved_at: When resolution last actually happened, ISO-8601 UTC.
            **Not** when the file was last written — see
            :meth:`equals_ignoring_resolved_at`.
        artifacts: Resolved artifacts, sorted by identity.
        units: Resolved units, sorted by unit id.
        outputs: Generated files, sorted by path.
        lock_version: Schema version of the lock format itself.
        manifest_digest: Canonical digest of ``.prompticorn.yaml`` at resolution
            time (PRO-111). Without it "the manifest changed" is undetectable:
            comparing declared *artifacts* would miss edits to ``spec``, which
            drive generation while touching no artifact. Optional so a lock
            written by hand, or before this field existed, still reads.
    """

    prompticorn_version: str
    resolved_at: str
    artifacts: tuple[LockedArtifact, ...] = ()
    units: tuple[LockedUnit, ...] = ()
    outputs: tuple[LockedOutput, ...] = ()
    lock_version: str = LOCK_SCHEMA_VERSION
    manifest_digest: str | None = None

    def __post_init__(self) -> None:
        """Reject a timestamp that is not in the one canonical spelling.

        A tolerated variant would round-trip fine and then silently break
        re-lock stability, which is the failure this class exists to prevent.
        """
        if not RESOLVED_AT_PATTERN.match(self.resolved_at):
            raise ValueError(
                f"resolved_at {self.resolved_at!r} must be ISO-8601 UTC to the "
                "second, e.g. 2026-08-09T02:40:00Z"
            )

    def canonical(self) -> LockFile:
        """The same lock with every sequence in its defined order.

        Sorting happens here rather than in the writer so that two locks can be
        compared as *values*. A caller that builds entries in discovery order
        and one that builds them in reverse must produce equal objects, not
        merely equal files.
        """
        return replace(
            self,
            artifacts=tuple(sorted(self.artifacts, key=lambda a: a.sort_key)),
            units=tuple(sorted(self.units, key=lambda u: u.sort_key)),
            outputs=tuple(sorted(self.outputs, key=lambda o: o.sort_key)),
        )

    def equals_ignoring_resolved_at(self, other: LockFile) -> bool:
        """Whether two locks record the same resolution.

        The comparison that makes ``resolved_at`` preservation possible. It has
        to exclude the very field it guards: comparing the whole object would
        always differ, and the timestamp would advance on every write — dirtying
        the tree each time anyone ran a build.
        """
        placeholder = replace(other.canonical(), resolved_at=self.resolved_at)
        return self.canonical() == placeholder

    def to_mapping(self) -> dict[str, Any]:
        """Plain, JSON-shaped data for the writer.

        Sequences are emitted in canonical order and every nested mapping is
        freshly built, so the serialiser never sees a shared object and can
        never emit an anchor.
        """
        canonical = self.canonical()
        mapping: dict[str, Any] = {
            LOCK_VERSION_KEY: canonical.lock_version,
            PROMPTICORN_VERSION_KEY: canonical.prompticorn_version,
            RESOLVED_AT_KEY: canonical.resolved_at,
            ARTIFACTS_KEY: [artifact.to_mapping() for artifact in canonical.artifacts],
            UNITS_KEY: [unit.to_mapping() for unit in canonical.units],
            OUTPUTS_KEY: [output.to_mapping() for output in canonical.outputs],
        }
        # Omitted rather than written as null, on the same reasoning as an
        # artifact's absent source: a key that is always present but usually
        # empty is noise in every review of the file.
        if canonical.manifest_digest is not None:
            mapping[MANIFEST_DIGEST_KEY] = canonical.manifest_digest
        return mapping
