"""The exit-code contract for `lock` and `build` (PRO-111).

Documented as a contract rather than left to whatever `click` happens to raise,
because CI scripts branch on these numbers. Changing one is a breaking change to
every pipeline that reads it.
"""

from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    """What a lock-aware command returns to the shell.

    ``UNUSABLE_LOCK`` is deliberately 3 rather than 2: `click` uses 2 for its own
    usage errors, and a lock this build cannot read is not a usage error. Reusing
    2 would make "you typed the command wrong" indistinguishable from "the lock
    is corrupt or from the future" in any script that checks.
    """

    CLEAN = 0
    DRIFT = 1
    UNUSABLE_LOCK = 3

    @property
    def meaning(self) -> str:
        """One line for `--help` and for documentation."""
        return _MEANINGS[self]


_MEANINGS: dict[ExitCode, str] = {
    ExitCode.CLEAN: "no drift; outputs match the lock",
    ExitCode.DRIFT: "the lock and reality diverge",
    ExitCode.UNUSABLE_LOCK: "the lock is corrupt, or written by a newer prompticorn",
}
