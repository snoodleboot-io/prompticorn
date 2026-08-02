"""Semver 2.0.0 parsing, rendering, and precedence (PRO-107).

The precedence table and the rejection table are the load-bearing parts of this
file. Both are lifted from the specification rather than from what the
implementation happens to do, so a regression shows up as a spec violation.
"""

import pytest

from prompticorn.artifact import InvalidSemanticVersionError, SemanticVersion

# Forms that must survive parse -> render unchanged. Includes the cases the
# spec calls out explicitly as legal and that hand-rolled parsers usually miss:
# uppercase and leading zeros inside *alphanumeric* prerelease identifiers.
ROUND_TRIP = [
    "0.0.0",
    "0.0.4",
    "1.2.3",
    "10.20.30",
    "1.0.0-alpha",
    "1.0.0-alpha.1",
    "1.0.0-0.3.7",
    "1.0.0-x.7.z.92",
    # Uppercase IS legal in a prerelease identifier (spec §9) — it is only the
    # artifact namespace/name that is lowercase-only, and for a different reason.
    "1.0.0-0A.is.legal",
    "1.0.0-alpha0.valid",
    "1.0.0+build.1",
    "1.0.0+21af26d3",
    "1.1.2-prerelease+meta",
    "1.0.0-rc.1+build.123",
    "2.0.0-rc.1+build.123",
]


@pytest.mark.parametrize("raw", ROUND_TRIP)
def test_parse_render_round_trips(raw: str) -> None:
    assert SemanticVersion.parse(raw).render() == raw


@pytest.mark.parametrize("raw", ROUND_TRIP)
def test_reparsing_a_rendered_version_is_stable(raw: str) -> None:
    once = SemanticVersion.parse(raw)

    assert SemanticVersion.parse(once.render()) == once


def test_components_are_parsed_into_typed_fields() -> None:
    version = SemanticVersion.parse("1.2.3-rc.1+build.5")

    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.prerelease == ("rc", "1")
    assert version.build == ("build", "5")


def test_str_is_the_rendered_form() -> None:
    assert str(SemanticVersion.parse("1.2.3-rc.1")) == "1.2.3-rc.1"


# Straight from the spec's own worked example (§11).
PRECEDENCE_CHAIN = [
    "1.0.0-alpha",
    "1.0.0-alpha.1",
    "1.0.0-alpha.beta",
    "1.0.0-beta",
    "1.0.0-beta.2",
    "1.0.0-beta.11",
    "1.0.0-rc.1",
    "1.0.0",
]


@pytest.mark.parametrize(("lower", "higher"), list(zip(PRECEDENCE_CHAIN, PRECEDENCE_CHAIN[1:])))
def test_spec_precedence_chain(lower: str, higher: str) -> None:
    assert SemanticVersion.parse(lower) < SemanticVersion.parse(higher)
    assert SemanticVersion.parse(higher) > SemanticVersion.parse(lower)


def test_sorting_follows_the_spec_chain() -> None:
    shuffled = [SemanticVersion.parse(raw) for raw in reversed(PRECEDENCE_CHAIN)]

    assert [v.render() for v in sorted(shuffled)] == PRECEDENCE_CHAIN


@pytest.mark.parametrize(
    ("lower", "higher"),
    [
        # Core components dominate.
        ("1.0.0", "2.0.0"),
        ("2.0.0", "2.1.0"),
        ("2.1.0", "2.1.1"),
        # A prerelease always sorts below its own release.
        ("1.0.0-rc.1", "1.0.0"),
        # Numeric identifiers compare numerically, not lexically: a string
        # comparison would put 11 below 2.
        ("1.0.0-beta.2", "1.0.0-beta.11"),
        # Numeric sorts below alphanumeric.
        ("1.0.0-1", "1.0.0-alpha"),
        # More fields outrank fewer when the prefix is equal.
        ("1.0.0-alpha", "1.0.0-alpha.1"),
    ],
)
def test_precedence_rules(lower: str, higher: str) -> None:
    assert SemanticVersion.parse(lower) < SemanticVersion.parse(higher)


@pytest.mark.parametrize(
    ("left", "right"),
    [("1.0.0+build.1", "1.0.0+build.2"), ("1.0.0", "1.0.0+meta"), ("1.0.0-rc.1+a", "1.0.0-rc.1+b")],
)
def test_build_metadata_is_ignored_by_precedence(left: str, right: str) -> None:
    """Spec §10. Equality has to agree, or sorting and dedupe both go wrong."""
    a, b = SemanticVersion.parse(left), SemanticVersion.parse(right)

    assert a == b
    assert not a < b
    assert not b < a
    assert a <= b and a >= b


def test_build_metadata_equal_versions_hash_alike() -> None:
    """Otherwise a set would hold two versions of equal precedence."""
    a = SemanticVersion.parse("1.0.0+build.1")
    b = SemanticVersion.parse("1.0.0+build.2")

    assert hash(a) == hash(b)
    assert len({a, b}) == 1


def test_build_metadata_survives_rendering_even_though_it_is_ignored() -> None:
    """Ignoring it for comparison must not mean discarding what the author wrote."""
    assert SemanticVersion.parse("1.0.0+build.1").render() == "1.0.0+build.1"


def test_comparison_against_a_foreign_type_is_not_claimed() -> None:
    assert SemanticVersion.parse("1.0.0") != "1.0.0"
    with pytest.raises(TypeError):
        _ = SemanticVersion.parse("1.0.0") < "1.0.0"  # type: ignore[operator]


# The rejection table. Each entry names a defect an author can actually make.
@pytest.mark.parametrize(
    ("raw", "expected_reason_fragment"),
    [
        ("", "is empty"),
        ("1", "expected major.minor.patch"),
        ("1.2", "expected major.minor.patch"),
        ("1.2.3.4", "at most"),
        ("01.2.3", "leading zero"),
        ("1.02.3", "leading zero"),
        ("1.2.03", "leading zero"),
        ("v1.2.3", "leading 'v'"),
        (" 1.2.3", "whitespace"),
        ("1.2.3 ", "whitespace"),
        ("1.2.3-", "prerelease part is empty"),
        ("1.2.3+", "build-metadata part is empty"),
        ("-1.2.3", "starts with '-'"),
        ("1.2.x", "not of the form"),
        # A *numeric* prerelease identifier may not carry a leading zero, even
        # though an alphanumeric one may (see "1.0.0-0A.is.legal" above).
        ("1.2.3-01", "not of the form"),
    ],
)
def test_invalid_versions_are_rejected_with_a_reason(
    raw: str, expected_reason_fragment: str
) -> None:
    with pytest.raises(InvalidSemanticVersionError) as caught:
        SemanticVersion.parse(raw)

    assert expected_reason_fragment in caught.value.reason
    assert caught.value.raw_version == raw


def test_a_non_string_is_rejected_rather_than_coerced() -> None:
    with pytest.raises(InvalidSemanticVersionError) as caught:
        SemanticVersion.parse(123)  # type: ignore[arg-type]

    assert "expected a string" in caught.value.reason


def test_the_error_message_quotes_the_offending_input() -> None:
    with pytest.raises(InvalidSemanticVersionError) as caught:
        SemanticVersion.parse("v1.2.3")

    assert "'v1.2.3'" in str(caught.value)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("3", "3.0.0"), ("2.1", "2.1.0"), ("2.1.4", "2.1.4"), ("1.0-rc.1", "1.0.0-rc.1")],
)
def test_partial_versions_complete_with_zeros(raw: str, expected: str) -> None:
    """Range operands may be abbreviated; `>=2.1` means `>=2.1.0`."""
    assert SemanticVersion.parse_partial(raw).render() == expected


@pytest.mark.parametrize("raw", ["3", "2.1", "1.0-rc.1"])
def test_abbreviated_forms_are_rejected_as_identities(raw: str) -> None:
    """An identity must be fully qualified, or a lock entry would be ambiguous."""
    with pytest.raises(InvalidSemanticVersionError):
        SemanticVersion.parse(raw)


def test_versions_are_immutable() -> None:
    version = SemanticVersion.parse("1.0.0")

    with pytest.raises(AttributeError):
        version.major = 2  # type: ignore[misc]


def test_core_ignores_prerelease_and_build() -> None:
    assert SemanticVersion.parse("1.2.3-rc.1+meta").core == (1, 2, 3)


@pytest.mark.parametrize(
    ("raw", "expected"), [("1.0.0", False), ("1.0.0-rc.1", True), ("1.0.0+meta", False)]
)
def test_is_prerelease(raw: str, expected: bool) -> None:
    assert SemanticVersion.parse(raw).is_prerelease is expected
