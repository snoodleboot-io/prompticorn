"""Translating the package's PEP 440 version into semver (PRO-108).

The two schemes are close enough to look interchangeable and different enough to
break. `prompticorn`'s distribution version is PEP 440 by necessity — PyPI
requires it, and `.github/scripts/calculate_version.py` says so in its own
comment — while :class:`~prompticorn.artifact.artifact_id.ArtifactId` requires
semver 2.0.0.

Feeding the raw package version to `ArtifactId` fails on every local install
(`0.0.0.dev0`), every feature-branch build (`0.5.0.dev1754…`), and every TestPyPI
preview, while passing on `main`. Translating at this boundary keeps both sides
strict instead of loosening either.

The mapping preserves ordering, which is the property that actually matters: a
`.devN` build sorts below its release in PEP 440, and `-dev.N` sorts below it in
semver, because both treat it as a pre-release.

One combination has **no** order-preserving mapping and is rejected rather than
translated: a dev build *of* a pre-release, `1.2.3rc1.dev5`. PEP 440 sorts it
below `1.2.3rc1`, but semver's "a larger set of prerelease fields outranks a
smaller one" sorts `1.2.3-rc.1.dev.5` *above* `1.2.3-rc.1` — the inverse. Every
suffix-based encoding hits this, and the alternatives (borrowing `rc.0`) collide
with real pre-releases. Since these versions feed lockfile pins, a loud rejection
beats a silent inversion. This project's version calculator never emits the form.
"""

from __future__ import annotations

import re

from prompticorn.artifact.errors import InvalidSemanticVersionError
from prompticorn.artifact.semantic_version import SemanticVersion

# The subset of PEP 440 this project actually produces: a release segment, an
# optional pre-release marker, and an optional `.devN`. Epochs, post-releases and
# local versions are deliberately unhandled — see `_UNSUPPORTED` below.
_PEP440_RE = re.compile(
    r"^(?P<release>\d+(?:\.\d+)*)"
    r"(?:(?P<pre_label>a|b|rc)(?P<pre_number>\d+))?"
    r"(?:\.dev(?P<dev>\d+))?$"
)

# PEP 440 spellings mapped to the semver identifiers they correspond to.
_PRE_LABELS = {"a": "alpha", "b": "beta", "rc": "rc"}

_DEV_LABEL = "dev"
_CORE_COMPONENTS = 3


def to_semantic_version(pep440_version: str) -> SemanticVersion:
    """Translate a PEP 440 version string into a semver version.

    ``0.5.0`` stays ``0.5.0``; ``0.5.0.dev1754`` becomes ``0.5.0-dev.1754``;
    ``1.2.3rc1`` becomes ``1.2.3-rc.1``.

    A release segment shorter than three components is padded with zeros, since
    PEP 440 treats ``1.2`` and ``1.2.0`` as the same release.

    Args:
        pep440_version: The distribution version.

    Returns:
        The equivalent semver version.

    Raises:
        InvalidSemanticVersionError: If the input is outside the supported
            subset. Raised rather than guessed at: a version that silently
            translates wrongly would pin a lockfile to the wrong release.
    """
    if not isinstance(pep440_version, str):
        raise InvalidSemanticVersionError(
            str(pep440_version), f"expected a string, got {type(pep440_version).__name__}"
        )

    text = pep440_version.strip()
    if not text:
        raise InvalidSemanticVersionError(pep440_version, "is empty")

    match = _PEP440_RE.match(text)
    if match is None:
        raise InvalidSemanticVersionError(
            pep440_version,
            "is not a PEP 440 version this project produces; expected "
            "release[aN|bN|rcN][.devN] (epochs, post-releases and local versions "
            "are not supported)",
        )

    numbers = [int(part) for part in match.group("release").split(".")]
    if len(numbers) > _CORE_COMPONENTS:
        raise InvalidSemanticVersionError(
            pep440_version,
            f"has {len(numbers)} release components; semver allows at most "
            f"{_CORE_COMPONENTS} (major.minor.patch)",
        )
    numbers += [0] * (_CORE_COMPONENTS - len(numbers))

    return SemanticVersion(
        major=numbers[0],
        minor=numbers[1],
        patch=numbers[2],
        prerelease=_prerelease_identifiers(pep440_version, match),
    )


def _prerelease_identifiers(raw_version: str, match: re.Match[str]) -> tuple[str, ...]:
    """Build the semver prerelease tuple from the PEP 440 suffixes.

    Each marker alone maps cleanly and preserves order. Their *combination* does
    not, and is refused — see the module docstring.

    Raises:
        InvalidSemanticVersionError: For a dev build of a pre-release.
    """
    pre_label = match.group("pre_label")
    dev = match.group("dev")

    if pre_label is not None and dev is not None:
        raise InvalidSemanticVersionError(
            raw_version,
            "is a dev build of a pre-release; PEP 440 sorts it below the "
            "pre-release while semver would sort it above, so there is no "
            "order-preserving translation",
        )

    if pre_label is not None:
        return (_PRE_LABELS[pre_label], match.group("pre_number"))
    if dev is not None:
        return (_DEV_LABEL, dev)
    return ()


def bundled_version() -> SemanticVersion:
    """The version bundled content is published under.

    Read from :mod:`prompticorn.__about__` at call time rather than import time,
    so a test that patches the package version is actually honoured.
    """
    from prompticorn.__about__ import __version__

    return to_semantic_version(__version__)
