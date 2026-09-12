"""A repository's identity, independent of where it sits on disk (PRO-128).

The install index is keyed by repository, and the obvious key — the filesystem
path — is wrong. Move a checkout and every install it owns is orphaned; clone it
somewhere else and the index thinks it has never seen the project before. The
key has to come from the repository's own identity.

For a git repository that is the **root commit**: the one commit with no
parents. It is assigned when the history begins, it is identical in every clone,
and it does not move when the directory does. A remote URL would have been the
easier thing to read and the wrong answer — forks and mirrors change it while
the repository stays the same project.

Outside git there is nothing intrinsic to hash, so an identifier is generated
once and written to ``.prompticorn/repo_id``. That survives a move for certain,
and a clone if the file is committed, which is the most a non-versioned
directory can promise.
"""

from __future__ import annotations

import subprocess
import uuid
from pathlib import Path

from prompticorn.config_handler import ConfigHandler
from prompticorn.text_writer import write_text

REPO_ID_FILENAME = "repo_id"

# Timeout for the git call. A hung git invocation must not hang the CLI; the
# fallback identity is always available.
GIT_TIMEOUT_SECONDS = 5


def repo_id(root: Path) -> str:
    """A stable identifier for the repository at ``root``.

    Returns:
        The root commit of the git repository, or a generated identifier
        persisted under ``.prompticorn/``. Callers should treat it as opaque.
    """
    from_git = _root_commit(root)
    if from_git is not None:
        return from_git
    return _persisted_id(root)


def _root_commit(root: Path) -> str | None:
    """The hash of the repository's first commit, or None if there is not one.

    None covers every uninteresting case together: git is not installed, this is
    not a repository, or it is a repository with no commits yet. All three mean
    the same thing here — no intrinsic identity to read — so they are not
    distinguished.
    """
    try:
        completed = subprocess.run(
            ["git", "rev-list", "--max-parents=0", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    # A repository with more than one root commit (a merged unrelated history)
    # lists several. The last is the oldest, and picking by position rather than
    # by chance keeps the answer stable across runs.
    commits = completed.stdout.split()
    return commits[-1] if commits else None


def _persisted_id(root: Path) -> str:
    """Read, or create once, an identifier stored inside the project."""
    path = root / ConfigHandler.DEFAULT_CONFIG_DIR.name / REPO_ID_FILENAME
    if path.is_file():
        existing = path.read_text(encoding="utf-8").strip()
        if existing:
            return existing
    generated = uuid.uuid4().hex
    path.parent.mkdir(parents=True, exist_ok=True)
    write_text(path, f"{generated}\n")
    return generated
