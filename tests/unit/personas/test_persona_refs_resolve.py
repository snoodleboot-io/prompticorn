"""Every persona agent ref must resolve to an agent that actually ships.

``personas.yaml`` is hand-maintained. It once carried per-persona skill and
workflow lists too, and three typos sat in them undetected for months —
harmless only because the build never read the lists. PRO-153 removed the
lists outright rather than wire them live: a persona selects agents, and what
those agents reach is the agent mappings' job, enforced by
``tests/unit/test_content_reachability.py`` and the persona coverage matrix.

What remains here is the agent side of that contract.

Reference: PRO-158, PRO-153
"""

from pathlib import Path

import pytest
import yaml

CONTENT_ROOT = Path("prompticorn")

#: Shared convention files (``conventions-*.md``, ``session.md``), not a
#: selectable agent. No persona may reference it.
NON_SELECTABLE_AGENTS = {"core"}


@pytest.fixture(scope="module")
def personas_data():
    with (CONTENT_ROOT / "personas" / "personas.yaml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)

def _agent_refs(personas_data):
    pairs = {
        (persona_name, ref)
        for persona_name, persona in personas_data["personas"].items()
        for key in ("primary_agents", "secondary_agents")
        for ref in persona.get(key) or []
    }
    pairs |= {("<universal>", ref) for ref in personas_data.get("universal_agents") or []}
    return sorted(pairs)


def test_agent_refs_resolve(personas_data):
    """Each referenced agent has a directory carrying a prompt."""
    missing = [
        (persona, ref)
        for persona, ref in _agent_refs(personas_data)
        if not (CONTENT_ROOT / "agents" / ref / "prompt.md").is_file()
    ]
    assert not missing, f"persona agent refs with no prompt.md: {missing}"


def test_no_persona_references_a_non_selectable_agent(personas_data):
    """``core`` holds conventions, not an agent — selecting it would emit nothing."""
    bad = [
        (persona, ref)
        for persona, ref in _agent_refs(personas_data)
        if ref in NON_SELECTABLE_AGENTS
    ]
    assert not bad, f"personas referencing non-selectable agents: {bad}"


def test_personas_differentiate_on_non_universal_agents(personas_data):
    """A persona built on universal agents selects nothing.

    Universal agents are enabled for every persona regardless of choice, so
    listing them is not a selection. `engineering_manager` shipped with `plan`
    primary and `orchestrator` secondary — both universal — leaving it
    differentiating on two agents and effectively duplicating
    product_manager + architect. (PRO-162)
    """
    universal = set(personas_data.get("universal_agents") or [])
    thin = []
    for persona_name, persona in personas_data["personas"].items():
        selected = set(persona.get("primary_agents") or []) | set(
            persona.get("secondary_agents") or []
        )
        if not selected - universal:
            thin.append(persona_name)

    assert not thin, (
        f"personas selecting only universal agents, so they narrow nothing: {thin}"
    )


def test_no_persona_lists_a_universal_agent(personas_data):
    """Listing a universal agent is misleading rather than harmful.

    It reads as a selection in the docs and the picker, but changes nothing —
    which is how the engineering_manager defect survived review.
    """
    universal = set(personas_data.get("universal_agents") or [])
    listed = [
        f"{persona_name} -> {agent}"
        for persona_name, persona in personas_data["personas"].items()
        for agent in sorted(
            (set(persona.get("primary_agents") or []) | set(persona.get("secondary_agents") or []))
            & universal
        )
    ]
    assert not listed, (
        f"personas listing universal agents, which are always enabled anyway: {listed}"
    )


def test_every_shipped_agent_is_claimed_by_some_persona(personas_data):
    """An agent no persona selects can never be emitted.

    ``qa-tester`` shipped unclaimed for exactly this reason — the persona named
    after it selected ``test``/``review``/``atdd`` instead.
    """
    claimed = {ref for _, ref in _agent_refs(personas_data)}
    shipped = {
        path.name
        for path in sorted((CONTENT_ROOT / "agents").iterdir())
        if path.is_dir() and path.name not in NON_SELECTABLE_AGENTS
    }
    assert not (shipped - claimed), f"agents no persona can select: {sorted(shipped - claimed)}"
