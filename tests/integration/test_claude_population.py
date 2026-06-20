"""Integration tests for Claude artifact population (end-to-end build).

These guard against a regression where the Claude build path emitted unrendered
template variables and raw Jinja2: language conventions shipped literal
``{{ language }}`` / macro imports, spec choices never reached the conventions,
and the orchestrator agent shipped a raw ``{{PRIMARY_AGENTS_LIST}}``.

Unlike ``test_conventions_conditional_rendering`` (which exercises the renderer
directly), these tests drive the actual ``get_prompt_builder("claude").build()``
path that real ``prompticorn init`` runs use.
"""

import re

import pytest

from prompticorn.config_handler import create_default_config
from prompticorn.prompt_builder import get_prompt_builder
from prompticorn.questions.base.spec_handler import SpecHandler

# Raw Jinja2 tokens / unresolved template stubs that must never survive into
# generated Claude output.
# (The ``general.md`` core convention still carries ``[LANG]``/``TODO`` fill-in
# prose, tracked separately in CLAUDE_TEMPLATE_POPULATION_FIX Phase 3.)
_UNRENDERED_PATTERNS = (
    re.compile(r"\{\{"),  # Jinja2 expression
    re.compile(r"\{%"),  # Jinja2 statement
    re.compile(r"Dynamic content - see template"),  # unfilled convention stub
    re.compile(r"<!--\s*path:"),  # leaked internal source-path comment
)


def _build_claude(output_dir, config):
    """Build Claude artifacts into output_dir and return the list of files."""
    get_prompt_builder("claude").build(output_dir, config=config, dry_run=False)
    return sorted(p for p in output_dir.rglob("*") if p.is_file())


def _assert_no_unrendered_tokens(files):
    """Assert that no generated file contains unrendered template tokens."""
    offenders = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for pattern in _UNRENDERED_PATTERNS:
            if pattern.search(text):
                offenders.append(f"{path.name}: {pattern.pattern}")
    assert not offenders, f"Unrendered template tokens found: {offenders}"


@pytest.fixture
def single_python_config():
    """Single-language Python configuration (as produced by `init`)."""
    config = create_default_config("python")
    config["variant"] = "minimal"
    config["active_personas"] = ["software_engineer"]
    return config


@pytest.fixture
def multi_language_config():
    """Multi-language monorepo: Python backend + TypeScript frontend."""
    handler = SpecHandler.for_repository_type("single-language")
    backend = handler.create_spec("python")
    backend["folder"] = "backend"
    frontend = handler.create_spec("typescript")
    frontend["folder"] = "frontend"
    return {
        "version": "1.0",
        "repository": {"type": "multi-language-monorepo", "mappings": {}},
        "spec": [backend, frontend],
        "variant": "minimal",
        "active_personas": ["software_engineer"],
    }


class TestSingleLanguageClaudePopulation:
    """Claude build for a single-language Python project."""

    def test_no_unrendered_template_tokens(self, tmp_path, single_python_config):
        # Arrange / Act
        files = _build_claude(tmp_path, single_python_config)
        # Assert
        _assert_no_unrendered_tokens(files)

    def test_language_convention_contains_spec_values(self, tmp_path, single_python_config):
        # Arrange / Act
        _build_claude(tmp_path, single_python_config)
        python_md = (tmp_path / ".claude" / "conventions" / "languages" / "python.md").read_text(
            encoding="utf-8"
        )
        # Assert — the user's actual Python toolchain choices are populated:
        # package manager, linter, formatter, AND the test framework + coverage
        # targets (rendered via the testing macro).
        assert "uv" in python_md
        assert "ruff" in python_md
        assert "pytest" in python_md
        assert "#### Coverage Targets" in python_md
        # abstract_class_style is populated from the (defaulted) spec and the
        # matching conditional block renders.
        assert "Abstract Class Style: interface" in python_md
        assert "Interface Pattern" in python_md

    def test_orchestrator_agents_list_is_populated(self, tmp_path, single_python_config):
        # Arrange / Act
        _build_claude(tmp_path, single_python_config)
        orchestrator = (tmp_path / ".claude" / "agents" / "orchestrator-agent.md").read_text(
            encoding="utf-8"
        )
        # Assert — the template variable is replaced with a real agent list,
        # restricted to the active persona's agents (which are the ones generated).
        assert "{{PRIMARY_AGENTS_LIST}}" not in orchestrator
        assert "- **code**" in orchestrator
        assert "- **backend**" in orchestrator
        # An agent NOT in the software_engineer persona must not be listed
        # (it isn't generated, so the orchestrator must not reference it).
        assert "- **compliance**" not in orchestrator
        generated_agents = {
            p.stem.replace("-agent", "") for p in (tmp_path / ".claude" / "agents").glob("*.md")
        }
        listed_agents = set(re.findall(r"^- \*\*([a-z]+)\*\*", orchestrator, re.MULTILINE))
        assert listed_agents == generated_agents


class TestMultiLanguageClaudePopulation:
    """Claude build for a Python + TypeScript monorepo."""

    def test_no_unrendered_template_tokens(self, tmp_path, multi_language_config):
        # Arrange / Act
        files = _build_claude(tmp_path, multi_language_config)
        # Assert
        _assert_no_unrendered_tokens(files)

    def test_each_language_convention_uses_its_own_spec(self, tmp_path, multi_language_config):
        # Arrange / Act
        _build_claude(tmp_path, multi_language_config)
        languages_dir = tmp_path / ".claude" / "conventions" / "languages"
        python_md = (languages_dir / "python.md").read_text(encoding="utf-8")
        typescript_md = (languages_dir / "typescript.md").read_text(encoding="utf-8")
        # Assert — backend Python toolchain in python.md, frontend TS toolchain in
        # typescript.md (each convention rendered from its own folder spec).
        assert "uv" in python_md
        assert "ruff" in python_md
        assert "pytest" in python_md
        assert "pnpm" in typescript_md
        assert "eslint" in typescript_md
        assert "prettier" in typescript_md
        assert "vitest" in typescript_md
