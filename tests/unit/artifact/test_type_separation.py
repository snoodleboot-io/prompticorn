"""`ArtifactId` and `UnitId` are not interchangeable (PRO-107 acceptance criterion).

The two are structurally similar — both are frozen value objects with
``parse``/``render`` and a lowercase-token grammar — which is precisely why the
boundary needs a test rather than a convention. They answer different questions:

- ``ArtifactId`` — *which release*: ``local/acme-sec@2.1.0``
- ``UnitId`` — *where the bytes live inside it*: ``agent/architect/minimal``

An artifact contains one or more units. Conflating them would collapse "version
the ACME security agent as a unit of release" into "version each variant
separately", which is the thing the artifact model exists to avoid.

The signature sweeps below are deliberately structural: they fail when someone
*adds* a signature crossing the boundary, not only when an existing one changes.
"""

import inspect
from types import ModuleType
from typing import Iterator

import pytest

import prompticorn.artifact as artifact_package
import prompticorn.content as content_package
from prompticorn.artifact import (
    ArtifactId,
    ArtifactRequirement,
    InvalidArtifactIdError,
    SemanticVersion,
)
from prompticorn.content import InvalidUnitIdError, UnitId


def _public_signatures(module: ModuleType) -> Iterator[tuple[str, str]]:
    """Yield ``(label, text)`` for every public signature the package exports.

    Covers module-level callables, class methods, properties, and dataclass
    field annotations — every place a type can appear in a public API. Reads
    annotations as text because ``from __future__ import annotations`` leaves
    them unresolved, which suits us: we want to know whether the *name* is
    mentioned at all.
    """
    for exported_name in module.__all__:
        exported = getattr(module, exported_name)

        if inspect.isfunction(exported):
            yield f"{module.__name__}.{exported_name}", str(inspect.signature(exported))
            continue

        if not inspect.isclass(exported):
            continue

        for field_name, annotation in getattr(exported, "__annotations__", {}).items():
            yield f"{exported_name}.{field_name}", str(annotation)

        for attribute_name in vars(exported):
            if attribute_name.startswith("_"):
                continue
            attribute = getattr(exported, attribute_name, None)
            if isinstance(attribute, property):
                attribute = attribute.fget
            if not callable(attribute):
                continue
            label = f"{exported_name}.{attribute_name}"
            yield label, str(inspect.signature(attribute))


# The single sanctioned translation boundary. `BundledIdentity` exists to map a
# UnitId to the ArtifactId of the artifact containing it (PRO-108), so it must
# name both types. That is the opposite of conflation — a converter proves the
# two are distinct — but it has to be declared, not silently tolerated.
_UNIT_ID_TRANSLATION_BOUNDARY = "BundledIdentity"


def test_no_artifact_signature_mentions_unit_id_outside_the_translation_boundary() -> None:
    offenders = [
        f"{label}{text}"
        for label, text in _public_signatures(artifact_package)
        if "UnitId" in text and not label.startswith(_UNIT_ID_TRANSLATION_BOUNDARY)
    ]

    assert offenders == []


def test_the_translation_boundary_exemption_is_actually_used() -> None:
    """Guards against the exemption quietly becoming dead and hiding a new leak."""
    boundary_signatures = [
        label
        for label, text in _public_signatures(artifact_package)
        if "UnitId" in text and label.startswith(_UNIT_ID_TRANSLATION_BOUNDARY)
    ]

    assert boundary_signatures != []


def test_no_signature_accepts_either_type_interchangeably() -> None:
    """The actual acceptance criterion: neither type substitutes for the other.

    Converting between them is fine; a parameter that would swallow *either* is
    not, because that is the signature under which a caller can pass the wrong
    one and never learn.
    """
    offenders = [
        f"{label}{text}"
        for module in (artifact_package, content_package)
        for label, text in _public_signatures(module)
        if "ArtifactId" in text and "UnitId" in text and "|" in text
    ]

    assert offenders == []


def test_no_content_signature_mentions_artifact_id() -> None:
    offenders = [
        f"{label}{text}"
        for label, text in _public_signatures(content_package)
        if "ArtifactId" in text
    ]

    assert offenders == []


def test_the_sweep_actually_inspects_something() -> None:
    """A sweep that silently found nothing would pass the two tests above."""
    artifact_signatures = list(_public_signatures(artifact_package))
    content_signatures = list(_public_signatures(content_package))

    assert len(artifact_signatures) > 10
    assert len(content_signatures) > 5
    assert any("ArtifactId" in text for _, text in artifact_signatures)
    assert any("UnitId" in text for _, text in content_signatures)


def test_neither_type_is_a_subclass_of_the_other() -> None:
    assert not issubclass(ArtifactId, UnitId)
    assert not issubclass(UnitId, ArtifactId)


def test_they_share_no_base_class_beyond_object() -> None:
    """A shared base would let a signature accept either one."""
    assert set(ArtifactId.__mro__) & set(UnitId.__mro__) == {object}


def test_the_two_packages_export_disjoint_identity_types() -> None:
    assert "ArtifactId" not in content_package.__all__
    assert "UnitId" not in artifact_package.__all__


def test_instances_never_compare_equal() -> None:
    """Even at their most similar, they are different things."""
    assert ArtifactId.parse("agent@1.0.0") != UnitId.parse("agent/code")
    assert UnitId.parse("agent/code") != ArtifactId.parse("agent@1.0.0")


def test_a_unit_id_is_not_accepted_where_an_artifact_id_belongs() -> None:
    requirement = ArtifactRequirement.parse("acme/sec@>=2.1,<3")

    with pytest.raises(AttributeError):
        requirement.matches(UnitId.parse("agent/code"))  # type: ignore[arg-type]


def test_neither_parser_accepts_the_other_grammar() -> None:
    """The grammars do not overlap, so a mix-up cannot pass silently.

    Each parser must reject with *its own* error type — a bare ``Exception``
    here would pass even if the rejection came from the wrong module.
    """
    with pytest.raises(InvalidArtifactIdError):
        ArtifactId.parse("agent/architect/minimal")

    with pytest.raises(InvalidUnitIdError):
        UnitId.parse("local/acme-sec@2.1.0")


def test_the_versioned_thing_is_the_artifact_not_the_unit() -> None:
    """One release identity spans many addressable units — the model's whole point."""
    release = ArtifactId.local("acme-sec", SemanticVersion.parse("2.1.0"))
    units = [UnitId.parse("agent/code"), UnitId.parse("skill/threat-modeling/minimal")]

    assert release.version == SemanticVersion.parse("2.1.0")
    assert not any(hasattr(unit, "version") for unit in units)
