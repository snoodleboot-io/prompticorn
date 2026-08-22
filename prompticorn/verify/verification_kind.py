"""The ways a generated tree can fail verification (PRO-115).

Three findings, and they are not variations on one theme. Two of them mean the
generated tree drifted from what the lock recorded; the third means a file is
there that nothing accounts for. Collapsing them into "verification failed"
would throw away the only information the reader can act on.
"""

from __future__ import annotations

from enum import Enum


class VerificationKind(Enum):
    """A classified verification failure.

    ``TAMPERED`` is the alarming member. ``MISSING`` usually means someone
    deleted a file or never ran the build; ``UNKNOWN`` usually means a stray
    file or a tool that was switched away from without cleaning up. ``TAMPERED``
    means a generated file's content was changed by hand — the thing the
    source/generated wall exists to prevent, and the reason regeneration is safe
    to do at all.
    """

    MISSING = "missing"
    TAMPERED = "tampered"
    UNKNOWN = "unknown"

    @property
    def headline(self) -> str:
        """One line naming what happened, in the user's terms."""
        return _HEADLINES[self]

    @property
    def remediation(self) -> str:
        """What to do about it."""
        return _REMEDIATION[self]

    @property
    def is_suspicious(self) -> bool:
        """Whether this warrants investigation rather than a rebuild.

        Drives both the report's emphasis and the exit code. A missing file is a
        chore; an edited one is a claim that the generated tree is no longer
        derivable from source, which is a different conversation.
        """
        return self is VerificationKind.TAMPERED


_HEADLINES: dict[VerificationKind, str] = {
    VerificationKind.MISSING: "The lock names a file that does not exist",
    VerificationKind.TAMPERED: "A generated file was modified by hand",
    VerificationKind.UNKNOWN: "A generated file exists that the lock does not know about",
}

_REMEDIATION: dict[VerificationKind, str] = {
    VerificationKind.MISSING: "Run `prompticorn build` to regenerate the outputs.",
    VerificationKind.TAMPERED: (
        "Never hand-patch generated output — the edit is lost at the next build "
        "and is invisible to everyone reading the source. Move the change into "
        "the authored source, then run `prompticorn build`. If the edit was not "
        "yours, investigate before rebuilding."
    ),
    VerificationKind.UNKNOWN: (
        "Delete it, or run `prompticorn lock` if it is genuinely part of the "
        "build. A file nothing accounts for is how a rogue agent goes unnoticed."
    ),
}
