"""Registry and discovery surface artifact identities (PRO-108).

AC 4 is the one with teeth here: identity is *additive*. Every pre-existing
name-keyed lookup must behave exactly as it did before, or this ticket has
broken the thing it was meant to annotate.
"""

import pytest

from prompticorn.agent_registry import Registry
from prompticorn.agent_registry.discovery import RegistryDiscovery
from prompticorn.agent_registry.errors import AgentNotFoundError
from prompticorn.artifact import ArtifactId, BundledIdentity
from prompticorn.artifact import SemanticVersion as Version


@pytest.fixture
def registry() -> Registry:
    """Registry over bundled content, pinned to a fixed artifact version."""
    return Registry(
        RegistryDiscovery.from_resolver().discover(),
        identity=BundledIdentity(version=Version.parse("1.2.3")),
    )


def test_every_agent_has_an_identity(registry: Registry) -> None:
    """AC 1, for the half of the tree the registry owns."""
    names = registry.list_agents(include_subagents=True)

    assert len(names) > 10, "sweep must actually cover the registry"
    for name in names:
        assert isinstance(registry.artifact_id(name), ArtifactId)


def test_agent_and_subagent_identities(registry: Registry) -> None:
    assert registry.artifact_id("code").render() == "local/agent.code@1.2.3"
    assert (
        registry.artifact_id("code/boilerplate").render() == "local/subagent.code.boilerplate@1.2.3"
    )


def test_identity_is_stable_across_calls(registry: Registry) -> None:
    """AC 2: unchanged content, unchanged identity."""
    assert registry.artifact_id("code") == registry.artifact_id("code")


def test_artifact_ids_covers_every_key_and_is_sorted(registry: Registry) -> None:
    identities = registry.artifact_ids()

    assert set(identities) == set(registry.list_agents(include_subagents=True))
    assert list(identities) == sorted(identities)


def test_an_unknown_key_has_no_identity(registry: Registry) -> None:
    """Deriving one would invent an artifact that was never discovered."""
    with pytest.raises(AgentNotFoundError):
        registry.artifact_id("no-such-agent")


def test_identities_are_unique_across_the_registry(registry: Registry) -> None:
    """Two agents sharing an identity would make a lock entry ambiguous."""
    identities = registry.artifact_ids()

    assert len({a.render() for a in identities.values()}) == len(identities)


def test_the_version_is_injectable() -> None:
    """So a test never depends on the distribution version of the moment."""
    registry = Registry(
        RegistryDiscovery.from_resolver().discover(),
        identity=BundledIdentity(version=Version.parse("9.9.9")),
    )

    assert registry.artifact_id("code").version == Version.parse("9.9.9")


def test_discovery_surfaces_identity_too() -> None:
    """AC names RegistryDiscovery alongside Registry."""
    discovery = RegistryDiscovery.from_resolver()

    assert discovery.artifact_id("code").name == "agent.code"


def test_resolver_discovery_sets_identity_despite_bypassing_init() -> None:
    """`from_resolver` builds via __new__, so a missed field is an AttributeError."""
    assert isinstance(RegistryDiscovery.from_resolver().artifact_id("code"), ArtifactId)


# ── AC 4: existing behaviour is untouched ──────────────────────────────────────


def test_name_keyed_lookups_are_unchanged(registry: Registry) -> None:
    agent = registry.get_agent("code")

    assert agent.name
    assert registry.has_agent("code")
    assert not registry.has_agent("no-such-agent")


def test_listing_is_unchanged(registry: Registry) -> None:
    top_level = registry.list_agents()

    assert "code" in top_level
    assert all("/" not in name for name in top_level)
    assert "code/boilerplate" in registry.list_agents(include_subagents=True)


def test_subagent_listing_is_unchanged(registry: Registry) -> None:
    assert "boilerplate" in registry.list_subagents("code")


def test_a_registry_built_without_an_identity_still_works() -> None:
    """The new parameter is optional; every existing construction site is fine."""
    registry = Registry(RegistryDiscovery.from_resolver().discover())

    assert registry.has_agent("code")
    assert registry.artifact_id("code").namespace == "local"


def test_agents_carry_no_identity_field() -> None:
    """Identity sits beside the IR model, never inside it.

    Adding a field to the Agent model would change generated output and move the
    golden corpus — for a ticket that emits nothing.
    """
    from prompticorn.ir.models import Agent

    assert "artifact_id" not in Agent.model_fields
