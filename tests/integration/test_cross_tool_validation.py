"""Cross-tool structural invariants that hold for every supported tool (PRO-11).

The golden test pins exact bytes and the value-coverage matrix checks that spec
values render, but several regressions this project hit were *structural* and
spanned tools: Agent Skills emitted without the frontmatter Claude Code/Copilot
require, and a tool's declared ``create_artifacts`` not actually appearing on
disk. These tests assert those invariants for the whole tool set at once, so a
new tool (or a change to the shared emitter) can't silently break them.
"""

from pathlib import Path

import pytest

from prompticorn.prompt_builder import get_prompt_builder
from prompticorn.tools import TOOLS, supported_tool_ids

_ALL_TOOLS = sorted(supported_tool_ids())
_CONFIG = {"spec": {"language": "python"}, "active_personas": ["software_engineer"]}


def _build(tool: str, root: Path) -> None:
    get_prompt_builder(tool).build(root, {**_CONFIG, "variant": "minimal"}, dry_run=False)


def _parse_frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    fields: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


@pytest.mark.integration
@pytest.mark.parametrize("tool", _ALL_TOOLS)
def test_build_produces_files(tool, tmp_path):
    """Every tool writes at least one file for a normal config."""
    _build(tool, tmp_path)
    assert any(p.is_file() for p in tmp_path.rglob("*")), f"{tool} emitted no files"


@pytest.mark.integration
@pytest.mark.parametrize("tool", _ALL_TOOLS)
def test_every_emitted_skill_is_a_valid_agent_skill(tool, tmp_path):
    """Any SKILL.md a tool emits must carry name + description frontmatter.

    This is the durable guard for the regression where authored skills emitted
    without frontmatter (invisible auto-invocation) and Copilot wrote a flat
    non-conformant path — both shipped green because nothing asserted validity.
    """
    _build(tool, tmp_path)
    offenders: dict[str, str] = {}
    for skill_md in tmp_path.rglob("SKILL.md"):
        rel = skill_md.relative_to(tmp_path).as_posix()
        fm = _parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        if fm is None:
            offenders[rel] = "no YAML frontmatter"
        elif not fm.get("name"):
            offenders[rel] = "missing name"
        elif not fm.get("description"):
            offenders[rel] = "missing description"
    assert not offenders, f"{tool} emitted non-conformant Agent Skills: {offenders}"


@pytest.mark.integration
@pytest.mark.parametrize("tool", _ALL_TOOLS)
def test_declared_create_artifacts_are_produced(tool, tmp_path):
    """Every path in a tool's ``create_artifacts`` actually appears after a build.

    A declared artifact that is never created is a switch-cleanup bug: the tool
    would not be detected or cleaned up on a later ``switch``.
    """
    _build(tool, tmp_path)
    missing = [
        artifact
        for artifact in sorted(TOOLS[tool].create_artifacts)
        if not (tmp_path / artifact.rstrip("/")).exists()
    ]
    assert not missing, f"{tool} declares create_artifacts it did not produce: {missing}"


@pytest.mark.integration
@pytest.mark.parametrize("tool", _ALL_TOOLS)
def test_no_unrendered_template_delimiters(tool, tmp_path):
    """No tool leaks ``{{``/``{%`` or a source-path comment into any output file."""
    _build(tool, tmp_path)
    blob = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore")
        for p in sorted(tmp_path.rglob("*"))
        if p.is_file()
    )
    for marker in ("{{", "{%", "<!-- path:", "{{PRIMARY_AGENTS_LIST}}"):
        assert marker not in blob, f"{tool} leaked unrendered template marker: {marker!r}"
