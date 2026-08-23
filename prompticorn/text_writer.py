r"""Writing text files that come out the same bytes on every platform (PRO-116).

CPython opens text files with ``newline=None`` by default, which translates
every ``\n`` to ``os.linesep`` on the way out. On Windows that means
``Path.write_text`` emits CRLF while the same call on Linux and macOS emits LF —
so the "same" build produces two different files.

This is easy to miss because it hides from prompticorn's own checks. Every
digest in the system is taken over text read back through ``read_text``, which
translates the endings away again, so a CRLF tree and an LF tree hash
identically and ``verify`` passes on both. Reproducibility that only holds after
normalisation is not reproducibility: the generated tree is committed, and a
team with one Windows machine gets a whole-repository diff every time that
machine runs a build.

Every write of generated text goes through here so the bytes themselves match.
``tests/unit/test_text_writer.py`` asserts that no module reaches for
``Path.write_text`` directly, because a single call that skips this is enough to
put CRLF back into one file, and one file is all it takes to fail the
cross-platform matrix.
"""

from __future__ import annotations

from pathlib import Path

# The one line ending prompticorn emits, on every platform. Not os.linesep: the
# output is committed to a repository shared across machines, so it belongs to
# the repository's conventions rather than to whichever machine last ran a build.
NEWLINE = "\n"

ENCODING = "utf-8"


def write_text(path: Path, content: str) -> None:
    r"""Write ``content`` to ``path`` as UTF-8 with LF line endings.

    Args:
        path: File to write. Its parent must already exist, as with
            ``Path.write_text`` — creating it here would hide a builder writing
            somewhere it did not mean to.
        content: The text to write. Any ``\n`` it contains is written literally.
    """
    path.write_text(content, encoding=ENCODING, newline=NEWLINE)
