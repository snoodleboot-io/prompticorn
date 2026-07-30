"""Canonical digest: stable across machines, checkouts, and editors (PRO-104)."""

import pytest

from prompticorn.content import canonical_text, digest_bytes, digest_text

BOM = "﻿"


@pytest.mark.unit
class TestCanonicalText:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("a\r\nb", "a\nb\n"),  # CRLF -> LF
            ("a\rb", "a\nb\n"),  # lone CR -> LF
            ("a\nb", "a\nb\n"),  # already LF
            ("a\nb\n", "a\nb\n"),  # single trailing newline preserved
            ("a\nb\n\n\n", "a\nb\n"),  # trailing blank lines collapsed
            (f"{BOM}a\n", "a\n"),  # BOM stripped
            (f"{BOM}a\r\n\n", "a\n"),  # all three at once
            ("", ""),  # empty stays empty
            ("\n", ""),  # a lone newline is no content
            ("  a  \n", "  a  \n"),  # interior whitespace untouched
        ],
    )
    def test_canonicalises(self, raw, expected):
        assert canonical_text(raw) == expected

    def test_is_idempotent(self):
        for raw in ("a\r\nb", f"{BOM}x\r\n\n\n", "", "\n\n"):
            once = canonical_text(raw)
            assert canonical_text(once) == once

    def test_a_bom_in_the_middle_is_content_not_a_marker(self):
        """Only a *leading* BOM is an encoding artefact."""
        assert canonical_text(f"a{BOM}b") == f"a{BOM}b\n"


@pytest.mark.unit
class TestDigestText:
    def test_line_ending_style_is_not_identity(self):
        """A CRLF checkout on Windows and an LF checkout on Linux must agree, or
        a lockfile pinned on one is unverifiable on the other."""
        assert digest_text("a\r\nb\r\n") == digest_text("a\nb\n")

    def test_trailing_newline_style_is_not_identity(self):
        assert digest_text("a\nb") == digest_text("a\nb\n") == digest_text("a\nb\n\n\n")

    def test_bom_is_not_identity(self):
        assert digest_text(f"{BOM}hello\n") == digest_text("hello\n")

    def test_different_content_differs(self):
        assert digest_text("a\n") != digest_text("b\n")

    def test_interior_whitespace_is_identity(self):
        """Canonicalisation normalises encoding artefacts, not authored content."""
        assert digest_text("a  b\n") != digest_text("a b\n")

    def test_contentless_documents_share_one_digest(self):
        """Empty and newline-only both carry no content. Distinguishing them
        would make the digest depend on a stray blank line an editor left."""
        assert digest_text("") == digest_text("\n") == digest_text("\n\n\n")

    def test_contentless_differs_from_content(self):
        assert digest_text("") != digest_text("a\n")

    def test_is_stable_across_calls(self):
        assert digest_text("content\n") == digest_text("content\n")

    def test_is_hex_sha256(self):
        value = digest_text("content\n")
        assert len(value) == 64
        assert all(c in "0123456789abcdef" for c in value)

    def test_matches_a_known_value(self):
        """Pins the algorithm itself: sha256 over canonical UTF-8 bytes. If this
        changes, every recorded digest in every lockfile is invalidated."""
        import hashlib

        assert digest_text("hello\n") == hashlib.sha256(b"hello\n").hexdigest()


@pytest.mark.unit
class TestDigestBytes:
    def test_agrees_with_digest_text(self):
        assert digest_bytes("hello\n".encode()) == digest_text("hello\n")

    def test_canonicalises_line_endings(self):
        assert digest_bytes(b"a\r\nb\r\n") == digest_text("a\nb\n")

    def test_strips_a_utf8_bom(self):
        assert digest_bytes(b"\xef\xbb\xbfhello\n") == digest_text("hello\n")

    def test_rejects_invalid_utf8_rather_than_substituting(self):
        """Replacement characters would silently change the digest, so invalid
        bytes must surface as an error."""
        with pytest.raises(UnicodeDecodeError):
            digest_bytes(b"\xff\xfe invalid")
