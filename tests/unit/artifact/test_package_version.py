"""Translating the PEP 440 package version into semver (PRO-108).

The ordering table is the load-bearing part. A translation that parses but
reorders is worse than one that fails, because it would pin a lockfile to the
wrong release without ever raising.
"""

import pytest

from prompticorn.artifact import InvalidSemanticVersionError, SemanticVersion, to_semantic_version
from prompticorn.artifact.package_version import bundled_version


@pytest.mark.parametrize(
    ("pep440", "expected"),
    [
        # Every form `.github/scripts/calculate_version.py` actually emits.
        ("0.5.0", "0.5.0"),  # release on main
        ("0.5.128", "0.5.128"),  # PR build
        ("0.5.0.dev1754160000", "0.5.0-dev.1754160000"),  # feature-branch push
        ("0.5.128.dev42", "0.5.128-dev.42"),  # TestPyPI preview
        ("0.0.0.dev0", "0.0.0-dev.0"),  # local / editable install
        # Standard PEP 440 pre-release spellings.
        ("1.2.3a1", "1.2.3-alpha.1"),
        ("1.2.3b2", "1.2.3-beta.2"),
        ("1.2.3rc1", "1.2.3-rc.1"),
        # A short release segment is the same release, zero-padded.
        ("1.2", "1.2.0"),
        ("1", "1.0.0"),
        # Surrounding whitespace is tolerated.
        (" 1.2.3 ", "1.2.3"),
    ],
)
def test_translation(pep440: str, expected: str) -> None:
    assert to_semantic_version(pep440).render() == expected


@pytest.mark.parametrize(
    ("lower", "higher", "why"),
    [
        ("0.5.0.dev1", "0.5.0.dev2", "dev builds order numerically"),
        ("0.5.0.dev999", "0.5.0", "a dev build precedes its release"),
        ("1.2.3a1", "1.2.3b1", "alpha precedes beta"),
        ("1.2.3b1", "1.2.3rc1", "beta precedes rc"),
        ("1.2.3rc1", "1.2.3", "rc precedes the release"),
        ("1.2.3", "1.2.4", "patch ordering survives"),
        ("0.5.128", "0.6.0", "minor ordering survives"),
    ],
)
def test_ordering_is_preserved(lower: str, higher: str, why: str) -> None:
    """PEP 440's ordering must survive the trip into semver."""
    assert to_semantic_version(lower) < to_semantic_version(higher), why


def test_a_dev_build_of_a_prerelease_is_refused() -> None:
    """The one combination with no order-preserving mapping.

    PEP 440 sorts `1.2.3rc1.dev5` below `1.2.3rc1`; semver's "more prerelease
    fields outrank fewer" would sort the translation above it. Refusing beats
    silently inverting, since these versions feed lockfile pins.
    """
    with pytest.raises(InvalidSemanticVersionError) as caught:
        to_semantic_version("1.2.3rc1.dev5")

    assert "dev build of a pre-release" in caught.value.reason


def test_the_refused_combination_would_indeed_have_inverted() -> None:
    """Pins *why* it is refused, so the rule cannot be dropped as over-caution."""
    naive_translation = SemanticVersion.parse("1.2.3-rc.1.dev.5")

    assert naive_translation > SemanticVersion.parse("1.2.3-rc.1")


@pytest.mark.parametrize(
    ("pep440", "expected_reason_fragment"),
    [
        ("", "is empty"),
        ("   ", "is empty"),
        ("1.2.3.4", "release components"),
        ("v1.2.3", "not a PEP 440 version"),
        ("1.2.3+local", "not a PEP 440 version"),  # local versions unsupported
        ("1!1.2.3", "not a PEP 440 version"),  # epochs unsupported
        ("1.2.3.post1", "not a PEP 440 version"),  # post-releases unsupported
        ("not-a-version", "not a PEP 440 version"),
    ],
)
def test_unsupported_forms_are_rejected(pep440: str, expected_reason_fragment: str) -> None:
    with pytest.raises(InvalidSemanticVersionError) as caught:
        to_semantic_version(pep440)

    assert expected_reason_fragment in caught.value.reason
    assert caught.value.raw_version == pep440


def test_a_non_string_is_rejected_rather_than_coerced() -> None:
    with pytest.raises(InvalidSemanticVersionError) as caught:
        to_semantic_version(None)  # type: ignore[arg-type]

    assert "expected a string" in caught.value.reason


def test_the_real_package_version_translates() -> None:
    """The regression that motivated this module.

    Feeding `__about__.__version__` straight to `ArtifactId` fails on every
    local install. Whatever the version is here, it must translate.
    """
    assert isinstance(bundled_version(), SemanticVersion)


def test_bundled_version_reads_the_package_at_call_time(monkeypatch: pytest.MonkeyPatch) -> None:
    """Import-time capture would make the version unpatchable in tests."""
    monkeypatch.setattr("prompticorn.__about__.__version__", "9.9.9")

    assert bundled_version().render() == "9.9.9"
