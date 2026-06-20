"""Integration tests for population across all CoreFilesLoader-based builders.

Guards against a regression where kilo/cline/cursor/copilot builds silently failed
every agent (e.g. `'dict object' has no attribute 'abstract_class_style'`,
`'repository_type' is undefined`) or emitted unrendered template variables
(raw macro imports, `{{PRIMARY_AGENTS_LIST}}`) because those builders rendered
conventions/agent prompts without the spec context or template substitution that
the Claude/Kilo paths had.
"""

import re

import pytest

from prompticorn.config_handler import create_default_config
from prompticorn.prompt_builder import get_prompt_builder

# Tools whose builders render conventions via CoreFilesLoader and embed agent
# system prompts (i.e. not Claude, which has its own dedicated test).
_TOOLS = ["kilo-cli", "cline", "cursor", "copilot"]

_JINJA = re.compile(r"\{\{|\{%")


@pytest.fixture
def python_config():
    config = create_default_config("python")
    config["variant"] = "minimal"
    config["active_personas"] = ["software_engineer"]
    return config


@pytest.mark.parametrize("tool", _TOOLS)
def test_build_has_no_agent_failures(tool, tmp_path, python_config):
    # Arrange / Act
    actions = get_prompt_builder(tool).build(tmp_path, config=python_config, dry_run=False)
    # Assert — no agent/file build reported a failure
    failures = [a for a in actions if a.startswith("✗")]
    assert not failures, f"{tool} build failures: {failures}"


@pytest.mark.parametrize("tool", _TOOLS)
def test_output_has_no_unrendered_templates(tool, tmp_path, python_config):
    # Arrange / Act
    get_prompt_builder(tool).build(tmp_path, config=python_config, dry_run=False)
    # Assert — no raw Jinja2 and no unsubstituted PRIMARY_AGENTS_LIST
    offenders = []
    for path in tmp_path.rglob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if _JINJA.search(text) or "{{PRIMARY_AGENTS_LIST}}" in text or "<!-- path:" in text:
            offenders.append(path.name)
    assert not offenders, f"{tool} emitted unrendered templates in: {offenders}"
