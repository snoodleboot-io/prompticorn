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

``prompticorn.text_writer.write_text`` pins both the encoding and the line
ending, so calls to it are exempt (PRO-116). The exemption is deliberately
narrow — a bare ``write_text(...)`` counts only in a module that actually
imports the helper — because the scan is the only thing standing between this
rule and a call that silently reintroduces the platform default.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

_PACKAGE = Path(__file__).parent.parent.parent / "prompticorn"

# Calls that take an `encoding` argument and silently default without one.
_ENCODING_SENSITIVE = {"open", "read_text", "write_text"}

# The helper that pins encoding *and* newline for every generated file.
_SAFE_WRITER = "prompticorn.text_writer"
_SAFE_WRITER_NAME = "write_text"

# Emitted-code templates: python source we generate into the user's output. The
# same rule applies, but it cannot be caught by parsing our own AST because the
# code lives inside a string literal.
_EMITTED_TEMPLATE_SOURCES = [
    _PACKAGE / "builders" / "bedrock_builder.py",
]


def _imports_the_safe_writer(tree: ast.Module) -> bool:
    """Whether this module imports ``write_text`` from ``prompticorn.text_writer``.

    Checked rather than assumed: a module that defined its own ``write_text``
    would otherwise be exempted by name alone, which is how a scan stops
    scanning.
    """
    return any(
        isinstance(node, ast.ImportFrom)
        and node.module == _SAFE_WRITER
        and any(alias.name == _SAFE_WRITER_NAME and alias.asname is None for alias in node.names)
        for node in ast.walk(tree)
    )


def _is_binary_mode(node: ast.Call) -> bool:
    """Whether this `open` call asks for binary mode.

    `Path.open("wb")` puts the mode first; the builtin `open(path, "wb")` puts
    it second. Getting this wrong in the lenient direction exempts text writes
    that genuinely need an encoding; getting it wrong in the strict direction
    reports binary writes that can never take one.
    """
    mode_position = 0 if isinstance(node.func, ast.Attribute) else 1
    arguments = node.args[mode_position : mode_position + 1]
    return any(
        isinstance(argument, ast.Constant)
        and isinstance(argument.value, str)
        and "b" in argument.value
        for argument in arguments
    )


def _unencoded_calls(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    uses_safe_writer = _imports_the_safe_writer(tree)
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
        # A bare `write_text(path, text)` is the helper, which pins the encoding
        # itself. `path.write_text(...)` is an attribute call and still counts —
        # that is the one that defaults.
        if (
            name == _SAFE_WRITER_NAME
            and isinstance(func, ast.Name)
            and uses_safe_writer
        ):
            continue
        # Binary mode takes no encoding. The mode is the *second* argument to
        # the builtin `open(path, mode)` and the *first* to `Path.open(mode)`,
        # so the position depends on the call shape. Checking every argument
        # instead would exempt `open("blob.txt")` on the "b" in its filename.
        if name == "open" and _is_binary_mode(node):
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

    def test_the_helper_exemption_does_not_disable_the_scan(self, tmp_path):
        """A bare `write_text` is exempt only where the helper is imported, and
        `path.write_text(...)` is never exempt. Without this, the exemption
        added in PRO-116 would quietly cover every call named `write_text`."""
        unimported = tmp_path / "unimported.py"
        unimported.write_text('write_text("a", "b")\n', encoding="utf-8")

        attribute = tmp_path / "attribute.py"
        attribute.write_text(
            "from prompticorn.text_writer import write_text\n\n"
            'Path("a").write_text("b")\n',
            encoding="utf-8",
        )

        exempt = tmp_path / "exempt.py"
        exempt.write_text(
            'from prompticorn.text_writer import write_text\n\nwrite_text("a", "b")\n',
            encoding="utf-8",
        )

        assert _unencoded_calls(unimported) == ["unimported.py:1 write_text()"]
        assert _unencoded_calls(attribute) == ["attribute.py:3 write_text()"]
        assert _unencoded_calls(exempt) == []

    def test_binary_mode_is_exempt_in_both_call_shapes(self, tmp_path: Path):
        """`Path.open("wb")` puts the mode first and the builtin puts it second.
        A guard that only knew one shape reported every binary write through the
        other as missing an encoding it cannot take."""
        planted = tmp_path / "binary.py"
        planted.write_text(
            'from pathlib import Path\n\n'
            'Path("x").open("wb")\n'
            'open("x", "wb")\n',
            encoding="utf-8",
        )

        assert _unencoded_calls(planted) == []

    def test_a_filename_containing_b_is_not_mistaken_for_binary_mode(self, tmp_path: Path):
        """The lazy fix — scan every argument for a "b" — would exempt this."""
        planted = tmp_path / "textual.py"
        planted.write_text('open("blob.txt")\n', encoding="utf-8")

        assert _unencoded_calls(planted) == ["textual.py:1 open()"]

    def test_the_helper_itself_still_pins_the_encoding(self):
        """The exemption is only sound because the helper does the thing."""
        assert _unencoded_calls(_PACKAGE / "text_writer.py") == []

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
