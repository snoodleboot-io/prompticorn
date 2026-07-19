"""Value-coverage matrix: prove collected answers reach every tool's output.

TESTING STRATEGY (PRO-64)
=========================
Every other test drives the ``init`` flow with a selector that returns *defaults*
and asserts substitution for only a couple of builders. That leaves two whole
classes of defect invisible:

* **collected-but-never-applied** — an answer the user picked is stored under a
  key no template reads, so the default renders instead (e.g. the historical
  ``go_version`` -> ``version`` bug, PRO-65).
* **placeholder-never-fed / leaked** — a template variable that ships
  unsubstituted for some builders (e.g. ``{{PRIMARY_AGENTS_LIST}}`` on the 9
  newer tools, PRO-72).

This module is the safety net for both. It drives the *real* single-language
question flow (and, for rendering, a sentinel-injected config) across **every**
supported tool id:

* ``test_build_reports_no_failures`` — every tool builds a non-default config
  with no per-file failure.
* ``test_flow_maps_chosen_answer_to_spec`` — the *collection* half: each chosen
  non-default answer lands under the spec key templates read (PRO-65/66).
* ``test_select_from_answers_lands_explicit_choice`` — the reusable
  ``select_from_answers`` seam drives the flow from an explicit answer map.
* ``test_chosen_values_reach_output`` — the *rendering* half: each literal spec
  value (via a unique sentinel that can't occur coincidentally) reaches the
  tool's output.
* ``test_output_has_no_unrendered_templates`` — no tool leaks ``{{``/``{%`` or
  ``{{PRIMARY_AGENTS_LIST}}``.
* ``test_every_collected_key_is_accounted_for`` — every collected spec key is
  either sentinel-asserted or explicitly classified as not-rendered, so a
  newly-added dead-end key fails loudly.

Known-open defects are pinned with ``strict`` xfail markers keyed to their
remediation ticket. When a fix lands, its xfail flips to an unexpected pass and
fails this suite — that is the signal to delete the marker. **Do not** silence a
new failure by adding a tool to an xfail set without a ticket.

Adding a question to the matrix: the non-default selector already covers every
single-select question. If a new value should render, add its spec key +
sentinel to ``_SENTINELS``; if it is intentionally not rendered, add it to
``_KNOWN_NOT_RENDERED`` with a reason.
"""

import re
from typing import Any

import pytest

from prompticorn.config_handler import create_default_config
from prompticorn.prompt_builder import get_prompt_builder
from prompticorn.questions.handlers.handle_single_language_questions import (
    HandleSingleLanguageQuestions,
)
from prompticorn.tools import supported_tool_ids

_JINJA = re.compile(r"\{\{|\{%")

# Every canonical tool id (kilo-cli/kilo-ide and copilot/copilot-chat are
# distinct builders/layouts, so all are exercised).
_ALL_TOOLS = sorted(supported_tool_ids())

# PRO-67 (resolved): AGENTS.md-only tools now inline the per-language convention,
# so per-language spec values reach them too. Kept as an (empty) seam so a future
# regression on a specific tool can be pinned to a ticket here.
_CORE_ONLY_TOOLS: set[str] = set()

# PRO-72 (resolved): a post-write pass now resolves {{PRIMARY_AGENTS_LIST}} for
# the IR-based builders, so no tool leaks it. Kept as an (empty) seam so a future
# leak regression on a specific tool can be pinned to a ticket here.
_LEAK_TOOLS: set[str] = set()

# Core per-language spec values that render as a literal value and so MUST reach
# the output of any tool that emits a per-language convention. Each is given a
# unique sentinel value that cannot occur coincidentally in boilerplate — bare
# option strings like "pip"/"pytest" appear in scaffolding text and would false
# positive. ``abstract_class_style`` is deliberately excluded here: it renders as
# a conditional *block*, not a literal value (its mapping is covered by the
# flow-mapping test and test_conventions_conditional_rendering).
_SENTINELS = {
    "runtime": "SENTINEL_RUNTIME_X",
    "package_manager": "SENTINEL_PKGMGR_X",
    "test_framework": "SENTINEL_TESTFW_X",
    "linter": "SENTINEL_LINTER_X",
    "formatter": "SENTINEL_FORMATTER_X",
    # PRO-69: python testing-tool selections, now rendered by conventions-python.md.
    "test_runner": "SENTINEL_TESTRUNNER_X",
    "mocking_library": "SENTINEL_MOCKING_X",
    "coverage_tool": "SENTINEL_COVTOOL_X",
    "mutation_tool": "SENTINEL_MUTATION_X",
}

# Core single-select questions whose chosen answer must land under the expected
# spec key (proves the question -> spec-key mapping, PRO-65/66). Maps spec key ->
# question key asked in the python single-language pipeline.
_FLOW_MAPPED = {
    "runtime": "python_runtime",
    "package_manager": "python_package_manager",
    "test_framework": "python_test_framework",
    "linter": "python_linter",
    "formatter": "python_formatter",
    "abstract_class_style": "python_abstract_class_style",
}

# Collected spec keys that are intentionally NOT asserted present as a literal
# value, with the reason. Guards test_every_collected_key_is_accounted_for so a
# newly-added collected key must be classified deliberately.
_KNOWN_NOT_RENDERED = {
    "language": "rendered, but also the folder name — asserted elsewhere",
    "repo_type": "metadata, not a rendered convention value",
    "coverage": "dict of targets; rendered as numbers, not a single literal",
    "layout_style": "drives the source-tree layout, not emitted verbatim",
    "error_handling": "may render '(not specified)'; covered by convention tests",
    "linters": "PRO-69: rendered when present, but a list; not sentinel-asserted",
    "abstract_class_style": "renders as a conditional block, not a literal value",
    "framework": "PRO-69: rendered for csharp/ts/fsharp core + python fungible; "
    "not collected in python single-language, so not sentinel-asserted here",
}


def select_from_answers(answers: dict[str, str]):
    """Build a UI selector that answers each question from an explicit map.

    ``answers`` maps a question's *display text* to the option to pick (the
    handler passes ``question.question_text`` to the selector, not the Question
    object, so text is the only key available). Any question not in the map
    takes its default; multi-select questions return a single-item list. This is
    the reusable seam for driving the flow with a chosen answer set without
    touching the interactive Click command.
    """

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
        chosen = answers.get(question)
        if allow_multiple:
            return [chosen] if chosen is not None else ([options[default_index]] if options else [])
        if chosen is not None and chosen in options:
            return chosen
        return options[default_index] if options else ""

    return selector


def _non_default_selector(language: str):
    """Selector that picks ``language`` for the language prompt and, for every
    other question, the first option that differs from the default — so each
    stored value is provably distinct from the seeded default."""

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
        non_default = [o for i, o in enumerate(options) if i != default_index]
        if allow_multiple:
            return (
                [non_default[0]] if non_default else ([options[default_index]] if options else [])
            )
        return non_default[0] if non_default else (options[default_index] if options else "")

    return selector


def _build_non_default_config(language: str = "python") -> dict[str, Any]:
    """Drive the real single-language question flow picking non-default answers."""
    config = HandleSingleLanguageQuestions(_non_default_selector(language)).handle(
        "single-language"
    )
    config["variant"] = "minimal"
    config["active_personas"] = ["software_engineer"]
    return config


def _sentinel_config(language: str = "python") -> dict[str, Any]:
    """A default config with each literal-rendered spec value replaced by a
    unique sentinel, so 'did the value reach output?' is unambiguous."""
    config = create_default_config(language)
    config["variant"] = "minimal"
    config["active_personas"] = ["software_engineer"]
    config["spec"].update(_SENTINELS)
    return config


def _build_blob(tool: str, config: dict[str, Any], tmp_path) -> tuple[list[str], str]:
    actions = get_prompt_builder(tool).build(tmp_path, config=config, dry_run=False)
    blob = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore") for p in tmp_path.rglob("*") if p.is_file()
    )
    return actions, blob


def _tool_param(tool: str, xfail_set: set[str], reason: str):
    if tool in xfail_set:
        return pytest.param(tool, marks=pytest.mark.xfail(reason=reason, strict=True))
    return pytest.param(tool)


@pytest.mark.parametrize("tool", _ALL_TOOLS)
def test_build_reports_no_failures(tool, tmp_path):
    """Every tool builds a non-default config without a per-file failure."""
    config = _build_non_default_config()
    actions, _ = _build_blob(tool, config, tmp_path)
    failures = [a for a in actions if a.startswith("✗")]
    assert not failures, f"{tool} build failures: {failures}"


def _expected_non_default(question) -> str:
    """The option _non_default_selector will pick for a question: the first one
    whose index differs from the question's own default."""
    default_idx = (
        question.options.index(question.default) if question.default in question.options else 0
    )
    return next(o for i, o in enumerate(question.options) if i != default_idx)


@pytest.mark.parametrize("spec_key,question_key", sorted(_FLOW_MAPPED.items()))
def test_flow_maps_chosen_answer_to_spec(spec_key, question_key):
    """The CLI flow stores each chosen non-default answer under the spec key the
    templates read — the collection half of value coverage (PRO-65/66). Failure
    means an answer is silently dropped before rendering is even reached."""
    from prompticorn.questions.language import get_language_questions

    questions = {q.key: q for q in get_language_questions("python")}
    assert question_key in questions, f"{question_key} not in the python pipeline"
    expected = _expected_non_default(questions[question_key])

    config = _build_non_default_config()
    stored = config["spec"].get(spec_key)
    stored_scalar = stored[0] if isinstance(stored, list) and stored else stored
    assert stored_scalar == expected, (
        f"non-default answer {expected!r} for {question_key} did not land under "
        f"spec[{spec_key!r}] (got {stored!r})"
    )


def test_select_from_answers_lands_explicit_choice():
    """The reusable select_from_answers helper drives the flow from an explicit
    {question_text: option} map, and the chosen option reaches the spec."""
    from prompticorn.questions.python.python_package_manager_question import (
        PythonPackageManagerQuestion,
    )

    q = PythonPackageManagerQuestion()
    target = _expected_non_default(q)  # a non-default package manager
    selector = select_from_answers(
        {"What is your primary language?": "python", q.question_text: target}
    )
    config = HandleSingleLanguageQuestions(selector).handle("single-language")
    stored = config["spec"].get("package_manager")
    stored_scalar = stored[0] if isinstance(stored, list) and stored else stored
    assert stored_scalar == target


@pytest.mark.parametrize(
    "tool",
    [
        _tool_param(t, _CORE_ONLY_TOOLS, "PRO-67: core-only tools emit no per-language convention")
        for t in _ALL_TOOLS
    ],
)
def test_chosen_values_reach_output(tool, tmp_path):
    """Every literal spec value (via unique sentinels) reaches the tool's output
    — the rendering half of value coverage. Sentinels cannot occur coincidentally
    in boilerplate, so a miss is a genuine drop, not a false positive."""
    config = _sentinel_config()
    _, blob = _build_blob(tool, config, tmp_path)
    missing = {key: sentinel for key, sentinel in _SENTINELS.items() if sentinel not in blob}
    assert not missing, f"{tool}: these chosen values did not reach output: {sorted(missing)}"


@pytest.mark.parametrize(
    "tool",
    [
        _tool_param(t, _LEAK_TOOLS, "PRO-72: {{PRIMARY_AGENTS_LIST}} left unsubstituted")
        for t in _ALL_TOOLS
    ],
)
def test_output_has_no_unrendered_templates(tool, tmp_path):
    """No tool leaks unrendered template syntax into its output."""
    config = _sentinel_config()
    _, blob = _build_blob(tool, config, tmp_path)
    offenders = []
    if _JINJA.search(blob):
        offenders.append("jinja `{{`/`{%`")
    if "{{PRIMARY_AGENTS_LIST}}" in blob:
        offenders.append("PRIMARY_AGENTS_LIST")
    if "<!-- path:" in blob:
        offenders.append("source-path comment")
    assert not offenders, f"{tool} emitted unrendered templates: {offenders}"


def _parse_toml(path):
    try:
        import tomllib
    except ModuleNotFoundError:  # py3.10
        import tomli as tomllib
    with open(path, "rb") as fh:
        tomllib.load(fh)


@pytest.mark.parametrize("tool", _ALL_TOOLS)
def test_emitted_structured_files_parse(tool, tmp_path):
    """Every emitted JSON/TOML/YAML artifact must parse (PRO-80).

    The no-leak scan only greps for ``{{ }}``; it never parsed structured output,
    which is how a token substitution injecting raw newlines into a JSON string
    (Amazon Q's agent ``prompt``) shipped invalid JSON. This closes that gap.
    """
    import json as _json

    import yaml

    get_prompt_builder(tool).build(tmp_path, config=_sentinel_config(), dry_run=False)
    failures = []
    for p in tmp_path.rglob("*"):
        if not p.is_file():
            continue
        suffix = p.suffix.lower()
        try:
            if suffix == ".json":
                _json.loads(p.read_text(encoding="utf-8"))
            elif suffix == ".toml":
                _parse_toml(p)
            elif suffix in (".yaml", ".yml") or p.name == ".roomodes":
                yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{p.relative_to(tmp_path)}: {type(exc).__name__}: {exc}")
    assert not failures, f"{tool} emitted unparseable structured file(s): {failures}"


def test_no_template_variable_placeholder_in_convention_sources():
    """Guard (PRO-73): no convention ships the literal '[Template variable]'
    placeholder. Unlike Jinja `{{ }}`, this literal survives rendering silently,
    so it must be caught at the source."""
    from pathlib import Path as _Path

    core = _Path(__file__).parent.parent.parent / "prompticorn" / "agents" / "core"
    offenders = [
        p.name
        for p in core.glob("conventions-*.md")
        if "[Template variable]" in p.read_text(encoding="utf-8")
    ]
    assert not offenders, f"conventions still using the literal placeholder: {offenders}"


def test_every_collected_key_is_accounted_for():
    """Guard: every key the flow stores in spec is either asserted-rendered
    (_SENTINELS) or explicitly classified as not-rendered (_KNOWN_NOT_RENDERED).
    A newly-added collected key forces a deliberate render-or-dead-end decision."""
    config = _build_non_default_config()
    collected = set(config["spec"])
    classified = set(_SENTINELS) | set(_KNOWN_NOT_RENDERED)
    unclassified = collected - classified
    assert not unclassified, (
        f"collected spec keys not classified as rendered or known-dead-end: "
        f"{sorted(unclassified)} — wire them into a template or add to "
        f"_KNOWN_NOT_RENDERED with a reason (see PRO-69)."
    )
