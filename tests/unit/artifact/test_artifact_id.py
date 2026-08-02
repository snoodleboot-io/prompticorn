"""Artifact identity: parsing, the default namespace, and rejection (PRO-107).

The namespace rules are the part that has to hold for years: every serialised
form carries a namespace today so that introducing real ones later changes what
the field contains, never whether it is there.
"""

import pytest

from prompticorn.artifact import (
    DEFAULT_NAMESPACE,
    ArtifactId,
    InvalidArtifactIdError,
    SemanticVersion,
)


def _v(raw: str) -> SemanticVersion:
    return SemanticVersion.parse(raw)


@pytest.mark.parametrize(
    ("raw", "namespace", "name", "version"),
    [
        ("acme-sec@2.1.0", "local", "acme-sec", "2.1.0"),
        ("local/acme-sec@2.1.0", "local", "acme-sec", "2.1.0"),
        ("acme/security-agent@2.1.0", "acme", "security-agent", "2.1.0"),
        ("acme/sec@1.0.0-rc.1", "acme", "sec", "1.0.0-rc.1"),
        ("acme/sec@1.0.0-rc.1+build.5", "acme", "sec", "1.0.0-rc.1+build.5"),
        # Charset edges: digits, dots, underscores, hyphens.
        ("ns0/agent_skill.map-2@0.0.1", "ns0", "agent_skill.map-2", "0.0.1"),
    ],
)
def test_parse_splits_into_typed_fields(raw: str, namespace: str, name: str, version: str) -> None:
    parsed = ArtifactId.parse(raw)

    assert parsed.namespace == namespace
    assert parsed.name == name
    assert parsed.version == _v(version)


def test_namespace_defaults_to_local_when_omitted() -> None:
    assert ArtifactId.parse("acme-sec@2.1.0").namespace == DEFAULT_NAMESPACE


def test_the_default_namespace_is_local() -> None:
    """Pinned as a value, not just as behaviour — it is part of the format."""
    assert DEFAULT_NAMESPACE == "local"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        # The namespace is emitted even when it was omitted on input, and even
        # when it is the default. This is what makes real namespaces a
        # non-migration later.
        ("acme-sec@2.1.0", "local/acme-sec@2.1.0"),
        ("local/acme-sec@2.1.0", "local/acme-sec@2.1.0"),
        ("acme/security-agent@2.1.0", "acme/security-agent@2.1.0"),
        ("acme/sec@1.0.0-rc.1+build.5", "acme/sec@1.0.0-rc.1+build.5"),
    ],
)
def test_render_always_carries_a_namespace(raw: str, expected: str) -> None:
    assert ArtifactId.parse(raw).render() == expected


@pytest.mark.parametrize(
    "raw",
    [
        "local/acme-sec@2.1.0",
        "acme/security-agent@2.1.0",
        "acme/sec@1.0.0-rc.1",
        "acme/sec@1.0.0-rc.1+build.5",
    ],
)
def test_parse_render_round_trips(raw: str) -> None:
    assert ArtifactId.parse(raw).render() == raw


def test_an_omitted_namespace_round_trips_through_its_rendered_form() -> None:
    once = ArtifactId.parse("acme-sec@2.1.0")

    assert ArtifactId.parse(once.render()) == once


def test_the_two_spellings_of_the_default_namespace_are_the_same_id() -> None:
    assert ArtifactId.parse("acme-sec@2.1.0") == ArtifactId.parse("local/acme-sec@2.1.0")


def test_equal_ids_hash_alike() -> None:
    a = ArtifactId.parse("acme-sec@2.1.0")
    b = ArtifactId.parse("local/acme-sec@2.1.0")

    assert hash(a) == hash(b)
    assert len({a, b}) == 1


def test_str_is_the_rendered_form() -> None:
    assert str(ArtifactId.parse("acme-sec@2.1.0")) == "local/acme-sec@2.1.0"


def test_coordinate_omits_the_version() -> None:
    assert ArtifactId.parse("acme/sec@2.1.0").coordinate == "acme/sec"


def test_the_same_artifact_at_two_versions_shares_a_coordinate() -> None:
    older = ArtifactId.parse("acme/sec@2.1.0")
    newer = ArtifactId.parse("acme/sec@3.0.0")

    assert older.coordinate == newer.coordinate
    assert older != newer


def test_local_factory_uses_the_default_namespace() -> None:
    built = ArtifactId.local("acme-sec", _v("2.1.0"))

    assert built == ArtifactId.parse("acme-sec@2.1.0")
    assert built.render() == "local/acme-sec@2.1.0"


def test_local_factory_validates_the_name() -> None:
    """Otherwise it would be a hole around the grammar `parse` enforces."""
    with pytest.raises(InvalidArtifactIdError):
        ArtifactId.local("Bad Name", _v("1.0.0"))


def test_direct_construction_validates_coordinates() -> None:
    """A bypass here would render ids that cannot be parsed back."""
    with pytest.raises(InvalidArtifactIdError):
        ArtifactId(namespace="ACME", name="sec", version=_v("1.0.0"))

    with pytest.raises(InvalidArtifactIdError):
        ArtifactId(namespace="acme", name="Sec", version=_v("1.0.0"))


@pytest.mark.parametrize(
    ("raw", "expected_reason_fragment"),
    [
        ("", "is empty"),
        ("acme-sec", "is missing '@'"),
        ("acme-sec@", "no version after '@'"),
        ("@2.1.0", "no name before '@'"),
        ("acme-sec@2.1.0@3", "more than one '@'"),
        ("a/b/c@1.0.0", "more than one '/'"),
        ("/sec@1.0.0", "empty namespace"),
        ("acme/@1.0.0", "empty name"),
        (" acme-sec@2.1.0", "whitespace"),
        ("acme-sec@2.1.0 ", "whitespace"),
        ("ACME/sec@1.0.0", "uppercase"),
        ("acme/Sec@1.0.0", "uppercase"),
        ("-sec@1.0.0", "not of the form"),
        (".sec@1.0.0", "not of the form"),
        ("ac me/sec@1.0.0", "not of the form"),
    ],
)
def test_invalid_ids_are_rejected_with_a_reason(raw: str, expected_reason_fragment: str) -> None:
    with pytest.raises(InvalidArtifactIdError) as caught:
        ArtifactId.parse(raw)

    assert expected_reason_fragment in caught.value.reason
    assert caught.value.raw_id == raw


@pytest.mark.parametrize("raw", ["sec@not-a-version", "sec@1.2", "sec@v1.0.0", "sec@01.0.0"])
def test_a_bad_version_is_reported_as_a_bad_id(raw: str) -> None:
    """One exception type for a caller parsing ids, with the defect preserved."""
    with pytest.raises(InvalidArtifactIdError) as caught:
        ArtifactId.parse(raw)

    assert "version" in caught.value.reason


def test_a_range_is_not_accepted_as_an_identity() -> None:
    """An id is always pinned; `>=2.1` belongs to ArtifactRequirement."""
    with pytest.raises(InvalidArtifactIdError):
        ArtifactId.parse("acme-sec@>=2.1")


def test_a_non_string_is_rejected_rather_than_coerced() -> None:
    with pytest.raises(InvalidArtifactIdError) as caught:
        ArtifactId.parse(None)  # type: ignore[arg-type]

    assert "expected a string" in caught.value.reason


def test_ids_are_immutable() -> None:
    parsed = ArtifactId.parse("acme-sec@2.1.0")

    with pytest.raises(AttributeError):
        parsed.name = "other"  # type: ignore[misc]
