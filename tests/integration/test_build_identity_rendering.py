"""Regression test for language build/identity selections (PRO-83).

These values declare a config_key (so they're collected in the single-language
flow) but were rendered nowhere — the conventions either had no field or wired
the wrong variable (shell read runtime instead of shell_type; java/kotlin/scala/
clojure/haskell read package_manager, which those languages never collect,
instead of build_tool). Each now renders the value the user actually chose.
"""

from pathlib import Path

import pytest

from prompticorn.config_handler import create_default_config
from prompticorn.prompt_builder import get_prompt_builder

# (language, spec key) — value the convention must now render.
_CASES = [
    ("haskell", "compiler"),
    ("haskell", "build_tool"),
    ("java", "build_tool"),
    ("kotlin", "build_tool"),
    ("scala", "build_tool"),
    ("clojure", "build_tool"),
    ("sql", "sql_dialect"),
    ("shell", "shell_type"),
]


@pytest.mark.parametrize("language,key", _CASES)
@pytest.mark.parametrize("tool", ["claude", "copilot"])
def test_build_identity_value_renders(language, key, tool, tmp_path):
    sentinel = f"SENT_{key.upper()}"
    config = create_default_config(language)
    config["variant"] = "minimal"
    config["active_personas"] = ["software_engineer"]
    config["spec"][key] = sentinel
    actions = get_prompt_builder(tool).build(tmp_path, config=config, dry_run=False)
    assert not [a for a in actions if a.startswith("✗")], actions
    blob = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore")
        for p in Path(tmp_path).rglob("*")
        if p.is_file()
    )
    assert sentinel in blob, f"{language}/{tool}: {key} not rendered"
