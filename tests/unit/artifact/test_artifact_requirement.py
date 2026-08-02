"""The manifest form: a coordinate plus an acceptable range (PRO-107).

The rule worth guarding is that the coordinate is checked *before* the version:
two artifacts sharing a name across namespaces are different artifacts, and
comparing only versions would let one silently satisfy a requirement on the other.
"""

import pytest

from prompticorn.artifact import (
    DEFAULT_NAMESPACE,
    ArtifactId,
    ArtifactRequirement,
    InvalidArtifactIdError,
    VersionRange,
)


@pytest.mark.parametrize(
    ("raw", "namespace", "name", "rendered_range"),
    [
        ("acme-sec@>=2.1,<3", "local", "acme-sec", ">=2.1.0,<3.0.0"),
        ("acme/security-agent@>=2.1,<3", "acme", "security-agent", ">=2.1.0,<3.0.0"),
        ("acme/sec@1.0.0", "acme", "sec", "==1.0.0"),
        ("acme/sec@>=1.0.0-rc.1", "acme", "sec", ">=1.0.0-rc.1"),
    ],
)
def test_parse_splits_into_typed_fields(
    raw: str, namespace: str, name: str, rendered_range: str
) -> None:
    parsed = ArtifactRequirement.parse(raw)

    assert parsed.namespace == namespace
    assert parsed.name == name
    assert parsed.version_range.render() == rendered_range


def test_namespace_defaults_to_local_and_is_always_rendered() -> None:
    parsed = ArtifactRequirement.parse("acme-sec@>=2.1,<3")

    assert parsed.namespace == DEFAULT_NAMESPACE
    assert parsed.render() == "local/acme-sec@>=2.1.0,<3.0.0"


@pytest.mark.parametrize(
    "raw",
    ["local/acme-sec@>=2.1.0,<3.0.0", "acme/sec@==1.0.0", "acme/sec@>=1.0.0-rc.1"],
)
def test_parse_render_round_trips(raw: str) -> None:
    assert ArtifactRequirement.parse(raw).render() == raw


def test_a_rendered_requirement_reparses_identically() -> None:
    once = ArtifactRequirement.parse("acme-sec@>=2.1,<3")

    assert ArtifactRequirement.parse(once.render()) == once


def test_str_is_the_rendered_form() -> None:
    assert str(ArtifactRequirement.parse("sec@1.0.0")) == "local/sec@==1.0.0"


def test_coordinate_omits_the_range() -> None:
    assert ArtifactRequirement.parse("acme/sec@>=2.1").coordinate == "acme/sec"


@pytest.mark.parametrize(
    ("candidate", "matches"),
    [
        ("acme/sec@2.1.0", True),
        ("acme/sec@2.9.9", True),
        ("acme/sec@3.0.0", False),
        ("acme/sec@2.0.0", False),
    ],
)
def test_matches_on_version(candidate: str, matches: bool) -> None:
    requirement = ArtifactRequirement.parse("acme/sec@>=2.1,<3")

    assert requirement.matches(ArtifactId.parse(candidate)) is matches


@pytest.mark.parametrize(
    ("candidate", "why"),
    [
        ("other/sec@2.1.0", "different namespace"),
        ("acme/other@2.1.0", "different name"),
        ("sec@2.1.0", "defaulted namespace is not the acme namespace"),
    ],
)
def test_a_version_in_range_does_not_match_a_different_coordinate(candidate: str, why: str) -> None:
    requirement = ArtifactRequirement.parse("acme/sec@>=2.1,<3")

    assert requirement.matches(ArtifactId.parse(candidate)) is False, why


def test_the_defaulted_namespace_matches_its_own_spelling() -> None:
    requirement = ArtifactRequirement.parse("sec@>=2.1,<3")

    assert requirement.matches(ArtifactId.parse("sec@2.1.0"))
    assert requirement.matches(ArtifactId.parse("local/sec@2.1.0"))


def test_prerelease_visibility_carries_through_to_matching() -> None:
    """The range's opt-in rule is what decides, not the requirement."""
    closed = ArtifactRequirement.parse("acme/sec@>=1.0.0")
    opted_in = ArtifactRequirement.parse("acme/sec@>=1.0.0-rc.1")

    assert closed.matches(ArtifactId.parse("acme/sec@2.0.0-alpha")) is False
    assert opted_in.matches(ArtifactId.parse("acme/sec@1.0.0-rc.2")) is True


def test_local_factory_uses_the_default_namespace() -> None:
    built = ArtifactRequirement.local("acme-sec", VersionRange.parse(">=2.1,<3"))

    assert built == ArtifactRequirement.parse("acme-sec@>=2.1,<3")


def test_local_factory_validates_the_name() -> None:
    with pytest.raises(InvalidArtifactIdError):
        ArtifactRequirement.local("Bad Name", VersionRange.parse(">=1.0.0"))


def test_direct_construction_validates_coordinates() -> None:
    with pytest.raises(InvalidArtifactIdError):
        ArtifactRequirement(
            namespace="ACME", name="sec", version_range=VersionRange.parse(">=1.0.0")
        )


@pytest.mark.parametrize(
    ("raw", "expected_reason_fragment"),
    [
        ("", "is empty"),
        ("acme-sec", "is missing '@'"),
        ("acme-sec@", "no version after '@'"),
        ("ACME/sec@>=1.0.0", "uppercase"),
        ("a/b/c@>=1.0.0", "more than one '/'"),
    ],
)
def test_invalid_requirements_are_rejected_with_a_reason(
    raw: str, expected_reason_fragment: str
) -> None:
    with pytest.raises(InvalidArtifactIdError) as caught:
        ArtifactRequirement.parse(raw)

    assert expected_reason_fragment in caught.value.reason
    assert caught.value.raw_id == raw


@pytest.mark.parametrize("raw", ["sec@>=", "sec@>=abc", "sec@>=2.1,"])
def test_a_bad_range_is_reported_as_a_bad_requirement(raw: str) -> None:
    with pytest.raises(InvalidArtifactIdError) as caught:
        ArtifactRequirement.parse(raw)

    assert "range" in caught.value.reason


def test_requirements_are_immutable() -> None:
    parsed = ArtifactRequirement.parse("sec@>=1.0.0")

    with pytest.raises(AttributeError):
        parsed.name = "other"  # type: ignore[misc]
