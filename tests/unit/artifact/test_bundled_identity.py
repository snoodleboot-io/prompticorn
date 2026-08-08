"""Artifact identities for bundled content (PRO-108).

Two properties carry this file: names are kind-qualified so distinct artifacts
cannot collide, and every variant of one artifact maps to a single identity.
The collision test runs against the real bundled tree because that is where the
problem was found — 10 names are shared across kinds.
"""

import pytest

from prompticorn.artifact import ArtifactId, BundledIdentity, InvalidArtifactIdError
from prompticorn.artifact import SemanticVersion as Version
from prompticorn.content import UnitId, UnitKind
from prompticorn.content.content_resolver import default_resolver


@pytest.fixture
def identity() -> BundledIdentity:
    """Identity pinned to a fixed version, so assertions do not move with the package."""
    return BundledIdentity(version=Version.parse("1.2.3"))


@pytest.mark.parametrize(
    ("unit", "expected"),
    [
        ("agent/code", "local/agent.code@1.2.3"),
        ("subagent/orchestrator/devops/minimal", "local/subagent.orchestrator.devops@1.2.3"),
        ("skill/threat-modeling/minimal", "local/skill.threat-modeling@1.2.3"),
        (
            "workflow/async-workflow-execution/verbose",
            "local/workflow.async-workflow-execution@1.2.3",
        ),
        ("convention/core/system", "local/convention.core.system@1.2.3"),
        ("convention/language/python", "local/convention.language.python@1.2.3"),
        ("configuration/personas", "local/configuration.personas@1.2.3"),
    ],
)
def test_identity_for_each_kind(identity: BundledIdentity, unit: str, expected: str) -> None:
    """AC 1: every kind the resolver carries gets an identity."""
    assert identity.for_unit(UnitId.parse(unit)).render() == expected


@pytest.mark.parametrize(
    ("first", "second"),
    [
        ("skill/threat-modeling/minimal", "skill/threat-modeling/verbose"),
        ("workflow/quality-assurance/minimal", "workflow/quality-assurance/verbose"),
        ("subagent/code/feature/minimal", "subagent/code/feature/verbose"),
    ],
)
def test_variants_share_one_artifact(identity: BundledIdentity, first: str, second: str) -> None:
    """The artifact is the named thing; variants are units inside it.

    This is what lets an org release one versioned artifact while the resolver
    still addresses each variant — the premise PRO-107 was built on.
    """
    assert identity.for_unit(UnitId.parse(first)) == identity.for_unit(UnitId.parse(second))


def test_names_are_kind_qualified(identity: BundledIdentity) -> None:
    """`code` is both an agent and a workflow in the bundled tree."""
    agent = identity.for_unit(UnitId.parse("agent/code"))
    workflow = identity.for_unit(UnitId.parse("workflow/code/minimal"))

    assert agent != workflow
    assert agent.name == "agent.code"
    assert workflow.name == "workflow.code"


def test_no_two_bundled_artifacts_share_an_identity() -> None:
    """The regression that forced kind-qualified names.

    Under a bare-`<name>` scheme 10 pairs collapse together — `code` as agent
    and workflow, `threat-modeling` as skill and workflow, and 8 more. Distinct
    artifacts sharing an identity is the exact conflation the model prevents.
    """
    identity = BundledIdentity(version=Version.parse("1.2.3"))
    owners: dict[str, set[str]] = {}

    for unit in default_resolver().units():
        owners.setdefault(identity.for_unit(unit.id).render(), set()).add(unit.id.render())

    collisions = {
        artifact: sorted(units)
        for artifact, units in owners.items()
        if len({u.split("/")[0] for u in units}) > 1
    }
    assert collisions == {}


def test_every_bundled_unit_yields_a_valid_identity() -> None:
    """AC 1, swept across the whole tree rather than a sample."""
    identity = BundledIdentity(version=Version.parse("1.2.3"))
    units = default_resolver().units()

    assert len(units) > 100, "sweep must actually cover the tree"
    for unit in units:
        rendered = identity.for_unit(unit.id).render()
        assert ArtifactId.parse(rendered).render() == rendered


def test_identity_is_stable_across_calls(identity: BundledIdentity) -> None:
    """AC 2: unchanged content, unchanged identity."""
    unit = UnitId.parse("agent/code")

    assert identity.for_unit(unit) == identity.for_unit(unit)


@pytest.mark.parametrize(
    ("key", "expected"),
    [
        ("code", "local/agent.code@1.2.3"),
        ("code/boilerplate", "local/subagent.code.boilerplate@1.2.3"),
    ],
)
def test_registry_keys_translate(identity: BundledIdentity, key: str, expected: str) -> None:
    assert identity.for_registry_key(key).render() == expected


def test_for_parts_matches_for_unit(identity: BundledIdentity) -> None:
    """The two entry points must not drift apart."""
    from_unit = identity.for_unit(UnitId.parse("subagent/code/feature/minimal"))
    from_parts = identity.for_parts(UnitKind.SUBAGENT, ("code", "feature"))

    assert from_unit == from_parts


def test_namespace_is_local(identity: BundledIdentity) -> None:
    assert identity.namespace == "local"
    assert identity.for_unit(UnitId.parse("agent/code")).namespace == "local"


def test_version_defaults_to_the_translated_package_version() -> None:
    from prompticorn.artifact.package_version import bundled_version

    assert BundledIdentity().version == bundled_version()


def test_an_illegal_name_is_rejected_rather_than_rendered(identity: BundledIdentity) -> None:
    """Uppercase would render an id that cannot be parsed back."""
    with pytest.raises(InvalidArtifactIdError):
        identity.for_parts(UnitKind.AGENT, ("Code",))
