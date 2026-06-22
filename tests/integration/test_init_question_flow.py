"""Regression tests for the interactive init question flow → build.

The unit/build tests use create_default_config (coverage is already a dict). The
real `init` flow runs the question pipeline, where the coverage question yields a
preset *name* ("standard") that must be resolved to a targets dict. A prior
regression stored the raw string, which then crashed convention rendering and
silently dropped ALL conventions. These tests exercise that exact path.
"""

import pytest

from prompticorn.prompt_builder import get_prompt_builder
from prompticorn.questions.handlers.handle_single_language_questions import (
    HandleSingleLanguageQuestions,
    resolve_answer,
)
from prompticorn.questions.python.python_coverage_targets_question import (
    PythonCoverageTargetsQuestion,
)


def _stub_selector(
    question,
    options,
    explanations=None,
    question_explanation=None,
    default_index=0,
    default_indices=None,
    allow_multiple=False,
    none_index=None,
):
    """Pick python for the language prompt, otherwise the default option."""
    if allow_multiple:
        return [options[default_index]] if options else []
    if options and "python" in options:
        return "python"
    return options[default_index] if options else ""


class TestResolveAnswer:
    def test_coverage_preset_resolves_to_dict(self):
        q = PythonCoverageTargetsQuestion()
        resolved = resolve_answer(q, "standard")
        assert isinstance(resolved, dict)
        assert resolved["line"] == 80

    def test_plain_answer_passes_through(self):
        q = PythonCoverageTargetsQuestion()
        # An option without a preset mapping falls back to the raw answer.
        assert resolve_answer(q, "nonexistent") == "nonexistent"


class TestInitQuestionFlowBuild:
    def test_question_flow_yields_dict_coverage(self):
        config = HandleSingleLanguageQuestions(_stub_selector).handle("single-language")
        assert isinstance(config["spec"]["coverage"], dict), (
            "coverage must resolve to a targets dict, not a preset name"
        )

    def test_question_flow_build_emits_conventions(self, tmp_path):
        # Arrange — build the config exactly as `init` does (question pipeline).
        config = HandleSingleLanguageQuestions(_stub_selector).handle("single-language")
        config["variant"] = "minimal"
        config["active_personas"] = ["software_engineer"]
        # Act
        actions = get_prompt_builder("claude").build(tmp_path, config=config, dry_run=False)
        # Assert — conventions are generated (the regression dropped them entirely).
        assert not [a for a in actions if a.startswith("⚠")], actions
        general = tmp_path / ".claude" / "conventions" / "core" / "general.md"
        python_conv = tmp_path / ".claude" / "conventions" / "languages" / "python.md"
        assert general.exists() and python_conv.exists()
        assert "#### Coverage Targets" in python_conv.read_text(encoding="utf-8")

    @pytest.mark.parametrize("tool", ["copilot", "kilo-cli"])
    def test_question_flow_build_other_tools_no_failures(self, tool, tmp_path):
        config = HandleSingleLanguageQuestions(_stub_selector).handle("single-language")
        config["variant"] = "minimal"
        config["active_personas"] = ["software_engineer"]
        actions = get_prompt_builder(tool).build(tmp_path, config=config, dry_run=False)
        assert not [a for a in actions if a.startswith("✗")], actions
