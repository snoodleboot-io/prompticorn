"""The lock: what a build actually resolved to.

``.prompticorn/prompticorn.lock`` is generated, committed, and read far more
often than written. The manifest declares version *ranges*; the lock records the
exact versions and digests they resolved to, so a range that starts matching
something new tomorrow is a visible diff rather than a silent change.

Everything about the format is chosen for stability: a re-lock over unchanged
inputs produces zero diff. Churn in a committed generated file is a review tax,
and a file that always shows up dirty stops being read.
"""

from prompticorn.lockfile.errors import (
    LockCorruptError,
    LockError,
    LockSchemaVersionError,
)
from prompticorn.lockfile.lock_file import (
    LOCK_SCHEMA_VERSION,
    SUPPORTED_LOCK_VERSIONS,
    LockFile,
)
from prompticorn.lockfile.lock_reader import LockReader
from prompticorn.lockfile.lock_writer import LockWriter
from prompticorn.lockfile.locked_artifact import LockedArtifact
from prompticorn.lockfile.locked_output import LockedOutput
from prompticorn.lockfile.locked_unit import LockedUnit

__all__ = [
    "LOCK_SCHEMA_VERSION",
    "SUPPORTED_LOCK_VERSIONS",
    "LockCorruptError",
    "LockError",
    "LockFile",
    "LockReader",
    "LockSchemaVersionError",
    "LockWriter",
    "LockedArtifact",
    "LockedOutput",
    "LockedUnit",
]
