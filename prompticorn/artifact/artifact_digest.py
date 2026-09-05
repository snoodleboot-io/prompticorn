"""One definition of what an artifact's content hashes to (PRO-124).

The lock records an artifact digest; a source verifies one on fetch. If those
two are computed differently, every artifact fetched from a source disagrees
with the lock that pinned it, and the failure looks like corruption rather than
like two functions that drifted apart. So the definition lives here and both
call it.

It is composed from the units' own digests rather than by re-reading content,
which keeps one definition of canonicalisation in the codebase instead of two:
:func:`~prompticorn.content.digest.digest_text` decides what a unit hashes to,
and this decides how those hashes combine.
"""

from __future__ import annotations

from collections.abc import Iterable

from prompticorn.content.digest import digest_text

# Between a unit's id and its digest. A character that cannot appear in either,
# so no pair can be made to look like a different pair.
MEMBER_SEPARATOR = ":"

# Between members. Sorted before joining, so the digest describes a *set* of
# units and does not depend on the order a source happened to enumerate them.
RECORD_SEPARATOR = "\n"


def artifact_digest(members: Iterable[tuple[str, str]]) -> str:
    """Digest covering every unit an artifact contains.

    Args:
        members: ``(rendered unit id, unit digest)`` pairs. Order is irrelevant;
            they are sorted before hashing.

    Returns:
        Lowercase hex sha256 over the sorted ``id:digest`` lines.
    """
    lines = sorted(f"{unit_id}{MEMBER_SEPARATOR}{digest}" for unit_id, digest in members)
    return digest_text(RECORD_SEPARATOR.join(lines))
