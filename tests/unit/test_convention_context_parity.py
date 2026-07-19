"""Guard for cross-builder convention-context parity (PRO-87).

The Claude/AGENTS.md language context (`_build_template_context`) and the
CoreFilesLoader context (kilo/cline/cursor/copilot) render the same convention
templates, so a variable present in one but not the other causes "renders on one
tool, blank/StrictUndefined-crash on another". This pins the shared keys.
"""

from prompticorn.builders.convention_generator import _build_template_context

# Keys the CoreFilesLoader context provides that the Claude context must also
# expose (empty-defaulted) to keep the two render paths in parity.
_PARITY_KEYS = [
    "repository_type",
    "source_layout",
    "error_handling",
    "commit_style",
    "pr_size",
    "deploy_target",
    "databases",
    "data_access",
]


def test_parity_keys_present():
    ctx = _build_template_context({"language": "python"})
    missing = [k for k in _PARITY_KEYS if k not in ctx]
    assert not missing, f"language context missing parity keys: {missing}"


def test_bare_coverage_not_exposed():
    # `coverage` (raw spec value) is dropped — the CoreFilesLoader context never
    # provided it, and a bare {{ coverage }} would crash there under
    # StrictUndefined. Templates use coverage_targets / config.coverage instead.
    ctx = _build_template_context({"language": "python", "coverage": {"line": 80}})
    assert "coverage" not in ctx
    assert "coverage_targets" in ctx
    assert ctx["config"].get("coverage") == {"line": 80}
