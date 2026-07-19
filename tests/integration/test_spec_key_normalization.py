"""Regression tests for question-key -> spec-key normalization (PRO-65, PRO-66).

Historically two flows mapped a question's answer to a spec key differently and
both could store it under a key no template reads:

* Single-language stripped the ``<language>_`` prefix (``go_version`` ->
  ``version``), but every convention reads ``runtime`` -> the version pick for
  all 21 non-Python languages was silently dropped.
* Monorepo stored the raw ``question.key`` (``python_linter``) unstripped ->
  templates read ``linter`` -> every monorepo core pick was dropped.

Both now normalize through ``spec_key_for``, which honors an explicit
``config_key`` and otherwise strips the language prefix.
"""

from prompticorn.questions.go.go_version_question import GoVersionQuestion
from prompticorn.questions.handlers.handle_single_language_questions import (
    HandleSingleLanguageQuestions,
    spec_key_for,
)
from prompticorn.questions.python.python_linter_question import PythonLinterQuestion
from prompticorn.questions.python.python_runtime_question import PythonRuntimeQuestion
from prompticorn.questions.shell.shell_type_question import ShellTypeQuestion


def _pick_last_selector(
    language: str,
):
    """Selector that picks ``language`` for the language prompt and the last
    (guaranteed non-default) option for every other single-select question."""

    def selector(
        question,
        options,
        explanations=None,
        question_explanation=None,
        default_index=0,
        default_indices=None,
        allow_multiple=False,
        none_index=None,
    ):
        if options and language in options:
            return language
        if allow_multiple:
            return [options[default_index]] if options else []
        return options[-1] if options else ""

    return selector


class TestSpecKeyFor:
    def test_config_key_is_authoritative(self):
        # Every *VersionQuestion declares config_key = "runtime".
        assert spec_key_for(GoVersionQuestion(), "go") == "runtime"
        assert spec_key_for(PythonRuntimeQuestion(), "python") == "runtime"

    def test_falls_back_to_prefix_strip(self):
        # Questions without a config_key strip the "<language>_" prefix.
        assert spec_key_for(PythonLinterQuestion(), "python") == "linter"

    def test_config_key_prevents_folder_type_collision(self):
        # shell_type must not strip to "type" (which is the folder-type field).
        assert spec_key_for(ShellTypeQuestion(), "shell") == "shell_type"


class TestSingleLanguageVersionLands:
    def test_non_python_version_reaches_runtime(self):
        # PRO-65: picking a Go version must populate spec.runtime, not a dead key.
        config = HandleSingleLanguageQuestions(_pick_last_selector("go")).handle("single-language")
        assert config["spec"]["runtime"] == GoVersionQuestion().options[-1]
        assert "version" not in config["spec"], "answer stored under dead 'version' key"

    def test_python_runtime_still_maps(self):
        # Python was the only language that worked before; keep it working.
        config = HandleSingleLanguageQuestions(_pick_last_selector("python")).handle(
            "single-language"
        )
        assert config["spec"]["runtime"] == PythonRuntimeQuestion().options[-1]
