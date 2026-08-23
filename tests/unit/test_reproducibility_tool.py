"""The comparison the cross-platform matrix rests on (PRO-116).

The matrix job is only as good as this function. A comparison that quietly
matches nothing — an empty reference tree, a path-separator mismatch that makes
every key differ, a read that normalises the very bytes under test — would leave
three green jobs proving nothing at all, which is worse than not running them.

So these tests are mostly about the failure modes of the *check*, not of
prompticorn: that a CRLF difference is caught, that an empty reference is an
error rather than a pass, and that the excerpt names something a reader can act
on.
"""

import importlib.util
import sys
from pathlib import Path

_TOOL_PATH = Path(__file__).resolve().parents[2] / "tools" / "reproducibility.py"


def _load_tool():
    """Import tools/reproducibility.py by path — `tools` is not a package."""
    spec = importlib.util.spec_from_file_location("_reproducibility_under_test", _TOOL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


tool = _load_tool()


class TestDifferences:
    def test_identical_trees_report_nothing(self):
        tree = {"CLAUDE.md": b"# Config\n", ".claude/agents/code.md": b"# Code\n"}

        assert tool.differences(tree, dict(tree)) == []

    def test_a_line_ending_difference_is_caught(self):
        """The difference this job exists to find, and the one that renders
        identically in every diff viewer."""
        reference = {"CLAUDE.md": b"# Config\nbody\n"}
        windows = {"CLAUDE.md": b"# Config\r\nbody\r\n"}

        report = tool.differences(reference, windows)

        assert any("byte-for-byte different" in line for line in report)
        assert any("CLAUDE.md" in line for line in report)
        assert any("\\r" in line for line in report), "the excerpt must make the CR visible"

    def test_a_missing_file_is_distinguished_from_an_extra_one(self):
        """Two different bugs. "Windows did not write it" and "Windows wrote
        something else as well" have nothing to do with each other."""
        report = tool.differences({"a.md": b"x"}, {"b.md": b"x"})

        assert any("missing on this platform" in line for line in report)
        assert any("produced only on this platform" in line for line in report)

    def test_long_reports_are_truncated_but_say_so(self):
        reference = {f"file{index}.md": b"x" for index in range(40)}

        report = tool.differences(reference, {})

        assert any("and 15 more" in line for line in report)


class TestFilesOf:
    def test_keys_are_posix_relative_paths(self, tmp_path):
        """Windows keys would differ from Linux keys in every entry, which
        reads as total failure rather than as the bug it is not."""
        nested = tmp_path / ".claude" / "agents"
        nested.mkdir(parents=True)
        (nested / "code.md").write_bytes(b"# Code\n")

        assert tool.files_of(tmp_path) == {".claude/agents/code.md": b"# Code\n"}

    def test_hidden_directories_are_included(self, tmp_path):
        """Every path in a generated tree is hidden. A walk that skipped them
        would compare an empty set and pass."""
        (tmp_path / ".prompticorn").mkdir()
        (tmp_path / ".prompticorn" / "prompticorn.lock").write_bytes(b"lock\n")

        assert ".prompticorn/prompticorn.lock" in tool.files_of(tmp_path)

    def test_content_is_read_as_bytes_not_text(self, tmp_path):
        """Reading as text would translate CRLF away and pass a tree that has
        it, which is precisely what this check is for."""
        (tmp_path / "crlf.md").write_bytes(b"a\r\nb\r\n")

        assert tool.files_of(tmp_path)["crlf.md"] == b"a\r\nb\r\n"


class TestCheckRefusesToProveNothing:
    def test_a_missing_reference_is_an_error(self, tmp_path, capsys):
        from argparse import Namespace

        code = tool.command_check(Namespace(reference=str(tmp_path / "absent")))

        assert code == 1
        assert "no reference tree" in capsys.readouterr().out

    def test_an_empty_reference_is_an_error_not_a_pass(self, tmp_path, capsys):
        """An artifact that uploaded nothing would otherwise give three green
        jobs that compared zero files."""
        from argparse import Namespace

        empty = tmp_path / "empty"
        empty.mkdir()

        code = tool.command_check(Namespace(reference=str(empty)))

        assert code == 1
        assert "empty" in capsys.readouterr().out
