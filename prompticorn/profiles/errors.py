"""What can go wrong with a profile store (PRO-130)."""

from __future__ import annotations


class ProfileError(Exception):
    """Base class for every error raised by the profile store."""


class ProfileNotFoundError(ProfileError):
    """No profile of that name, or no such version of it."""

    def __init__(self, name: str, version: int | None = None) -> None:
        subject = f"{name}@v{version}" if version is not None else name
        super().__init__(f"no profile {subject!r}")
        self.name = name
        self.version = version


class InvalidProfileError(ProfileError):
    """A stored profile could not be understood.

    Raised rather than skipped. A profile that half-parses and is then applied
    writes a half-correct manifest into somebody's repository, which is a worse
    outcome than refusing to read it.
    """

    def __init__(self, path: str, reason: str) -> None:
        super().__init__(f"profile at {path} is unusable: {reason}")
        self.path = path
        self.reason = reason


class InvalidProfileNameError(ProfileError):
    """A name that cannot be used as a directory.

    Names become paths under the store, so anything with a separator or a
    traversal segment is refused at the boundary rather than sanitised. Silently
    rewriting a name means `save` and `load` can disagree about where a profile
    lives.
    """

    def __init__(self, name: str, reason: str) -> None:
        super().__init__(f"profile name {name!r} is invalid: {reason}")
        self.name = name
        self.reason = reason
