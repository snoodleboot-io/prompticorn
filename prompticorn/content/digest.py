"""Canonical digest of authored content (PRO-104).

Content is canonicalised before hashing so the same authored bytes produce the
same digest regardless of the machine, checkout, or editor that produced them.
Without this a CRLF checkout on Windows and an LF checkout on Linux disagree
about every file, and a lockfile pinned on one is unverifiable on the other.

**The digest covers the stored source bytes, not post-transform text.**
Provenance should describe the artifact as authored. The downstream transforms
(header stripping and friends) are deterministic, so the lockfile's output
digests cover the rest of the pipeline; hashing post-transform text here would
merely make provenance depend on the transform's version.
"""

from __future__ import annotations

import hashlib

_BOM = "﻿"


def canonical_text(text: str) -> str:
    """Normalise authored text to its canonical form.

    - strip a leading UTF-8 BOM (editors add it; it is not content)
    - CRLF and lone CR both become LF, so line-ending style is not identity
    - exactly one trailing newline, so "did the editor add one" is not identity

    A document that is empty or contains only newlines canonicalises to the
    empty string: both carry no content, and distinguishing them would make the
    digest depend on whether an editor left a stray blank line.
    """
    if text.startswith(_BOM):
        text = text[len(_BOM) :]
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.rstrip("\n")
    return f"{text}\n" if text else ""


def digest_text(text: str) -> str:
    """sha256 of the canonical form, as lowercase hex."""
    return hashlib.sha256(canonical_text(text).encode("utf-8")).hexdigest()


def digest_bytes(raw: bytes) -> str:
    """sha256 of canonicalised UTF-8 bytes.

    Decoding is strict: content that is not valid UTF-8 is a defect worth
    surfacing, not something to paper over with replacement characters that
    would silently change the digest.
    """
    return digest_text(raw.decode("utf-8"))
