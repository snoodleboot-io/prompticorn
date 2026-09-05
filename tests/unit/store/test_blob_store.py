"""The content-addressed blob cache (PRO-127).

Most of these are about what must *not* be in the store after something goes
wrong. A cache that keeps a truncated blob at the path its digest claims poisons
every later offline build, and the failure surfaces as corruption in the source
rather than as the fetch that actually died — so "leaves nothing behind" is the
property under test almost throughout.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from prompticorn.sources.errors import DigestMismatchError
from prompticorn.store import BlobStore, BlobTooLargeError

CONTENT = b"# Testing Strategies\n\nThree shapes get argued about.\n"
DIGEST = hashlib.sha256(CONTENT).hexdigest()


@pytest.fixture
def store(tmp_path: Path) -> BlobStore:
    return BlobStore(root=tmp_path / "cas")


def staged(store: BlobStore) -> list[Path]:
    """Anything left in the staging area."""
    staging = store.directory / "tmp"
    return sorted(staging.glob("*")) if staging.is_dir() else []


class TestRoundTrip:
    def test_put_returns_the_content_digest(self, store: BlobStore):
        assert store.put(CONTENT) == DIGEST

    def test_stored_content_reads_back_unchanged(self, store: BlobStore):
        assert store.read(store.put(CONTENT)) == CONTENT

    def test_a_stored_blob_is_present(self, store: BlobStore):
        store.put(CONTENT)

        assert store.has(DIGEST)

    def test_an_unstored_blob_is_absent(self, store: BlobStore):
        assert not store.has(DIGEST)

    def test_the_path_fans_out_by_digest(self, store: BlobStore):
        """Flat directories with hundreds of thousands of entries are slow to
        list on most filesystems."""
        path = store.path_for(DIGEST)

        assert path.parent.name == DIGEST[2:4]
        assert path.parent.parent.name == DIGEST[:2]
        assert path.name == DIGEST

    def test_streaming_and_buffered_writes_agree(self, store: BlobStore):
        chunked = BlobStore(root=store.directory).put_stream([CONTENT[:10], CONTENT[10:]])

        assert chunked == store.put(CONTENT)


class TestNothingUnverifiedIsKept:
    def test_a_digest_mismatch_stores_nothing(self, store: BlobStore):
        with pytest.raises(DigestMismatchError):
            store.put(CONTENT, expected="0" * 64)

        assert not store.has("0" * 64)
        assert not store.has(DIGEST)
        assert list(store.blobs()) == []

    def test_a_digest_mismatch_leaves_no_partial_file(self, store: BlobStore):
        with pytest.raises(DigestMismatchError):
            store.put(CONTENT, expected="0" * 64)

        assert staged(store) == []

    def test_an_interrupted_stream_stores_nothing(self, store: BlobStore):
        """Crash injection: the generator dies halfway, as a dropped connection
        would."""

        def dying():
            yield CONTENT[:20]
            raise ConnectionError("connection reset")

        with pytest.raises(ConnectionError):
            store.put_stream(dying())

        assert list(store.blobs()) == []
        assert staged(store) == []

    def test_an_oversized_blob_aborts_and_stores_nothing(self, store: BlobStore):
        small = BlobStore(root=store.directory, max_bytes=10)

        with pytest.raises(BlobTooLargeError):
            small.put(CONTENT)

        assert list(small.blobs()) == []
        assert staged(small) == []

    def test_the_size_limit_aborts_mid_stream_not_after_it(self, store: BlobStore):
        """A limit enforced after the read has already lost. Proven by counting
        how much of the stream was consumed."""
        consumed = []

        def counted():
            for index in range(100):
                consumed.append(index)
                yield b"x" * 1000

        small = BlobStore(root=store.directory, max_bytes=5000)

        with pytest.raises(BlobTooLargeError):
            small.put_stream(counted())

        assert len(consumed) < 100, "the whole stream was read before the limit fired"


class TestImmutability:
    def test_rewriting_an_existing_blob_is_a_no_op(self, store: BlobStore):
        """The path already holds bytes that hash to that name. Overwriting
        would only create a window where it exists but is incomplete."""
        store.put(CONTENT)
        before = store.path_for(DIGEST).stat().st_mtime_ns

        store.put(CONTENT)

        assert store.path_for(DIGEST).stat().st_mtime_ns == before

    def test_two_writers_of_the_same_blob_converge(self, store: BlobStore):
        """Interleaved, as two CLI invocations would be. Neither sees a partial
        file, because each stages under its own name."""
        one = BlobStore(root=store.directory)
        two = BlobStore(root=store.directory)

        assert one.put(CONTENT) == two.put(CONTENT) == DIGEST
        assert store.read(DIGEST) == CONTENT
        assert list(store.blobs()) == [DIGEST]


class TestPurging:
    def test_clear_empties_the_cache(self, store: BlobStore):
        store.put(CONTENT)
        store.put(b"another blob\n")

        assert store.clear() == 2
        assert list(store.blobs()) == []

    def test_a_purged_cache_only_costs_a_refetch(self, store: BlobStore):
        """The cache holds nothing that cannot be obtained again, which is what
        makes purging safe to offer at all."""
        store.put(CONTENT)
        store.clear()

        assert store.put(CONTENT) == DIGEST
        assert store.read(DIGEST) == CONTENT

    def test_clearing_an_absent_cache_is_not_an_error(self, tmp_path: Path):
        assert BlobStore(root=tmp_path / "never-created").clear() == 0

    def test_staging_is_not_listed_as_a_blob(self, store: BlobStore):
        store.put(CONTENT)
        (store.directory / "tmp").mkdir(parents=True, exist_ok=True)
        (store.directory / "tmp" / "leftover.partial").write_bytes(b"junk")

        assert list(store.blobs()) == [DIGEST]
