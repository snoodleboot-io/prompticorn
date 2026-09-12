"""Profiles as files a human can read, diff and commit (PRO-130).

The authoritative half of the store. A SQLite index over these arrives later and
is derived — deleting it must cost nothing — so everything needed to reconstruct
that index lives here, in YAML, under ``~/.prompticorn/profiles``.

Layout::

    profiles/<name>/v1.yaml
                    v2.yaml     # saving produces N+1; N is never rewritten

The ticket describes ``profiles/<name>.yaml``. A single file cannot hold
immutable versions, and immutable versions are what make ``diff v3 v4``
meaningful and rollback a copy rather than a reconstruction — so the name
becomes a directory and the versions are files inside it.

**Writes are atomic.** Content goes to a temporary file in the same directory
and is moved into place with ``os.replace``, which is atomic on POSIX and
Windows alike. A crash mid-write therefore leaves the previous version intact
and never a half-written one; a profile is applied to configure a repository,
and a truncated one would configure it wrongly rather than fail.

**Claiming a version number is exclusive.** Two saves racing for N+1 both create
with ``O_EXCL``; the loser retries at N+2 rather than overwriting the winner.
"""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

import yaml

from prompticorn.profiles.errors import (
    InvalidProfileError,
    InvalidProfileNameError,
    ProfileNotFoundError,
)
from prompticorn.profiles.profile import FIRST_VERSION, Profile
from prompticorn.store.store_paths import ensure_directory, profiles_root

# Names become directories, so they are restricted to what is unambiguous on
# every filesystem: no separators, no traversal, no leading dot.
_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_MAX_NAME_LENGTH = 64

VERSION_PREFIX = "v"
VERSION_SUFFIX = ".yaml"
_VERSION_PATTERN = re.compile(rf"^{VERSION_PREFIX}(\d+)\{VERSION_SUFFIX}$")

# Retries when two saves race for the same version number. Small: each retry
# means another process won, and a store with dozens of simultaneous writers is
# not a situation this design is for.
_CLAIM_ATTEMPTS = 16


class FileProfileStore:
    """Profiles stored as YAML under a directory per name.

    Args:
        root: Where profiles live. Defaults to the one under
            ``PROMPTICORN_HOME``.
    """

    def __init__(self, root: Path | None = None) -> None:
        self._root = root

    @property
    def root(self) -> Path:
        """Resolved late, so a store built at import time does not freeze
        ``PROMPTICORN_HOME`` before a test sets it."""
        return self._root if self._root is not None else profiles_root()

    # -- naming ----------------------------------------------------------

    @staticmethod
    def validate_name(name: str) -> str:
        """Return ``name`` if it can be a directory, else raise.

        Refused at the boundary rather than sanitised: rewriting a name means
        ``save`` and ``load`` can disagree about where a profile lives.
        """
        if not name:
            raise InvalidProfileNameError(name, "is empty")
        if len(name) > _MAX_NAME_LENGTH:
            raise InvalidProfileNameError(name, f"exceeds {_MAX_NAME_LENGTH} characters")
        if not _NAME_PATTERN.match(name):
            raise InvalidProfileNameError(
                name,
                "must start with a letter or digit and contain only letters, "
                "digits, dot, dash or underscore",
            )
        return name

    def directory_for(self, name: str) -> Path:
        return self.root / self.validate_name(name)

    def path_for(self, name: str, version: int) -> Path:
        return self.directory_for(name) / f"{VERSION_PREFIX}{version}{VERSION_SUFFIX}"

    # -- reading ---------------------------------------------------------

    def names(self) -> tuple[str, ...]:
        """Every profile name, sorted."""
        if not self.root.is_dir():
            return ()
        return tuple(sorted(child.name for child in self.root.iterdir() if child.is_dir()))

    def versions_of(self, name: str) -> tuple[int, ...]:
        """Every stored version of one profile, ascending."""
        directory = self.directory_for(name)
        if not directory.is_dir():
            return ()
        found = []
        for child in directory.iterdir():
            match = _VERSION_PATTERN.match(child.name)
            if match and child.is_file():
                found.append(int(match.group(1)))
        return tuple(sorted(found))

    def current_version(self, name: str) -> int | None:
        """The highest stored version, or None if the profile does not exist."""
        versions = self.versions_of(name)
        return versions[-1] if versions else None

    def load(self, name: str, version: int | None = None) -> Profile:
        """One version of a profile, defaulting to the newest.

        Raises:
            ProfileNotFoundError: If the profile or version does not exist.
            InvalidProfileError: If the file is not a readable profile.
        """
        resolved = version if version is not None else self.current_version(name)
        if resolved is None:
            raise ProfileNotFoundError(name)
        path = self.path_for(name, resolved)
        if not path.is_file():
            raise ProfileNotFoundError(name, resolved)
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
            raise InvalidProfileError(str(path), str(error)) from error
        try:
            return Profile.from_mapping(raw)
        except ValueError as error:
            raise InvalidProfileError(str(path), str(error)) from error

    # -- writing ---------------------------------------------------------

    def save(self, name: str, payload: dict, description: str, created_at: str) -> Profile:
        """Store a new version. Never rewrites an existing one.

        Returns:
            The profile as stored, carrying the version it was given.
        """
        directory = ensure_directory(self.directory_for(name))
        next_version = (self.current_version(name) or FIRST_VERSION - 1) + 1

        for attempt in range(_CLAIM_ATTEMPTS):
            candidate = next_version + attempt
            profile = Profile(
                name=name,
                version=candidate,
                payload=dict(payload),
                description=description,
                created_at=created_at,
            )
            if self._claim(directory, candidate, profile):
                return profile
        raise InvalidProfileError(
            str(directory), f"could not claim a version after {_CLAIM_ATTEMPTS} attempts"
        )

    def _claim(self, directory: Path, version: int, profile: Profile) -> bool:
        """Write this version if nobody else has. Returns whether we won.

        The exclusive create is the claim; the atomic replace is the write. Done
        in that order so two racers cannot both believe they own the number.
        """
        destination = directory / f"{VERSION_PREFIX}{version}{VERSION_SUFFIX}"
        try:
            # O_EXCL: fails rather than truncating if another process got here.
            handle = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            return False
        os.close(handle)

        # The claim above created an empty file at the version's own path. Until
        # the real content replaces it, that empty file *is* a partial version —
        # readable, listable, and wrong. Anything that goes wrong from here must
        # therefore remove it, or a crash leaves behind a version that exists and
        # says nothing.
        staged: Path | None = None
        try:
            rendered = yaml.safe_dump(
                profile.to_mapping(), sort_keys=True, default_flow_style=False, allow_unicode=True
            )
            # Same directory, so the replace is a rename within one filesystem.
            with tempfile.NamedTemporaryFile(
                "w", dir=directory, delete=False, suffix=".partial", encoding="utf-8", newline="\n"
            ) as partial:
                partial.write(rendered)
                staged = Path(partial.name)
            os.replace(staged, destination)
        except BaseException:
            destination.unlink(missing_ok=True)
            if staged is not None:
                staged.unlink(missing_ok=True)
            raise
        return True

    def delete(self, name: str) -> int:
        """Remove a profile and every version of it. Returns how many were removed."""
        directory = self.directory_for(name)
        if not directory.is_dir():
            raise ProfileNotFoundError(name)
        removed = 0
        for child in sorted(directory.iterdir()):
            if child.is_file():
                child.unlink()
                removed += 1
        directory.rmdir()
        return removed
