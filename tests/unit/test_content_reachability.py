"""Shipped content must be reachable by some agent or language.

A workflow directory with no mapping entry can never be emitted: not by any
agent, any language, or any persona. It is dead weight in the wheel and a
trap for anyone who edits it expecting an effect. 33 workflows had
accumulated that way before PRO-157.

Reference: PRO-157
"""

from pathlib import Path

import pytest
import yaml

CONTENT_ROOT = Path("prompticorn")
CONFIGURATIONS = CONTENT_ROOT / "configurations"


def _load(name):
    with (CONFIGURATIONS / name).open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@pytest.fixture(scope="module")
def mappings():
    return _load("agent_skill_mapping.yaml"), _load("language_skill_mapping.yaml")


def _mapped(mappings, key):
    """Every name reachable through either mapping, for one of skills/workflows."""
    agent_map, language_map = mappings
    names = {n for entry in agent_map.values() for n in (entry.get(key) or [])}
    names |= {
        n
        for entry in language_map.values()
        if isinstance(entry, dict)
        for n in (entry.get(key) or [])
    }
    return names


def _on_disk(directory):
    return {p.name for p in sorted((CONTENT_ROOT / directory).iterdir()) if p.is_dir()}


@pytest.mark.parametrize(("key", "directory"), [("workflows", "workflows"), ("skills", "skills")])
def test_everything_shipped_is_reachable(mappings, key, directory):
    unreachable = sorted(_on_disk(directory) - _mapped(mappings, key))
    assert not unreachable, (
        f"{len(unreachable)} {key} ship but no agent or language maps them, "
        f"so nothing can ever emit them: {unreachable}"
    )


@pytest.mark.parametrize(("key", "directory"), [("workflows", "workflows"), ("skills", "skills")])
def test_no_mapping_points_at_missing_content(mappings, key, directory):
    """The inverse failure: a mapping entry naming content that does not exist."""
    dangling = sorted(_mapped(mappings, key) - _on_disk(directory))
    assert not dangling, f"{key} mapped but absent from disk: {dangling}"


def test_every_agent_directory_has_a_mapping_entry(mappings):
    agent_map, _ = mappings
    shipped = _on_disk("agents") - {"core"}  # core holds conventions, not an agent
    unmapped = sorted(shipped - set(agent_map))
    assert not unmapped, f"agents with no skill/workflow mapping: {unmapped}"
