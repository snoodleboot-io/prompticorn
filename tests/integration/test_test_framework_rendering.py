"""Regression test for test_framework rendering across all languages (PRO-68).

Nine languages (javascript, csharp, php, swift, scala, elixir, elm, dart, lua)
have hand-written testing sections that did not render the collected
``test_framework`` value — the "Framework:" line shipped a literal
"[Template variable]" placeholder. This asserts the chosen value now reaches the
rendered convention for every language, on both a lenient (claude) and a
StrictUndefined (copilot) build path.
"""

from pathlib import Path

import pytest

from prompticorn.config_handler import create_default_config
from prompticorn.prompt_builder import get_prompt_builder

_SENTINEL = "SentinelTestFW"

# The nine languages whose hand-written testing sections previously shipped a
# literal "[Template variable]" for the framework instead of the collected value
# (PRO-68). Languages without a testing-framework concept (html, sql, terraform,
# shell, …) are intentionally excluded — they render no framework line.
_LANGUAGES = [
    "javascript",
    "csharp",
    "php",
    "swift",
    "scala",
    "elixir",
    "elm",
    "dart",
    "lua",
]


@pytest.mark.parametrize("language", _LANGUAGES)
@pytest.mark.parametrize("tool", ["claude", "copilot"])
def test_test_framework_value_renders(language, tool, tmp_path):
    # Arrange — a non-default test_framework the template must surface.
    config = create_default_config(language)
    config["variant"] = "minimal"
    config["active_personas"] = ["software_engineer"]
    config["spec"]["test_framework"] = _SENTINEL
    # Act
    actions = get_prompt_builder(tool).build(tmp_path, config=config, dry_run=False)
    # Assert — build clean and the chosen framework appears in output.
    assert not [a for a in actions if a.startswith("✗")], actions
    blob = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore")
        for p in Path(tmp_path).rglob("*")
        if p.is_file()
    )
    assert _SENTINEL in blob, f"{language}/{tool}: test_framework not rendered"
