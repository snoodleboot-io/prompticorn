"""Every generated file leaves prompticorn with LF endings (PRO-116).

Two tests, and they guard different halves of the same property. The first says
the helper does what it claims. The second says nothing bypasses it — which is
the half that decays, because ``path.write_text(...)`` is the obvious thing to
reach for and it is wrong here on exactly one platform.

That asymmetry is why a source-level assertion earns its place. A behavioural
test for CRLF can only fail on Windows, so a bypass introduced on Linux would
sit green in local runs and in every CI job but one.
"""

from __future__ import annotations

import ast
from pathlib import Path

from prompticorn.text_writer import NEWLINE, write_text

PACKAGE = Path(__file__).resolve().parents[2] / "prompticorn"

# The module that defines the rule is the one place allowed to call the
# underlying API, and the venv is not ours to police.
_EXEMPT = {"text_writer.py"}
_NOT_SOURCE = {".venv", "__pycache__"}


def _modules() -> list[Path]:
    return sorted(
        path
        for path in PACKAGE.rglob("*.py")
        if not _NOT_SOURCE & set(path.parts) and path.name not in _EXEMPT
    )


def _direct_write_text_calls(module: Path) -> list[int]:
    """Line numbers of ``<something>.write_text(...)`` calls in ``module``."""
    tree = ast.parse(module.read_text(encoding="utf-8"))
    return [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "write_text"
    ]


def _text_writes_without_newline(module: Path) -> list[int]:
    """Line numbers of ``open(..., "w")`` calls that do not pin ``newline``."""
    tree = ast.parse(module.read_text(encoding="utf-8"))
    found = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
            continue
        if node.func.id != "open":
            continue
        modes = [
            argument.value
            for argument in node.args[1:2]
            if isinstance(argument, ast.Constant) and isinstance(argument.value, str)
        ]
        keywords = {keyword.arg for keyword in node.keywords}
        writes_text = any("w" in mode or "a" in mode for mode in modes) and not any(
            "b" in mode for mode in modes
        )
        if writes_text and "newline" not in keywords:
            found.append(node.lineno)
    return found


class TestWriteText:
    def test_writes_lf_on_every_platform(self, tmp_path: Path):
        """The bytes on disk carry LF, not whatever ``os.linesep`` happens to be.

        This is the assertion that fails on Windows without the helper, and it
        is checked on the raw bytes deliberately: reading back through
        ``read_text`` would translate CRLF away and pass either way.
        """
        target = tmp_path / "output.md"

        write_text(target, "first\nsecond\n")

        assert target.read_bytes() == b"first\nsecond\n"
        assert b"\r\n" not in target.read_bytes()

    def test_newline_is_lf(self):
        """The constant is the repository's convention, not the machine's."""
        assert NEWLINE == "\n"

    def test_round_trips_through_read_text(self, tmp_path: Path):
        """What was written is what comes back."""
        target = tmp_path / "output.md"
        content = "# Title\n\nbody\n"

        write_text(target, content)

        assert target.read_text(encoding="utf-8") == content


class TestNothingBypassesTheHelper:
    def test_no_module_calls_write_text_directly(self):
        """One bypassed call is enough to put CRLF back into one file, and one
        file is enough to fail the cross-platform reproducibility matrix."""
        offenders = {
            module.relative_to(PACKAGE).as_posix(): lines
            for module in _modules()
            if (lines := _direct_write_text_calls(module))
        }

        assert not offenders, (
            "these call Path.write_text directly instead of "
            f"prompticorn.text_writer.write_text: {offenders}"
        )

    def test_no_module_opens_a_text_file_for_writing_without_pinning_newline(self):
        """``open(path, "w")`` translates line endings for the same reason."""
        offenders = {
            module.relative_to(PACKAGE).as_posix(): lines
            for module in _modules()
            if (lines := _text_writes_without_newline(module))
        }

        assert not offenders, f"these open a text file for writing without newline=: {offenders}"

    def test_the_scan_actually_finds_something(self, tmp_path: Path):
        """A scanner that silently matches nothing would pass forever.

        Without this, a refactor that renamed the attribute or moved the package
        would turn both tests above into assertions about an empty set.
        """
        planted = tmp_path / "planted.py"
        planted.write_text(
            'from pathlib import Path\n\nPath("x").write_text("y", encoding="utf-8")\n'
            'with open("z", "w", encoding="utf-8") as handle:\n    handle.write("q")\n',
            encoding="utf-8",
        )

        assert _direct_write_text_calls(planted) == [3]
        assert _text_writes_without_newline(planted) == [4]

    def test_the_package_is_where_the_test_thinks_it_is(self):
        """Guards the path above: an empty scan must mean clean, not missing."""
        assert PACKAGE.is_dir()
        assert len(_modules()) > 50

