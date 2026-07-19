"""Regression test for app-framework rendering (PRO-69).

The ``framework`` question (ASP.NET, React, Giraffe, …) was collected but read by
no template. It is a *core* question for csharp/typescript/fsharp, so those
conventions now render it. Asserts the chosen value reaches output on both a
lenient (claude) and a StrictUndefined (copilot) build, and on an AGENTS.md-only
tool (gemini).
"""

from pathlib import Path

import pytest

from prompticorn.config_handler import create_default_config
from prompticorn.prompt_builder import get_prompt_builder

_SENTINEL = "FrameworkSentinel"


@pytest.mark.parametrize("language", ["csharp", "typescript", "fsharp"])
@pytest.mark.parametrize("tool", ["claude", "copilot", "gemini"])
def test_framework_value_renders(language, tool, tmp_path):
    config = create_default_config(language)
    config["variant"] = "minimal"
    config["active_personas"] = ["software_engineer"]
    config["spec"]["framework"] = _SENTINEL
    actions = get_prompt_builder(tool).build(tmp_path, config=config, dry_run=False)
    assert not [a for a in actions if a.startswith("✗")], actions
    blob = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore")
        for p in Path(tmp_path).rglob("*")
        if p.is_file()
    )
    assert _SENTINEL in blob, f"{language}/{tool}: framework not rendered"
