"""The CLI's own output must never abort a command (PRO-116).

Found by the cross-platform CI job, not by reasoning: `prompticorn regenerate`
died on Windows with `UnicodeEncodeError` on `ℹ`, *after* deleting the old
tree and rebuilding it, while printing what it had done.

The trap is that it only happens when output is redirected. A real Windows
console takes UTF-16 through the console API and every glyph arrives, so
`prompticorn build` works and `prompticorn build > build.log` crashes on the
same machine for the same build. Nothing that runs on a terminal would ever
see it.

These tests reproduce the condition on any platform, because a cp1252
`TextIOWrapper` behaves the same way everywhere.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

from prompticorn.console import configure_output_streams

# The character that actually broke the Windows job, and a few of its neighbours.
_GLYPHS = "ℹ✓✗⚠→│└"

_PACKAGE = Path(__file__).resolve().parents[2] / "prompticorn"


def _cp1252_stream() -> io.TextIOWrapper:
    """A text stream that behaves like redirected stdout on a Windows box."""
    return io.TextIOWrapper(io.BytesIO(), encoding="cp1252")


class TestThePremise:
    def test_cp1252_really_cannot_encode_what_the_cli_prints(self):
        """Guards the premise. If these ever became encodable the tests below
        would still pass while proving nothing."""
        stream = _cp1252_stream()

        with pytest.raises(UnicodeEncodeError):
            stream.write(_GLYPHS)
            stream.flush()

    def test_the_cli_still_prints_characters_cp1252_cannot_encode(self):
        """The hazard is only real while the output actually uses them."""
        unencodable = set()
        for module in _PACKAGE.rglob("*.py"):
            if "__pycache__" in module.parts:
                continue
            for character in module.read_text(encoding="utf-8"):
                if ord(character) > 127:
                    try:
                        character.encode("cp1252")
                    except UnicodeEncodeError:
                        unencodable.add(character)

        assert "ℹ" in unencodable, "the character that broke Windows is gone — recheck this test"
        assert len(unencodable) > 10


class TestConfigureOutputStreams:
    def test_a_cp1252_stream_stops_raising(self, monkeypatch):
        """The whole point: the command completes instead of dying on a glyph."""
        stream = _cp1252_stream()
        monkeypatch.setattr(sys, "stdout", stream)

        configure_output_streams()
        stream.write(_GLYPHS)
        stream.flush()

        assert stream.buffer.getvalue().decode("utf-8") == _GLYPHS

    def test_stderr_is_configured_too(self, monkeypatch):
        """Every failure path in the CLI writes to stderr, so an unconfigured
        stderr would crash exactly when something had already gone wrong."""
        stream = _cp1252_stream()
        monkeypatch.setattr(sys, "stderr", stream)

        configure_output_streams()
        stream.write(_GLYPHS)
        stream.flush()

        assert stream.buffer.getvalue().decode("utf-8") == _GLYPHS

    def test_a_stream_without_reconfigure_is_tolerated(self, monkeypatch):
        """`StringIO` has no `reconfigure`. Test harnesses substitute one, and
        configuring output must not be the thing that breaks them."""
        monkeypatch.setattr(sys, "stdout", io.StringIO())

        configure_output_streams()  # must not raise

    def test_a_closed_stream_is_tolerated(self, monkeypatch):
        stream = _cp1252_stream()
        stream.close()
        monkeypatch.setattr(sys, "stdout", stream)

        configure_output_streams()  # must not raise

    def test_calling_it_twice_is_harmless(self, monkeypatch):
        stream = _cp1252_stream()
        monkeypatch.setattr(sys, "stdout", stream)

        configure_output_streams()
        configure_output_streams()
        stream.write(_GLYPHS)
        stream.flush()

        assert stream.buffer.getvalue().decode("utf-8") == _GLYPHS


class TestTheCliWiresItUp:
    def test_the_group_callback_runs_it_before_the_subcommand(self, monkeypatch):
        """A fix that is never called is not a fix.

        Asserted through the callback rather than by watching a stream, because
        `CliRunner` substitutes its own stdout for the duration of the invoke —
        the thing under test would be hidden by the harness testing it.
        """
        from click.testing import CliRunner

        import prompticorn.cli as cli_module

        calls: list[str] = []
        monkeypatch.setattr(cli_module, "configure_output_streams", lambda: calls.append("called"))

        CliRunner().invoke(cli_module.cli, ["validate"])

        assert calls == ["called"]


@pytest.mark.unit
class TestTheRealCommandUnderCp1252:
    def test_a_command_survives_a_redirected_cp1252_stream(self):
        """The Windows failure, reproduced on any platform.

        A subprocess with `PYTHONIOENCODING=cp1252` and a piped stdout is
        precisely the condition the CI job hit: the locale encoding applies
        because nothing is a console. Without the fix this exits 1 with
        `UnicodeEncodeError` on the first tick mark.
        """
        import os
        import subprocess

        environment = {**os.environ, "PYTHONIOENCODING": "cp1252"}
        completed = subprocess.run(
            [sys.executable, "-c", "from prompticorn.cli import cli; cli()", "list"],
            capture_output=True,
            env=environment,
        )

        assert completed.returncode == 0, completed.stderr.decode("utf-8", "replace")
        assert "✓".encode() in completed.stdout, "the output no longer proves anything"
