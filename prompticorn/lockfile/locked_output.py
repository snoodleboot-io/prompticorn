"""One generated output file in the lock (PRO-110)."""

from __future__ import annotations

from dataclasses import dataclass

PATH_KEY = "path"
DIGEST_KEY = "digest"


@dataclass(frozen=True)
class LockedOutput:
    """A file the build produced, and the digest of what it contained.

    Recording outputs alongside inputs is what lets a later `verify` answer two
    different questions: did the *sources* change, and did someone edit the
    *generated* files by hand. Digesting only the inputs would leave the second
    undetectable.

    Attributes:
        path: Repository-relative POSIX path. Always POSIX so a lock written on
            Windows and one written on Linux describe the same tree — a
            backslash here would make the file platform-specific.
        digest: sha256 of the file's canonical content, as lowercase hex.
    """

    path: str
    digest: str

    @property
    def sort_key(self) -> str:
        """The path — the defined order for outputs in the lock."""
        return self.path

    def to_mapping(self) -> dict[str, str]:
        """Plain, JSON-shaped data for the writer. A fresh dict every call."""
        return {PATH_KEY: self.path, DIGEST_KEY: self.digest}
