"""A deprecated persona id must keep resolving while it stops being offered.

``software_engineer`` was an exact duplicate of ``fullstack_software_engineer``
— same agents, workflows and skills — carrying the description "Alias for
Fullstack Software Engineer - deprecated". It was still the first thing the
interactive picker offered, under the most inviting name on the list
("Software Engineer (Fullstack)"), so the deprecated id kept being chosen.

Deleting the key is not available as a fix. It is live in real configs,
including this repository's own, and the failure mode is silent rather than
loud: ``PersonaFilter`` raises ``KeyError`` on an unknown persona, but
``prompt_builder`` catches broadly around persona filtering and falls back to
building *every* agent. A deleted key would turn a deprecation into a config
that quietly emits the whole library.

So the alias resolves at load time instead, and these tests pin both halves of
that: resolution (it still builds, identically) and withdrawal (it is no longer
selectable).

Reference: PRO-159
"""

import warnings
from pathlib import Path

import pytest
import yaml

from prompticorn.builders.template_handlers.primary_agents_handler import PrimaryAgentsHandler
from prompticorn.personas.registry import (
    DeprecatedPersonaWarning,
    PersonaFilter,
    PersonaRegistry,
)
from prompticorn.prompt_builder import get_prompt_builder
from tests.golden_corpus import manifest

ALIAS = "software_engineer"
CANONICAL = "fullstack_software_engineer"
PERSONAS_YAML = Path("prompticorn/personas/personas.yaml")


@pytest.fixture
def registry():
    """Registry over the shipped personas.yaml, not a synthetic stand-in.

    The alias is a property of the shipped data, so a hand-built fixture would
    assert the mechanism while leaving the actual declaration unchecked.
    """
    return PersonaRegistry.from_yaml(PERSONAS_YAML)


@pytest.fixture
def personas_data():
    with PERSONAS_YAML.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_the_alias_is_declared_as_one_in_the_yaml(personas_data):
    """The declaration is data, not a hard-coded pair in the registry."""
    aliases = personas_data.get("deprecated_aliases") or {}
    assert aliases.get(ALIAS) == CANONICAL


def test_every_declared_alias_points_at_a_persona_that_exists(personas_data):
    """An alias to nothing would resolve to nothing and filter nothing."""
    aliases = personas_data.get("deprecated_aliases") or {}
    dangling = sorted(
        f"{alias} -> {target}"
        for alias, target in aliases.items()
        if target not in personas_data["personas"]
    )
    assert not dangling, f"aliases pointing at undefined personas: {dangling}"


def test_a_surviving_alias_definition_does_not_drift_from_its_target(personas_data):
    """The duplicate block is dead data, and must stay an honest duplicate.

    Nothing reads it — resolution happens first — but while it is still in the
    file a reader comparing the two blocks must not find two different answers
    for the same role. Passing vacuously once the block is deleted is the
    intended end state, not a gap.
    """
    drifted = []
    for alias, target in (personas_data.get("deprecated_aliases") or {}).items():
        block = personas_data["personas"].get(alias)
        if block is None:
            continue
        canonical = personas_data["personas"][target]
        drifted += [
            f"{alias}.{key}"
            for key in ("primary_agents", "secondary_agents", "workflows", "skills")
            if block.get(key) != canonical.get(key)
        ]

    assert not drifted, f"alias definitions that no longer match their target: {drifted}"


def test_the_alias_resolves_to_the_canonical_id(registry):
    with pytest.warns(DeprecatedPersonaWarning):
        assert registry.resolve_persona(ALIAS) == CANONICAL


def test_a_canonical_id_resolves_to_itself_without_a_warning(registry):
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecatedPersonaWarning)
        assert registry.resolve_persona(CANONICAL) == CANONICAL


def test_the_alias_enables_exactly_what_the_canonical_id_enables(registry):
    """The selection is canonicalized, so nothing downstream sees the alias."""
    with pytest.warns(DeprecatedPersonaWarning):
        aliased = PersonaFilter(registry, [ALIAS])
    canonical = PersonaFilter(registry, [CANONICAL])

    assert aliased.get_enabled_agents() == canonical.get_enabled_agents()
    assert aliased.get_enabled_workflows() == canonical.get_enabled_workflows()
    assert aliased.get_enabled_skills() == canonical.get_enabled_skills()
    assert aliased.get_selected_personas() == [CANONICAL]


def test_selecting_both_the_alias_and_its_target_is_one_persona(registry):
    """A config mid-migration may name both; that is not two selections."""
    with pytest.warns(DeprecatedPersonaWarning):
        pfilter = PersonaFilter(registry, [ALIAS, CANONICAL])
    assert pfilter.get_selected_personas() == [CANONICAL]


def test_the_alias_is_not_offered_for_selection(registry):
    """``list_personas`` feeds the init and swap pickers."""
    assert ALIAS not in registry.list_personas()
    assert CANONICAL in registry.list_personas()


def test_the_alias_is_still_an_accepted_configuration_value(registry):
    """Hidden from the picker is not the same as rejected from a config."""
    assert ALIAS in registry.list_resolvable_personas()
    assert set(registry.list_personas()).issubset(set(registry.list_resolvable_personas()))


def test_the_alias_reports_the_canonical_display_name(registry):
    """An alias must never render under its own old label."""
    with pytest.warns(DeprecatedPersonaWarning):
        assert registry.get_display_name(ALIAS) == "Fullstack Software Engineer"


def test_an_unknown_persona_is_still_rejected(registry):
    """Resolution must not turn a typo into a silent full build."""
    with pytest.raises(KeyError, match="Invalid persona"):
        PersonaFilter(registry, ["not_a_persona"])


def test_resolution_survives_the_definition_being_deleted():
    """The next release drops the duplicate block; resolution must outlive it.

    This is the whole point of declaring the alias separately from the persona
    it points at: when the deprecated definition goes, a stale config keeps
    building the right thing instead of falling into the catch-all that emits
    every agent.
    """
    data = {
        "universal_agents": ["ask"],
        "personas": {
            CANONICAL: {
                "display_name": "Fullstack Software Engineer",
                "primary_agents": ["code"],
                "secondary_agents": ["review"],
            }
        },
        "deprecated_aliases": {ALIAS: CANONICAL},
    }
    reg = PersonaRegistry(data)

    with pytest.warns(DeprecatedPersonaWarning):
        pfilter = PersonaFilter(reg, [ALIAS])

    assert pfilter.get_enabled_agents() == {"ask", "code", "review"}
    assert reg.list_personas() == [CANONICAL]
    assert ALIAS in reg.list_resolvable_personas()


def test_an_alias_to_an_undefined_persona_is_ignored_rather_than_obeyed():
    """A broken declaration must not make a working persona unreachable."""
    data = {
        "personas": {"engineer": {"primary_agents": ["code"]}},
        "deprecated_aliases": {"engineer": "typo_target"},
    }
    reg = PersonaRegistry(data)

    assert reg.resolve_persona("engineer") == "engineer"
    assert reg.list_personas() == ["engineer"]


def test_the_warning_fires_once_and_names_both_ids(registry):
    """Resolution happens on every lookup; the reader needs telling once."""
    with pytest.warns(DeprecatedPersonaWarning) as recorded:
        for _ in range(3):
            registry.resolve_persona(ALIAS)
            registry.get_display_name(ALIAS)
            registry.get_agents_for_persona(ALIAS)

    assert len(recorded) == 1
    message = str(recorded[0].message)
    assert ALIAS in message
    assert CANONICAL in message


def test_the_warning_names_the_config_file_when_the_caller_knows_it(registry, tmp_path):
    """``active_personas`` arrives as a bare list, so provenance is passed in."""
    config_file = tmp_path / ".prompticorn.yaml"

    with pytest.warns(DeprecatedPersonaWarning) as recorded:
        PersonaFilter(registry, [ALIAS], source=config_file)

    assert str(config_file) in str(recorded[0].message)


def test_the_warning_omits_a_file_it_cannot_name(registry):
    """Naming a file that has nothing to do with the value is worse than silence."""
    with pytest.warns(DeprecatedPersonaWarning) as recorded:
        PersonaFilter(registry, [ALIAS])

    assert ".prompticorn.yaml" not in str(recorded[0].message)


def test_the_primary_agents_handler_resolves_the_alias():
    """It loads personas.yaml by path and swallows every failure (returning None,
    which falls back to mode-based selection), so a broken alias here would be
    invisible."""
    with pytest.warns(DeprecatedPersonaWarning):
        aliased = PrimaryAgentsHandler._enabled_agent_names({"active_personas": [ALIAS]})

    assert aliased is not None
    assert aliased == PrimaryAgentsHandler._enabled_agent_names({"active_personas": [CANONICAL]})


def _build(root: Path, personas: list[str], tool: str) -> dict[str, str]:
    """Build one config into ``root`` and hash every emitted file.

    The deprecation warning is suppressed rather than asserted here: it has its
    own tests, and swallowing the build inside ``pytest.warns`` would let a
    missing warning mask the content comparison that is the point of this one.
    """
    root.mkdir(parents=True, exist_ok=True)
    config = {
        "spec": {"language": "python"},
        "variant": "minimal",
        "active_personas": personas,
    }
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecatedPersonaWarning)
        get_prompt_builder(tool).build(root, config, dry_run=False)
    return manifest(root)


@pytest.mark.parametrize("tool", ["claude", "kilo-ide"])
def test_a_config_using_the_alias_emits_what_the_canonical_id_emits(tmp_path, tool):
    """Byte-for-byte, not just the same agent names.

    The CLAUDE.md header is the part the obvious implementation gets wrong: a
    resolved alias that still reports its own display name stamps "Software
    Engineer (Fullstack)" into the generated document, so the two configs would
    agree on every path and still differ in content.
    """
    aliased = _build(tmp_path / "aliased", [ALIAS], tool)
    canonical = _build(tmp_path / "canonical", [CANONICAL], tool)

    assert sorted(aliased) == sorted(canonical)
    assert aliased == canonical
