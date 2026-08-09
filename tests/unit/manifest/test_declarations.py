"""The declaration value objects themselves (PRO-109).

`ManifestSchema` exercises parsing and rejection in bulk; this covers the parts
of the declaration API a caller touches directly, and the delegation boundary —
these types wrap the artifact module's grammar rather than restating it.
"""

import pytest

from prompticorn.artifact import ArtifactRequirement, VersionRange
from prompticorn.manifest import ArtifactDeclaration, ManifestSchemaError, SourceDeclaration
from prompticorn.manifest.source_type import SourceType


def test_an_artifact_declaration_wraps_a_requirement() -> None:
    """The manifest declares a *range*; the lock records the exact version."""
    declaration = ArtifactDeclaration.parse(
        {"name": "acme/sec", "version": ">=2.1,<3"}, "artifacts[0]"
    )

    assert isinstance(declaration.requirement, ArtifactRequirement)
    assert declaration.requirement.version_range == VersionRange.parse(">=2.1,<3")


def test_name_exposes_the_qualified_coordinate() -> None:
    declaration = ArtifactDeclaration.parse({"name": "sec", "version": "==1.0.0"}, "artifacts[0]")

    assert declaration.name == "local/sec"


def test_source_defaults_to_none() -> None:
    declaration = ArtifactDeclaration.parse({"name": "sec", "version": "==1.0.0"}, "artifacts[0]")

    assert declaration.source is None


def test_an_explicit_null_source_is_absent_not_an_error() -> None:
    """YAML authors write `source:` with no value to mean "unset"."""
    declaration = ArtifactDeclaration.parse(
        {"name": "sec", "version": "==1.0.0", "source": None}, "artifacts[0]"
    )

    assert declaration.source is None


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ({"name": "sec", "version": ">=2.1,<3"}, "local/sec@>=2.1.0,<3.0.0"),
        (
            {"name": "acme/sec", "version": "==1.0.0", "source": "acme-internal"},
            "acme/sec@==1.0.0 from acme-internal",
        ),
    ],
)
def test_str_is_readable(raw: dict, expected: str) -> None:
    assert str(ArtifactDeclaration.parse(raw, "artifacts[0]")) == expected


def test_declarations_are_immutable() -> None:
    declaration = ArtifactDeclaration.parse({"name": "sec", "version": "==1.0.0"}, "artifacts[0]")

    with pytest.raises(AttributeError):
        declaration.source = "other"  # type: ignore[misc]


def test_a_bad_range_is_blamed_on_the_version_key() -> None:
    """The artifact module's error is phrased for a requirement string.

    A manifest author is holding two YAML keys, so it must be re-pointed at
    whichever one is actually at fault.
    """
    with pytest.raises(ManifestSchemaError) as caught:
        ArtifactDeclaration.parse({"name": "sec", "version": ">=oops"}, "artifacts[3]")

    assert caught.value.key_path == "artifacts[3].version"


def test_a_bad_coordinate_is_blamed_on_the_name_key() -> None:
    with pytest.raises(ManifestSchemaError) as caught:
        ArtifactDeclaration.parse({"name": "Bad Name", "version": "==1.0.0"}, "artifacts[3]")

    assert caught.value.key_path == "artifacts[3].name"


def test_the_underlying_reason_is_preserved_not_discarded() -> None:
    """Re-typing an error must not throw away which defect it was."""
    with pytest.raises(ManifestSchemaError) as caught:
        ArtifactDeclaration.parse({"name": "sec", "version": ">=01.2.3"}, "artifacts[0]")

    assert "leading zero" in caught.value.reason


def test_a_source_declaration_parses() -> None:
    declaration = SourceDeclaration.parse({"name": "acme", "type": "builtin"}, "sources[0]")

    assert declaration.name == "acme"
    assert declaration.type is SourceType.BUILTIN


def test_source_type_lists_what_is_legal() -> None:
    """The message has to name the alternatives; the enum is the only source of them."""
    assert SourceType.known() == "builtin"

    with pytest.raises(ManifestSchemaError) as caught:
        SourceDeclaration.parse({"name": "acme", "type": "svn"}, "sources[0]")

    assert SourceType.known() in caught.value.reason
