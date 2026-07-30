"""Generated output must not depend on the working directory (PRO-105).

`CoreFilesLoader` defaulted to the **CWD-relative** path
``"prompticorn/agents/core"``. Five builders instantiate it, so every core
convention silently vanished whenever the process ran from anywhere but the
repository root — which is always, for an installed package used in someone
else's repo.

Measured before the fix, for a single-language python build:

    cline    .clinerules   782,122 chars at repo root -> 200,674 elsewhere (74% lost)
    cursor   .cursorrules  same truncation
    copilot  copilot-instructions.md  same truncation
    kilo-ide 6 of 6 files under .kilo/rules/ missing entirely

The golden corpus cannot catch this: pytest always runs from the repository
root, so the recorded baseline is the *working* output and every user got the
degraded one. Hence a dedicated test that builds from a foreign directory.
"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from prompticorn.prompt_builder import get_prompt_builder

_CONFIG = {
    "spec": {"language": "python"},
    "active_personas": ["software_engineer"],
    "variant": "minimal",
}

_DATE_RE = re.compile(rb"\d{4}-\d{2}-\d{2}")

# Every builder that instantiates CoreFilesLoader, plus claude as a control that
# never did — so a regression here is attributable rather than ambient.
_BUILDERS = ["cline", "cursor", "copilot", "kilo-ide", "claude"]


def _manifest(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(
            _DATE_RE.sub(b"YYYY-MM-DD", path.read_bytes())
        ).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _build_from(cwd: Path, tool: str) -> dict[str, str]:
    previous = Path.cwd()
    try:
        os.chdir(cwd)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            get_prompt_builder(tool).build(root, _CONFIG, dry_run=False)
            return _manifest(root)
    finally:
        os.chdir(previous)


@pytest.mark.unit
class TestOutputIsIndependentOfWorkingDirectory:
    @pytest.mark.parametrize("tool", _BUILDERS)
    def test_output_identical_from_a_foreign_cwd(self, tool, tmp_path):
        """The regression itself: identical bytes regardless of where the
        process runs."""
        from_repo = _build_from(Path.cwd(), tool)
        from_elsewhere = _build_from(tmp_path, tool)

        missing = sorted(set(from_repo) - set(from_elsewhere))
        assert not missing, f"{tool} loses files when run outside the repo: {missing}"
        changed = sorted(
            p for p in set(from_repo) & set(from_elsewhere) if from_repo[p] != from_elsewhere[p]
        )
        assert not changed, f"{tool} produces different content outside the repo: {changed}"

    def test_core_conventions_survive_a_foreign_cwd(self, tmp_path):
        """A targeted check on the specific content that used to vanish, so a
        failure names the cause rather than just 'bytes differ'."""
        emitted = _build_from(tmp_path, "kilo-ide")
        rules = {p for p in emitted if p.startswith(".kilo/rules/")}
        for expected in (
            ".kilo/rules/system.md",
            ".kilo/rules/conventions.md",
            ".kilo/rules/session.md",
            ".kilo/rules/conventions-python.md",
        ):
            assert expected in rules, f"{expected} missing when run outside the repo"

    def test_core_files_loader_reads_content_from_a_foreign_cwd(self, tmp_path):
        """The unit-level version: the loader itself must not depend on the CWD."""
        from prompticorn.ir.loaders.core_files_loader import CoreFilesLoader

        previous = Path.cwd()
        try:
            os.chdir(tmp_path)
            files = CoreFilesLoader().get_core_files(language="python")
        finally:
            os.chdir(previous)

        assert set(files) == {"system", "conventions", "session", "conventions_python"}
        assert all(content.strip() for content in files.values())

    def test_mapping_loaders_default_from_the_package_not_the_cwd(self, tmp_path):
        """The same defect class in the two mapping loaders — landmines that had
        not yet been stepped on because callers passed explicit paths."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader
        from prompticorn.ir.loaders.language_skill_mapping_loader import (
            LanguageSkillMappingLoader,
        )

        previous = Path.cwd()
        try:
            os.chdir(tmp_path)
            assert AgentSkillMappingLoader().get_skills_for_agent("code")
            assert LanguageSkillMappingLoader().mapping_file.is_file()
        finally:
            os.chdir(previous)
