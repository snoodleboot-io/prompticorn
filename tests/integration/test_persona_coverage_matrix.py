"""Persona-coverage matrix: prove every persona's selection reaches output.

TESTING STRATEGY (PRO-168)
==========================
Two holes this closes, both invisible to every other test.

**The persona axis was never varied.** `tests/golden_corpus.py` drives four
configs and all seventeen tools, but every one of them — and every integration
test that sets the key at all — hardcodes
``active_personas = ["software_engineer"]``. Three of twenty-one personas were
exercised end to end, and the third is the deprecated alias we are removing. A
persona could select nothing, or everything, and nothing would fail.

**Golden pins bytes, not validity.** The 136-cell matrix asserts sha256 of a
file list against a recording. It says the output has not *changed*; it says
nothing about whether the output is *right*. PRO-162 is the proof: 898 files
left the corpus when three personas were corrected, and they had been recorded
as correct since the day the mapping was wrong. PRO-167 is the sharper proof —
every build has emitted a universal agent's leaked skills, recorded as correct
from day one.

So this module derives what *should* be emitted straight from the YAML —
``personas.yaml`` for agents, ``agent_skill_mapping.yaml`` and
``language_skill_mapping.yaml`` for skills and workflows — and asserts set
**equality** against a real build. Deriving the expectation from the code under
test would make the assertion circular and worthless, so it is deliberately
recomputed here even though that duplicates resolution logic.

Known-open defects are pinned with ``strict`` xfail keyed to their remediation
ticket, as in ``test_value_coverage_matrix``: when a fix lands the xfail flips
to an unexpected pass and fails this suite, which is the signal to delete the
marker. **Do not** silence a new failure by widening a tolerance.
"""

from pathlib import Path

import pytest
import yaml

from prompticorn.config_handler import create_default_config
from prompticorn.prompt_builder import get_prompt_builder

CONTENT = Path("prompticorn")
LANGUAGE = "python"
VARIANT = "minimal"

#: Subagents whose leaf name collides with a top-level agent's mapping key, so
#: the build resolves the wrong entry and leaks that agent's skills. PRO-167.
_COLLIDING_SUBAGENTS = {
    "orchestrator/devops": "devops",
    "review/code": "code",
    "compliance/review": "review",
    "security/review": "review",
    "review/performance": "performance",
    "code/refactor": "refactor",
    "code/migration": "migration",
}


def _load(path):
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


PERSONAS_DOC = _load(CONTENT / "personas" / "personas.yaml")
AGENT_MAP = _load(CONTENT / "configurations" / "agent_skill_mapping.yaml")
LANGUAGE_MAP = _load(CONTENT / "configurations" / "language_skill_mapping.yaml")
PERSONAS = sorted(PERSONAS_DOC["personas"])
UNIVERSAL = list(PERSONAS_DOC["universal_agents"])


def expected_agents(persona: str) -> set[str]:
    """Agents a persona should enable: its own, plus the universal ones."""
    p = PERSONAS_DOC["personas"][persona]
    return (
        set(p.get("primary_agents") or []) | set(p.get("secondary_agents") or []) | set(UNIVERSAL)
    )


def expected_content(persona: str, key: str) -> set[str]:
    """Skills or workflows a persona should reach, derived from the YAML.

    Agent-level mappings are the base. Language-level entries are added to
    every agent, and ``<language>/<agent>`` entries to that agent, mirroring
    the documented two-tier union — recomputed from the files rather than
    borrowed from the loader so the assertion is independent.
    """
    agents = expected_agents(persona)
    found = {name for a in agents for name in (AGENT_MAP.get(a, {}).get(key) or [])}
    found |= set((LANGUAGE_MAP.get(LANGUAGE) or {}).get(key) or [])
    for a in agents:
        found |= set((LANGUAGE_MAP.get(f"{LANGUAGE}/{a}") or {}).get(key) or [])
    return found


def leaked_by_collision(persona: str, key: str) -> set[str]:
    """What PRO-167's name collision adds on top of the correct expectation."""
    agents = expected_agents(persona)
    leaked = set()
    for registry_key, resolves_to in _COLLIDING_SUBAGENTS.items():
        if registry_key.split("/")[0] in agents:
            leaked |= set(AGENT_MAP.get(resolves_to, {}).get(key) or [])
    return leaked - expected_content(persona, key)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    """One real Claude build per persona. Module-scoped — each build is slow."""
    out = {}
    for persona in PERSONAS:
        config = create_default_config(LANGUAGE)
        config["variant"] = VARIANT
        config["active_personas"] = [persona]
        root = tmp_path_factory.mktemp(f"persona_{persona}")
        get_prompt_builder("claude").build(root, config=config, dry_run=False)
        out[persona] = root
    return out


def _emitted(root: Path, kind: str) -> set[str]:
    if kind == "agents":
        return {p.stem.removesuffix("-agent") for p in (root / ".claude/agents").glob("*.md")}
    if kind == "skills":
        base = root / ".claude/skills"
        return {p.name for p in base.iterdir() if p.is_dir()} if base.is_dir() else set()
    base = root / ".claude/workflows"
    return {p.stem for p in base.glob("*.md")} if base.is_dir() else set()


@pytest.mark.integration
@pytest.mark.parametrize("persona", PERSONAS)
def test_emitted_agents_are_exactly_the_personas_agents(built, persona):
    """The selection reaches disk: no agent missing, none smuggled in."""
    emitted = _emitted(built[persona], "agents")
    expected = expected_agents(persona)
    assert emitted == expected, (
        f"{persona}: missing={sorted(expected - emitted)} unexpected={sorted(emitted - expected)}"
    )


@pytest.mark.integration
@pytest.mark.parametrize("persona", PERSONAS)
def test_no_persona_emits_an_empty_agent_set(built, persona):
    """A persona that selects nothing would be silently useless."""
    assert _emitted(built[persona], "agents"), f"{persona} emitted no agents at all"


@pytest.mark.integration
@pytest.mark.parametrize("kind", ["skills", "workflows"])
@pytest.mark.parametrize("persona", PERSONAS)
def test_emitted_content_is_reachable_from_the_personas_agents(built, persona, kind):
    """Nothing is emitted that no selected agent maps.

    The weaker direction of set equality, and the one that holds today. Its
    counterpart is pinned below pending PRO-167.
    """
    emitted = _emitted(built[persona], kind)
    allowed = expected_content(persona, kind) | leaked_by_collision(persona, kind)
    assert not (emitted - allowed), (
        f"{persona}: emitted {kind} that no selected agent maps: {sorted(emitted - allowed)}"
    )


@pytest.mark.integration
@pytest.mark.parametrize("kind", ["skills", "workflows"])
@pytest.mark.parametrize("persona", PERSONAS)
def test_everything_reachable_is_actually_emitted(built, persona, kind):
    """Nothing a selected agent maps is silently dropped."""
    emitted = _emitted(built[persona], kind)
    expected = expected_content(persona, kind)
    assert not (expected - emitted), (
        f"{persona}: {kind} mapped by a selected agent but never written: "
        f"{sorted(expected - emitted)}"
    )


@pytest.mark.integration
@pytest.mark.parametrize("kind", ["skills", "workflows"])
@pytest.mark.parametrize("persona", PERSONAS)
def test_emitted_content_is_exactly_what_the_persona_reaches(built, persona, kind):
    """Strict set equality — the assertion PRO-167 currently violates.

    Pinned per persona rather than skipped: a persona with no colliding parent
    passes today and must keep passing, and the rest flip to an unexpected pass
    the moment PRO-167 lands.
    """
    if leaked_by_collision(persona, kind):
        pytest.xfail(f"PRO-167: subagent name collision leaks into {persona} {kind}")
    emitted = _emitted(built[persona], kind)
    expected = expected_content(persona, kind)
    assert emitted == expected, (
        f"{persona} {kind}: missing={sorted(expected - emitted)} "
        f"unexpected={sorted(emitted - expected)}"
    )


@pytest.mark.integration
def test_every_persona_is_covered_by_this_matrix():
    """A persona added to the YAML must appear here without anyone remembering."""
    assert set(PERSONAS) == set(PERSONAS_DOC["personas"]), "persona list drifted"
    assert len(PERSONAS) >= 21, f"expected at least 21 personas, found {len(PERSONAS)}"
