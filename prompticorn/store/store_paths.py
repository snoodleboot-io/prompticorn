"""Where prompticorn keeps machine-local state (PRO-127).

One user, one machine, no server: `~/.prompticorn` is the hub every repo on this
machine shares — the blob cache, the install index, profiles, and the user
content layer. Nothing here is per-project; a project's own truth is its lock,
which lives in the repo.

`PROMPTICORN_HOME` overrides the location. That exists for tests and for people
who keep dotfiles elsewhere, and it must be honoured everywhere rather than in
the one place someone remembered — a store that is relocatable for the cache but
not for the index is not relocatable.

Directories are created 0700. The store holds a record of every repository on
this machine and, in time, credentials for the sources it pulls from. On a
shared box the default umask would make that world-readable.
"""

from __future__ import annotations

import os
from pathlib import Path

HOME_VARIABLE = "PROMPTICORN_HOME"
DEFAULT_HOME_NAME = ".prompticorn"

# Owner-only. Applied to the directories this module creates, and re-applied on
# an existing directory, because a store created before this rule existed should
# not stay open.
DIRECTORY_MODE = 0o700

CAS_DIRNAME = "cas"
TMP_DIRNAME = "tmp"
PROFILES_DIRNAME = "profiles"
CONTENT_DIRNAME = "content"
DATABASE_FILENAME = "store.db"


def home() -> Path:
    """The store root: ``$PROMPTICORN_HOME`` or ``~/.prompticorn``.

    Resolved on every call rather than cached, so a test that sets the variable
    does not have to reason about which module imported it first.
    """
    override = os.environ.get(HOME_VARIABLE)
    if override:
        return Path(override).expanduser()
    return Path.home() / DEFAULT_HOME_NAME


def ensure_directory(path: Path) -> Path:
    """Create ``path`` owner-only, and return it.

    The mode is applied whether or not the directory already existed. A
    permissive directory created by an older version, or by a shell, is exactly
    the case worth correcting.
    """
    path.mkdir(mode=DIRECTORY_MODE, parents=True, exist_ok=True)
    try:
        path.chmod(DIRECTORY_MODE)
    except (OSError, NotImplementedError):
        # Windows has no POSIX mode bits and chmod is largely inert there.
        # Failing to tighten permissions is not a reason to fail the command.
        pass
    return path


def cas_root() -> Path:
    """The content-addressed blob store."""
    return home() / CAS_DIRNAME


def cas_staging() -> Path:
    """Where partial writes live before they are verified.

    Inside the CAS root deliberately: the final move must be a rename within one
    filesystem to be atomic, and a staging area under ``/tmp`` can be on another
    device where ``os.replace`` degrades to a copy.
    """
    return cas_root() / TMP_DIRNAME


def database_path() -> Path:
    """The install index."""
    return home() / DATABASE_FILENAME


def profiles_root() -> Path:
    """Saved configuration profiles."""
    return home() / PROFILES_DIRNAME


def user_content_root() -> Path:
    """The user's own content layer, above the bundled tree."""
    return home() / CONTENT_DIRNAME
