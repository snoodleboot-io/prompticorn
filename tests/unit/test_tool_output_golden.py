"""Golden byte-identical output test for all tools (PRO-60 / F2b).

Builds a fixed sample configuration for every tool id + variant and asserts the
generated file tree (relative path + sha256 of content) exactly matches the
recorded baseline. This guards the write-layout strategy refactor: extracting
the per-tool ``if self.tool_name ==`` branches must not change any emitted byte.

To regenerate the baseline (only when output changes intentionally), run the
snippet in the module docstring of the generator, or delete the fixture and
re-capture. Do NOT regenerate to make a failing refactor pass.
"""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from prompticorn.prompt_builder import get_prompt_builder

_FIXTURE = Path(__file__).parent / "_golden_tool_output.json"
_CONFIG_BASE = {"spec": {"language": "python"}, "active_personas": ["software_engineer"]}


def _manifest(root: Path) -> list[list[str]]:
    """Return sorted [relative_posix_path, sha256] for every file under root."""
    items: list[list[str]] = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            items.append([path.relative_to(root).as_posix(), digest])
    return items


class TestToolOutputGolden(unittest.TestCase):
    """Every tool/variant build matches the recorded byte-for-byte baseline."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = json.loads(_FIXTURE.read_text(encoding="utf-8"))

    def test_all_tools_match_golden_baseline(self) -> None:
        for key, expected in self.baseline.items():
            tool_id, variant = key.split("::")
            with self.subTest(tool=tool_id, variant=variant):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    builder = get_prompt_builder(tool_id)
                    builder.build(root, {**_CONFIG_BASE, "variant": variant}, dry_run=False)
                    self.assertEqual(
                        _manifest(root),
                        [list(pair) for pair in expected],
                        f"output for {tool_id}::{variant} diverged from golden baseline",
                    )


if __name__ == "__main__":
    unittest.main()
