"""The lock model itself (PRO-110).

Canonical ordering and the `resolved_at`-blind comparison live on the model
rather than in the writer, so two locks can be compared as *values* — a caller
that assembled entries in discovery order and one that assembled them backwards
must produce equal objects, not merely equal files.
"""

import pytest

from prompticorn.artifact import ArtifactId, PinnedArtifact
from prompticorn.content import UnitId
from prompticorn.lockfile import (
    LOCK_SCHEMA_VERSION,
    LockedArtifact,
    LockedOutput,
    LockedUnit,
    LockFile,
)

DIGEST_A = "a" * 64
DIGEST_B = "b" * 64
STAMP = "2026-08-09T02:40:00Z"


def test_canonical_sorts_every_sequence() -> None:
    lock = LockFile(
        "0.5.0",
        STAMP,
        artifacts=(
            LockedArtifact(PinnedArtifact(ArtifactId.parse("z/z@1.0.0"), DIGEST_A)),
            LockedArtifact(PinnedArtifact(ArtifactId.parse("a/a@1.0.0"), DIGEST_B)),
        ),
        units=(
            LockedUnit(UnitId.parse("skill/zzz/minimal"), "builtin", DIGEST_A),
            LockedUnit(UnitId.parse("agent/aaa"), "builtin", DIGEST_B),
        ),
        outputs=(LockedOutput("z.md", DIGEST_A), LockedOutput("a.md", DIGEST_B)),
    )

    canonical = lock.canonical()

    assert [a.sort_key for a in canonical.artifacts] == ["a/a@1.0.0", "z/z@1.0.0"]
    assert [u.sort_key for u in canonical.units] == ["agent/aaa", "skill/zzz/minimal"]
    assert [o.sort_key for o in canonical.outputs] == ["a.md", "z.md"]


def test_canonical_is_idempotent() -> None:
    lock = LockFile(
        "0.5.0", STAMP, outputs=(LockedOutput("b", DIGEST_A), LockedOutput("a", DIGEST_B))
    )

    assert lock.canonical().canonical() == lock.canonical()


def test_locks_differing_only_in_assembly_order_are_equal_after_canonicalising() -> None:
    forward = LockFile(
        "0.5.0", STAMP, outputs=(LockedOutput("a", DIGEST_A), LockedOutput("b", DIGEST_B))
    )
    backward = LockFile(
        "0.5.0", STAMP, outputs=(LockedOutput("b", DIGEST_B), LockedOutput("a", DIGEST_A))
    )

    assert forward.canonical() == backward.canonical()


def test_equals_ignoring_resolved_at_sees_past_the_timestamp() -> None:
    earlier = LockFile("0.5.0", STAMP, outputs=(LockedOutput("a", DIGEST_A),))
    later = LockFile("0.5.0", "2026-12-25T11:11:11Z", outputs=(LockedOutput("a", DIGEST_A),))

    assert earlier.equals_ignoring_resolved_at(later)
    assert earlier != later, "the objects genuinely differ; only the comparison is blind"


def test_equals_ignoring_resolved_at_ignores_assembly_order() -> None:
    """Order must not masquerade as a real re-resolution."""
    forward = LockFile(
        "0.5.0", STAMP, outputs=(LockedOutput("a", DIGEST_A), LockedOutput("b", DIGEST_B))
    )
    backward = LockFile(
        "0.5.0",
        "2026-12-25T11:11:11Z",
        outputs=(LockedOutput("b", DIGEST_B), LockedOutput("a", DIGEST_A)),
    )

    assert forward.equals_ignoring_resolved_at(backward)


@pytest.mark.parametrize(
    ("other", "why"),
    [
        (LockFile("9.9.9", STAMP, outputs=(LockedOutput("a", DIGEST_A),)), "version differs"),
        (LockFile("0.5.0", STAMP, outputs=(LockedOutput("a", DIGEST_B),)), "digest differs"),
        (LockFile("0.5.0", STAMP, outputs=(LockedOutput("b", DIGEST_A),)), "path differs"),
        (LockFile("0.5.0", STAMP), "output removed"),
    ],
)
def test_a_real_difference_is_not_ignored(other: LockFile, why: str) -> None:
    """The blindness must be confined to the timestamp."""
    base = LockFile("0.5.0", STAMP, outputs=(LockedOutput("a", DIGEST_A),))

    assert not base.equals_ignoring_resolved_at(other), why


@pytest.mark.parametrize(
    "stamp",
    [
        "2026-08-09T02:40:00+00:00",  # same instant, different bytes
        "2026-08-09 02:40:00Z",  # space instead of T
        "2026-08-09T02:40:00.123Z",  # sub-second precision
        "2026-08-09",
        "",
    ],
)
def test_a_non_canonical_timestamp_is_rejected(stamp: str) -> None:
    """A tolerated variant would round-trip and then break stability silently."""
    with pytest.raises(ValueError, match="ISO-8601 UTC"):
        LockFile("0.5.0", stamp)


def test_the_schema_version_defaults_to_the_current_one() -> None:
    assert LockFile("0.5.0", STAMP).lock_version == LOCK_SCHEMA_VERSION


def test_to_mapping_never_shares_nested_objects() -> None:
    """Shared objects are what make PyYAML emit anchors.

    The dumper refuses aliases too; this is the second line of defence, and the
    one that keeps the data itself honest.
    """
    shared = PinnedArtifact(ArtifactId.parse("acme/sec@2.1.0"), DIGEST_A)
    lock = LockFile(
        "0.5.0",
        STAMP,
        artifacts=(LockedArtifact(shared, source="one"), LockedArtifact(shared, source="two")),
    )

    mapping = lock.to_mapping()

    first, second = mapping["artifacts"]
    assert first is not second
    assert first["digest"] == second["digest"]


def test_locks_are_immutable() -> None:
    lock = LockFile("0.5.0", STAMP)

    with pytest.raises(AttributeError):
        lock.resolved_at = "2026-12-25T11:11:11Z"  # type: ignore[misc]
