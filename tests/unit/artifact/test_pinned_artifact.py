"""Pairing an identity with the digest of its content (PRO-107).

The design point under test: the digest hangs off *this* type, not off
``ArtifactId``. That separation is what lets signing and provenance attach later
without a format break, so the tests that pin it are not incidental.
"""

import pytest

from prompticorn.artifact import ArtifactId, InvalidDigestError, PinnedArtifact
from prompticorn.content import digest_text


def _id(raw: str = "acme/sec@2.1.0") -> ArtifactId:
    return ArtifactId.parse(raw)


def test_for_content_uses_the_shared_canonical_digest() -> None:
    """One definition of "canonical" in the codebase; a second would drift."""
    pinned = PinnedArtifact.for_content(_id(), "hello world")

    assert pinned.digest == digest_text("hello world")


def test_the_digest_is_lowercase_hex_sha256() -> None:
    pinned = PinnedArtifact.for_content(_id(), "hello world")

    assert len(pinned.digest) == 64
    assert pinned.digest == pinned.digest.lower()
    int(pinned.digest, 16)


def test_matches_content_confirms_the_same_bytes() -> None:
    pinned = PinnedArtifact.for_content(_id(), "hello world")

    assert pinned.matches_content("hello world")
    assert not pinned.matches_content("hello world!")


@pytest.mark.parametrize(
    ("authored", "equivalent", "why"),
    [
        ("a\r\nb", "a\nb", "line-ending style is not identity"),
        ("a\nb", "a\nb\n", "a trailing newline is not identity"),
        ("﻿a\nb", "a\nb", "an editor's BOM is not content"),
    ],
)
def test_canonicalisation_is_inherited_not_reimplemented(
    authored: str, equivalent: str, why: str
) -> None:
    """A CRLF checkout must verify against a pin written on an LF checkout."""
    pinned = PinnedArtifact.for_content(_id(), authored)

    assert pinned.matches_content(equivalent), why


def test_the_digest_is_not_part_of_the_identity() -> None:
    """Two different contents under one version are the same *identity*.

    The id answers "which release"; the digest answers "which bytes". Folding
    the hash into the id would make it unwritable by a human in a manifest.
    """
    one = PinnedArtifact.for_content(_id(), "content A")
    two = PinnedArtifact.for_content(_id(), "content B")

    assert one.artifact_id == two.artifact_id
    assert one.digest != two.digest
    assert one != two


def test_artifact_id_carries_no_digest_field() -> None:
    """Guards the boundary structurally, not just by convention."""
    assert "digest" not in ArtifactId.__dataclass_fields__


def test_re_rendering_an_id_cannot_invalidate_a_digest() -> None:
    """The hash covers canonical content, never the identity string."""
    omitted = PinnedArtifact.for_content(ArtifactId.parse("sec@2.1.0"), "body")
    explicit = PinnedArtifact.for_content(ArtifactId.parse("local/sec@2.1.0"), "body")

    assert omitted.digest == explicit.digest
    assert omitted == explicit


def test_render_names_the_hash_algorithm() -> None:
    pinned = PinnedArtifact.for_content(_id(), "body")

    assert pinned.render() == f"acme/sec@2.1.0 sha256:{pinned.digest}"
    assert str(pinned) == pinned.render()


def test_equal_pins_hash_alike() -> None:
    one = PinnedArtifact.for_content(_id(), "body")
    two = PinnedArtifact.for_content(_id(), "body")

    assert one == two
    assert len({one, two}) == 1


@pytest.mark.parametrize(
    ("digest", "expected_reason_fragment"),
    [
        ("", "expected 64"),
        ("abc123", "expected 64"),
        ("f" * 63, "expected 64"),
        ("f" * 65, "expected 64"),
        ("g" * 64, "expected 64"),
        ("F" * 64, "uppercase"),
    ],
)
def test_a_malformed_digest_is_rejected(digest: str, expected_reason_fragment: str) -> None:
    """Worse than no digest: it looks like verification while never matching."""
    with pytest.raises(InvalidDigestError) as caught:
        PinnedArtifact(artifact_id=_id(), digest=digest)

    assert expected_reason_fragment in caught.value.reason
    assert caught.value.raw_digest == digest


def test_a_non_string_digest_is_rejected_rather_than_coerced() -> None:
    with pytest.raises(InvalidDigestError) as caught:
        PinnedArtifact(artifact_id=_id(), digest=None)  # type: ignore[arg-type]

    assert "expected a string" in caught.value.reason


def test_a_well_formed_digest_is_accepted_directly() -> None:
    """Reading a lock file must not require recomputing every hash."""
    pinned = PinnedArtifact(artifact_id=_id(), digest="a" * 64)

    assert pinned.digest == "a" * 64


def test_pins_are_immutable() -> None:
    pinned = PinnedArtifact.for_content(_id(), "body")

    with pytest.raises(AttributeError):
        pinned.digest = "b" * 64  # type: ignore[misc]
