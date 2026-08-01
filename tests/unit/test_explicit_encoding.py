"""File I/O must never rely on the platform default encoding (PRO-140).

`open`, `read_text` and `write_text` fall back to the platform default when no
`encoding` is given. On a UTF-8 Linux box that is UTF-8 and everything works; on
Windows (cp1252) or under a C/POSIX locale it is not — and prompticorn's content
is full of em dashes, arrows and box-drawing characters.

Two failure modes, the silent one being worse:

* ASCII/C locale -> ``UnicodeDecodeError`` and a crash.
* Windows cp1252 -> decodes without error and yields **mojibake**, so a corrupted
  system prompt reaches the model with no signal that anything went wrong.

This bites hardest in the Bedrock builder, which emits an ``invoke_example.py``
that runs on the *user's* machine, where we control neither locale nor platform.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

_PACKAGE = Path(__file__).parent.parent.parent / "prompticorn"

# Calls that take an `encoding` argument and silently default without one.
_ENCODING_SENSITIVE = {"open", "read_text", "write_text"}

# Emitted-code templates: python source we generate into the user's output. The
# same rule applies, but it cannot be caught by parsing our own AST because the
# code lives inside a string literal.
_EMITTED_TEMPLATE_SOURCES = [
    _PACKAGE / "builders" / "bedrock_builder.py",
]


def _unencoded_calls(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    findings = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = (
            func.attr
            if isinstance(func, ast.Attribute)
            else (func.id if isinstance(func, ast.Name) else "")
        )
        if name not in _ENCODING_SENSITIVE:
            continue
        # `open(...)` in binary mode takes no encoding; "b" in the mode argument.
        if name == "open" and any(
            isinstance(a, ast.Constant) and isinstance(a.value, str) and "b" in a.value
            for a in node.args[1:]
        ):
            continue
        if "encoding" not in {kw.arg for kw in node.keywords}:
            findings.append(f"{path.name}:{node.lineno} {name}()")
    return findings


@pytest.mark.unit
class TestNoImplicitEncoding:
    def test_no_live_call_relies_on_the_platform_default(self):
        """Sweep the whole package. Cheap, and it catches the next one too."""
        offenders = sorted(
            finding for path in sorted(_PACKAGE.rglob("*.py")) for finding in _unencoded_calls(path)
        )
        assert not offenders, (
            "file I/O without an explicit encoding relies on the platform default "
            f"and breaks on non-UTF-8 systems: {offenders}"
        )

    @pytest.mark.parametrize("source", _EMITTED_TEMPLATE_SOURCES, ids=lambda p: p.name)
    def test_emitted_python_templates_read_utf8_explicitly(self, source):
        """Code we generate runs on the user's machine, where we control neither
        the platform nor the locale. Checked as text because the emitted source
        lives inside a string literal and never reaches our AST."""
        text = source.read_text(encoding="utf-8")
        offenders = [
            line.strip()
            for line in text.splitlines()
            if (".read_text()" in line or ".write_text(" in line)
            and "encoding=" not in line
            and not line.strip().startswith("#")
        ]
        assert not offenders, f"emitted template has unencoded I/O: {offenders}"


@pytest.mark.unit
class TestEmittedBedrockScriptSurvivesNonUtf8:
    def test_emitted_invoke_example_declares_utf8_where_it_reads_content(self):
        """End-to-end: build the bundle and inspect the script we actually wrote,
        not just the template it came from."""
        from tempfile import TemporaryDirectory

        from prompticorn.prompt_builder import get_prompt_builder

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            get_prompt_builder("bedrock").build(
                root,
                {
                    "spec": {"language": "python"},
                    "active_personas": ["software_engineer"],
                    "variant": "minimal",
                },
                dry_run=False,
            )
            scripts = list(root.rglob("invoke_example.py"))
            assert scripts, "bedrock build emitted no invoke_example.py"
            emitted = scripts[0].read_text(encoding="utf-8")

        reads = [line for line in emitted.splitlines() if ".read_text(" in line]
        assert reads, "invoke_example.py no longer reads content — update this test"
        for line in reads:
            assert "encoding=" in line, f"emitted read without encoding: {line.strip()}"

    def test_emitted_prompts_are_not_ascii_so_the_encoding_matters(self):
        """Guards the premise. If the prompts ever became pure ASCII the tests
        above would still pass while proving nothing."""
        from tempfile import TemporaryDirectory

        from prompticorn.prompt_builder import get_prompt_builder

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            get_prompt_builder("bedrock").build(
                root,
                {
                    "spec": {"language": "python"},
                    "active_personas": ["software_engineer"],
                    "variant": "minimal",
                },
                dry_run=False,
            )
            prompts = list(root.rglob("bedrock/prompts/*.md"))
            assert prompts, "bedrock build emitted no prompt files"
            non_ascii = sum(1 for path in prompts for byte in path.read_bytes() if byte > 127)

        assert non_ascii > 0, (
            "emitted prompts are pure ASCII, so the encoding tests above no longer "
            "demonstrate a real hazard — re-check the premise"
        )
