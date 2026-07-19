"""Regression test for data-system rendering in language conventions (PRO-70).

conventions-sql.md references {{ databases }} / {{ data_access }}, but the
Claude/AGENTS.md language-convention context did not inject them (only the core
context did), so they rendered blank on that path while the Kilo/CoreFilesLoader
path rendered them. Assert both paths now render them identically.
"""

from pathlib import Path

import pytest

from prompticorn.config_handler import create_default_config
from prompticorn.prompt_builder import get_prompt_builder


@pytest.mark.parametrize("tool", ["claude", "kilo-cli"])
def test_sql_convention_renders_data_system(tool, tmp_path):
    config = create_default_config("sql")
    config["variant"] = "minimal"
    config["active_personas"] = ["software_engineer"]
    config["spec"]["databases"] = ["PostgreSQL", "SQLite"]
    config["spec"]["data_access"] = ["SQLAlchemy"]
    get_prompt_builder(tool).build(tmp_path, config=config, dry_run=False)
    blob = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore")
        for p in Path(tmp_path).rglob("*")
        if p.is_file()
    )
    assert "PostgreSQL" in blob, f"{tool}: databases not rendered in sql convention"
    assert "SQLAlchemy" in blob, f"{tool}: data_access not rendered in sql convention"
