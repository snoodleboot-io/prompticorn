"""Every persona ref must resolve to content that actually ships.

``personas.yaml`` is hand-maintained and its refs were unchecked, so three
typos sat in it undetected: a workflow that never existed
(``deployment-automation``), and two skills that were really workflow names
(``feature-prioritization-workflow``, ``feature-engineering-guide``). They were
inert only because the persona skill/workflow lists were dead data at the time.
Once those lists drive the build, a bad ref is silently dropped content.

Reference: PRO-158
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


def _refs(personas_data, key):
    """Every (persona, ref) pair for one persona key, sorted for stable output."""
    pairs = set()
    for persona_name, persona in personas_data["personas"].items():
        for ref in persona.get(key) or []:
            pairs.add((persona_name, ref))
    return sorted(pairs)


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


@pytest.mark.parametrize(
    ("key", "directory"),
    [("workflows", "workflows"), ("skills", "skills")],
)
def test_content_refs_resolve_with_both_variants(personas_data, key, directory):
    """Refs must resolve, and carry both verbosity variants.

    A directory with only ``verbose/`` builds fine until someone selects
    ``minimal``, so existence alone is not enough to assert.
    """
    missing = []
    for persona, ref in _refs(personas_data, key):
        base = CONTENT_ROOT / directory / ref
        if not base.is_dir():
            missing.append((persona, ref, "no directory"))
            continue
        absent = sorted(v for v in ("minimal", "verbose") if not (base / v).is_dir())
        if absent:
            missing.append((persona, ref, f"missing variant(s): {absent}"))

    assert not missing, f"unresolvable persona {key} refs: {missing}"


def test_a_skill_ref_is_never_really_a_workflow(personas_data):
    """The two typos that shipped were both workflow names in a skills list."""
    confused = [
        (persona, ref)
        for persona, ref in _refs(personas_data, "skills")
        if not (CONTENT_ROOT / "skills" / ref).is_dir()
        and (CONTENT_ROOT / "workflows" / ref).is_dir()
    ]
    assert not confused, f"workflow names listed as skills: {confused}"


@pytest.mark.parametrize("key", ["skills", "workflows"])
def test_persona_lists_are_reachable_from_their_own_agents(personas_data, key):
    """A persona may only narrow what its agents map — it can never add.

    Under the intersect semantics of PRO-153 a persona ref that no selected
    agent maps is not an error, it is silently dropped content. ai_engineer
    listed ``model-evaluation`` this way: the skill lives on ``mlai``, which
    that persona does not select.
    """
    with (CONTENT_ROOT / "configurations" / "agent_skill_mapping.yaml").open(
        encoding="utf-8"
    ) as f:
        agent_map = yaml.safe_load(f)

    unreachable = []
    for persona_name, persona in personas_data["personas"].items():
        agents = (persona.get("primary_agents") or []) + (persona.get("secondary_agents") or [])
        reachable = {
            ref for agent in agents for ref in (agent_map.get(agent, {}).get(key) or [])
        }
        for ref in sorted(set(persona.get(key) or []) - reachable):
            unreachable.append(f"{persona_name} -> {ref}")

    assert not unreachable, (
        f"persona {key} that no selected agent maps, so the build would drop them "
        f"without a word: {unreachable}"
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
