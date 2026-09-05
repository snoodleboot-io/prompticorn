"""The content-addressed blob cache (PRO-127).

Shared by every source implementation, including EE's remote one later. A blob
is named by the digest of its own bytes, which makes two properties fall out for
free: an entry can never be stale, and two processes fetching the same artifact
converge on the same path instead of racing to overwrite each other.

**Unverified bytes never occupy a CAS path.** Everything is written to a staging
file, hashed as it streams, and only moved into place once the digest is known
to be right. An interrupted or corrupt fetch therefore leaves nothing behind,
because the alternative — a truncated blob sitting at the path its digest
claims — poisons every later offline build and looks like corruption in the
source rather than a fetch that died.

Hashing happens **during** the stream, not after. Artifact size is unbounded, so
a size limit checked after reading is a limit that has already been exceeded.
"""

from __future__ import annotations

import hashlib
import os
import uuid
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

from prompticorn.sources.errors import DigestMismatchError
from prompticorn.store.errors import BlobTooLargeError
from prompticorn.store.store_paths import cas_root, cas_staging, ensure_directory

# Two levels of two hex characters. Directories with hundreds of thousands of
# entries are slow to list on most filesystems; 256 x 256 keeps any one of them
# small without making the tree deep enough to be annoying to inspect by hand.
FANOUT = 2
FANOUT_DEPTH = 2

# 256 MiB. Far above any real artifact and far below anything that would exhaust
# a disk unnoticed. Callers may lower it; the point is that a default exists.
DEFAULT_MAX_BYTES = 256 * 1024 * 1024

# Read size while streaming. Large enough that hashing dominates syscalls.
CHUNK_BYTES = 1024 * 1024


@dataclass(frozen=True)
class BlobStore:
    """Immutable blobs addressed by the sha256 of their content.

    Attributes:
        root: The CAS directory. Defaults to the one under ``PROMPTICORN_HOME``.
        max_bytes: Largest blob accepted, enforced mid-stream.
    """

    root: Path | None = None
    max_bytes: int = DEFAULT_MAX_BYTES

    @property
    def directory(self) -> Path:
        """The CAS root, resolved now rather than at construction.

        Late resolution keeps a store built at import time from freezing the
        value of ``PROMPTICORN_HOME`` before a test sets it.
        """
        return self.root if self.root is not None else cas_root()

    def path_for(self, digest: str) -> Path:
        """Where a blob with this digest lives, whether or not it is there."""
        parts = [
            digest[index : index + FANOUT] for index in range(0, FANOUT * FANOUT_DEPTH, FANOUT)
        ]
        return self.directory.joinpath(*parts, digest)

    def has(self, digest: str) -> bool:
        """Whether the blob is already cached."""
        return self.path_for(digest).is_file()

    def read(self, digest: str) -> bytes:
        """The blob's bytes.

        Raises:
            FileNotFoundError: If it is not cached. Deliberately not a store
                error: a cache miss is an ordinary condition, and the caller's
                answer is to fetch rather than to report a fault.
        """
        return self.path_for(digest).read_bytes()

    def put(self, content: bytes, expected: str | None = None) -> str:
        """Store bytes already in memory. Returns the digest."""
        return self.put_stream([content], expected)

    def put_stream(self, chunks: Iterable[bytes], expected: str | None = None) -> str:
        """Store a stream of chunks, hashing as it goes.

        Args:
            chunks: The content, in whatever pieces the caller has it.
            expected: The digest the content is supposed to have. When given and
                the content does not match, nothing is stored.

        Returns:
            The digest the content actually hashed to.

        Raises:
            BlobTooLargeError: If the stream exceeds :attr:`max_bytes`. Raised
                as soon as the limit is passed, not after the stream ends.
            DigestMismatchError: If ``expected`` was given and does not match.
        """
        ensure_directory(self.directory)
        staging = ensure_directory(cas_staging() if self.root is None else self.directory / "tmp")
        # A unique name per attempt: two processes writing the same blob must not
        # share a partial file, or one truncates what the other is hashing.
        partial = staging / f"{uuid.uuid4().hex}.partial"

        digest = hashlib.sha256()
        written = 0
        try:
            with partial.open("wb") as handle:
                for chunk in chunks:
                    written += len(chunk)
                    if written > self.max_bytes:
                        raise BlobTooLargeError(self.max_bytes, written)
                    digest.update(chunk)
                    handle.write(chunk)
            actual = digest.hexdigest()
            if expected is not None and actual != expected:
                raise DigestMismatchError("blob", expected, actual)
            self._commit(partial, actual)
            return actual
        finally:
            # Covers the mismatch, the size abort, and any exception the caller's
            # own generator raised mid-stream. A partial file that outlived its
            # attempt is exactly what must never reach a CAS path.
            partial.unlink(missing_ok=True)

    def _commit(self, partial: Path, digest: str) -> None:
        """Move verified content into place, or discard it as already present.

        Blobs are immutable by digest, so an existing entry is never overwritten:
        it already holds bytes that hash to this name, and rewriting it would
        only create a window in which the path exists but is incomplete.
        """
        destination = self.path_for(digest)
        if destination.is_file():
            return
        ensure_directory(destination.parent)
        os.replace(partial, destination)

    def clear(self) -> int:
        """Delete every cached blob. Returns how many were removed.

        Safe by construction: the CAS is a cache, so a purge costs a refetch and
        nothing else. Staging is cleared too, which is where anything abandoned
        by a killed process would be.
        """
        removed = 0
        if not self.directory.is_dir():
            return removed
        for path in sorted(self.directory.rglob("*")):
            if path.is_file():
                path.unlink(missing_ok=True)
                removed += 1
        return removed

    def blobs(self) -> Iterator[str]:
        """Every cached digest, sorted."""
        if not self.directory.is_dir():
            return iter(())
        staging = self.directory / "tmp"
        return iter(
            sorted(
                path.name
                for path in self.directory.rglob("*")
                if path.is_file() and staging not in path.parents
            )
        )
