"""Making prompticorn's own output survive a stream that cannot encode it (PRO-116).

The CLI prints ``✓``, ``✗``, ``⚠``, ``ℹ``, arrows and box-drawing characters —
20 distinct code points that Windows' cp1252 has no room for. On a real Windows
console that is fine: Python writes through the console API in UTF-16 and every
glyph arrives. **Redirect the output and it is not.** A piped or file-redirected
stream falls back to the locale encoding, and the first ``✓`` raises
``UnicodeEncodeError`` mid-command.

So ``prompticorn build`` works and ``prompticorn build > build.log`` crashes, on
the same machine, for the same build. The cross-platform CI job found it by
capturing output; nothing that runs on a terminal ever would.

Losing a tick mark is cosmetic. Aborting a half-finished command because the
terminal cannot draw one is not — ``regenerate`` has already deleted the old tree
by the time it reports what it did.

PRO-140 settled the same question for file I/O: every read and write names its
encoding rather than inheriting the platform's. This is that rule applied to the
one pair of streams prompticorn does not open itself.
"""

from __future__ import annotations

import sys

# UTF-8 rather than the stream's own encoding, because a redirected stream has no
# opinion worth honouring — nothing is rendering those bytes as cp1252 by
# necessity, and every tool that reads a log file understands UTF-8. This is the
# direction CPython itself is going (PEP 686).
ENCODING = "utf-8"

# The backstop. If a stream refuses the encoding change, it must still never
# raise: a command that has already changed the filesystem may not die reporting
# that it did.
ERRORS = "replace"


def configure_output_streams() -> None:
    """Make stdout and stderr encode anything the CLI prints, without raising.

    Safe to call more than once, and safe on streams that are not real files —
    ``click``'s test runner and captured pipes both pass through here.
    """
    for stream in (sys.stdout, sys.stderr):
        _make_tolerant(stream)


def _make_tolerant(stream: object) -> None:
    """Reconfigure one stream, degrading rather than failing at each step."""
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is None:
        # Not a text stream we can retune — a StringIO under test, or a stream
        # somebody replaced. Nothing to do, and nothing to complain about.
        return
    try:
        reconfigure(encoding=ENCODING, errors=ERRORS)
    except (ValueError, OSError, TypeError):
        # Detached, closed, or a stream whose reconfigure takes different
        # arguments. Try the part that actually prevents the crash.
        try:
            reconfigure(errors=ERRORS)
        except (ValueError, OSError, TypeError):
            return
