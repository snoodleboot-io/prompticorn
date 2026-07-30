"""Cache for resolved content, keyed by source and unit (PRO-106).

Replaces a module-level ``lru_cache`` keyed on a ``Path``. Two problems with
that: it has no ``clear()`` a test fixture can call, so entries persist across
tests within a process; and once several sources are layered, a key that names
only the file cannot distinguish which layer produced the bytes, so a
long-running invocation would serve content from a source that no longer wins.
"""

from __future__ import annotations

from prompticorn.content.unit_id import UnitId


class ContentCache:
    """Memoises resolved text per ``(source, unit)``.

    Not thread-safe by design: builds are single-threaded, and a lock here would
    buy nothing but contention.
    """

    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], str] = {}
        self._hits = 0
        self._misses = 0

    @staticmethod
    def key(source_name: str, unit_id: UnitId) -> tuple[str, str]:
        return (source_name, unit_id.render())

    def get(self, source_name: str, unit_id: UnitId) -> str | None:
        value = self._entries.get(self.key(source_name, unit_id))
        if value is None:
            self._misses += 1
        else:
            self._hits += 1
        return value

    def put(self, source_name: str, unit_id: UnitId, text: str) -> None:
        self._entries[self.key(source_name, unit_id)] = text

    def clear(self) -> None:
        """Drop every entry. Called by the test fixture so cached content cannot
        leak between tests."""
        self._entries.clear()
        self._hits = 0
        self._misses = 0

    @property
    def stats(self) -> dict[str, int]:
        return {"entries": len(self._entries), "hits": self._hits, "misses": self._misses}

    def __len__(self) -> int:
        return len(self._entries)
