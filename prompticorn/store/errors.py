"""What can go wrong in the machine-local store (PRO-127)."""

from __future__ import annotations


class StoreError(Exception):
    """Base class for every error raised by the local store."""


class BlobTooLargeError(StoreError):
    """A blob exceeded the configured maximum and the write was abandoned.

    Raised mid-stream rather than after the read completes. The whole reason the
    limit exists is that artifact size is unbounded and the far end is not
    necessarily friendly; a limit enforced after buffering the content has
    already lost.
    """

    def __init__(self, limit: int, read_so_far: int) -> None:
        super().__init__(
            f"blob exceeds the {limit} byte limit (abandoned after {read_so_far} bytes)"
        )
        self.limit = limit
        self.read_so_far = read_so_far
