"""Version-range parsing and matching, including the prerelease rule (PRO-107).

The prerelease-visibility table is the part worth guarding: without it every
open-ended range silently enrolls its users in unreleased versions.
"""

import pytest

from prompticorn.artifact import (
    ComparisonOperator,
    InvalidVersionRangeError,
    SemanticVersion,
    VersionConstraint,
    VersionRange,
)


def _v(raw: str) -> SemanticVersion:
    return SemanticVersion.parse(raw)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (">=2.1,<3", ">=2.1.0,<3.0.0"),
        (">=2.1.0", ">=2.1.0"),
        ("<=1.4.2", "<=1.4.2"),
        (">1.0.0", ">1.0.0"),
        ("!=1.2.3", "!=1.2.3"),
        ("==1.2.3", "==1.2.3"),
        # A bare version means exact equality, and renders with the operator made
        # explicit so a reader never has to know that rule.
        ("1.2.3", "==1.2.3"),
        # Whitespace around comparators is tolerated on input.
        (">=2.1, <3", ">=2.1.0,<3.0.0"),
    ],
)
def test_parse_render(raw: str, expected: str) -> None:
    assert VersionRange.parse(raw).render() == expected


@pytest.mark.parametrize("raw", [">=2.1,<3", "1.2.3", "!=1.0.0", ">=1.0.0-rc.1,<2"])
def test_rendered_ranges_reparse_identically(raw: str) -> None:
    once = VersionRange.parse(raw)

    assert VersionRange.parse(once.render()) == once


def test_operators_are_parsed_longest_first() -> None:
    """`>=2.1` must not read as `>` followed by the version `=2.1`."""
    parsed = VersionRange.parse(">=2.1")

    assert parsed.constraints[0].operator is ComparisonOperator.GREATER_EQUAL
    assert parsed.constraints[0].operand == _v("2.1.0")


def test_a_bare_version_defaults_to_equality() -> None:
    parsed = VersionRange.parse("1.2.3")

    assert parsed.constraints[0].operator is ComparisonOperator.EQUAL


def test_constraints_keep_the_order_written() -> None:
    parsed = VersionRange.parse("<3,>=2.1")

    assert [c.operator for c in parsed.constraints] == [
        ComparisonOperator.LESS,
        ComparisonOperator.GREATER_EQUAL,
    ]


@pytest.mark.parametrize(
    ("candidate", "matches"),
    [
        ("2.0.9", False),
        ("2.1.0", True),
        ("2.1.1", True),
        ("2.99.99", True),
        ("3.0.0", False),
        ("3.0.1", False),
        ("1.0.0", False),
    ],
)
def test_and_semantics_across_comparators(candidate: str, matches: bool) -> None:
    """`>=2.1,<3` is a conjunction: both bounds must hold."""
    assert VersionRange.parse(">=2.1,<3").contains(_v(candidate)) is matches


@pytest.mark.parametrize(
    ("range_text", "candidate", "matches"),
    [
        (">=1.0.0", "1.0.0", True),
        (">=1.0.0", "0.9.9", False),
        (">1.0.0", "1.0.0", False),
        ("<=1.0.0", "1.0.0", True),
        ("<1.0.0", "1.0.0", False),
        ("==1.0.0", "1.0.0", True),
        ("==1.0.0", "1.0.1", False),
        ("!=1.0.0", "1.0.0", False),
        ("!=1.0.0", "1.0.1", True),
    ],
)
def test_each_operator(range_text: str, candidate: str, matches: bool) -> None:
    assert VersionRange.parse(range_text).contains(_v(candidate)) is matches


def test_build_metadata_does_not_affect_matching() -> None:
    """Follows from precedence ignoring it — pinned here so it cannot regress."""
    assert VersionRange.parse("==1.0.0").contains(_v("1.0.0+build.7"))


# The prerelease opt-in rule, stated as a table because the asymmetry is the
# whole point: prereleases are reachable only where the range asked for them.
@pytest.mark.parametrize(
    ("range_text", "candidate", "matches", "why"),
    [
        (">=1.0.0", "2.0.0-alpha", False, "range names no prerelease"),
        (">=1.0.0", "1.5.0", True, "ordinary release is unaffected"),
        (">=1.0.0-rc.1", "1.0.0-rc.2", True, "same release, range opted in"),
        (">=1.0.0-rc.1", "1.0.0-rc.1", True, "the opted-in version itself"),
        (">=1.0.0-rc.1", "2.0.0-alpha", False, "opt-in does not carry to another release"),
        (">=1.0.0-rc.1", "1.0.0", True, "the release itself still matches"),
        # The gate is a property of the range, not of each comparator: the `<2`
        # names no prerelease, and requiring every comparator to opt in would
        # wrongly reject this.
        (">=1.0.0-rc.1,<2", "1.0.0-rc.2", True, "gate is evaluated range-wide"),
        (">=2.1,<3", "3.0.0-alpha", False, "upper bound prerelease stays excluded"),
    ],
)
def test_prerelease_visibility(range_text: str, candidate: str, matches: bool, why: str) -> None:
    assert VersionRange.parse(range_text).contains(_v(candidate)) is matches, why


def test_exact_builds_a_single_version_range() -> None:
    pinned = VersionRange.exact(_v("2.1.0"))

    assert pinned.render() == "==2.1.0"
    assert pinned.contains(_v("2.1.0"))
    assert not pinned.contains(_v("2.1.1"))


def test_exact_on_a_prerelease_matches_itself() -> None:
    """The range names the prerelease, so the opt-in gate lets it through."""
    pinned = VersionRange.exact(_v("1.0.0-rc.1"))

    assert pinned.contains(_v("1.0.0-rc.1"))


@pytest.mark.parametrize(
    ("raw", "expected_reason_fragment"),
    [
        ("", "is empty"),
        ("   ", "is empty"),
        (">=2.1,", "empty comparator"),
        (",<3", "empty comparator"),
        (">=", "operator but no version"),
        (">=abc", "unparseable version"),
        (">=1.2.x", "unparseable version"),
        (">=01.2.3", "leading zero"),
        ("=>1.0.0", "unparseable version"),
    ],
)
def test_invalid_ranges_are_rejected_with_a_reason(raw: str, expected_reason_fragment: str) -> None:
    with pytest.raises(InvalidVersionRangeError) as caught:
        VersionRange.parse(raw)

    assert expected_reason_fragment in caught.value.reason
    assert caught.value.raw_range == raw


def test_a_non_string_range_is_rejected_rather_than_coerced() -> None:
    with pytest.raises(InvalidVersionRangeError) as caught:
        VersionRange.parse(None)  # type: ignore[arg-type]

    assert "expected a string" in caught.value.reason


def test_range_errors_quote_the_whole_range_not_the_fragment() -> None:
    """An author searching their manifest needs the text they actually typed."""
    with pytest.raises(InvalidVersionRangeError) as caught:
        VersionRange.parse(">=2.1,<oops")

    assert caught.value.raw_range == ">=2.1,<oops"
    assert "'>=2.1,<oops'" in str(caught.value)


def test_the_underlying_version_defect_is_preserved_in_the_reason() -> None:
    """Re-typing the error must not throw away which defect it was."""
    with pytest.raises(InvalidVersionRangeError) as caught:
        VersionRange.parse(">=01.2.3")

    assert "leading zero" in caught.value.reason


def test_constraint_renders_with_an_explicit_operator() -> None:
    constraint = VersionConstraint.parse("2.1", "2.1")

    assert constraint.render() == "==2.1.0"


def test_ranges_are_immutable() -> None:
    parsed = VersionRange.parse(">=1.0.0")

    with pytest.raises(AttributeError):
        parsed.constraints = ()  # type: ignore[misc]
