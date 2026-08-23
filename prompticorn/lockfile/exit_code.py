"""The exit-code contract for `lock`, `build` and `verify` (PRO-111, PRO-115).

Documented as a contract rather than left to whatever `click` happens to raise,
because CI scripts branch on these numbers. Changing one is a breaking change to
every pipeline that reads it.
"""

from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    """What a lock-aware command returns to the shell.

    **2 is not ours.** `click` uses it for usage errors, so nothing here may
    claim it. That is why ``UNUSABLE_LOCK`` is 3: reusing 2 would make "you typed
    the command wrong" indistinguishable from "the lock is corrupt or from the
    future" in any script that checks.

    ``TAMPERED`` is 4 for the same reason, and it matters more there. PRO-115
    originally specified 2 for it, which would have made the highest-severity
    signal in the system — a generated file edited by hand — fire on a mistyped
    flag. A supply-chain alert that cries wolf at typos is one people learn to
    ignore.
    """

    CLEAN = 0
    DRIFT = 1
    UNUSABLE_LOCK = 3
    TAMPERED = 4

    @property
    def meaning(self) -> str:
        """One line for `--help` and for documentation."""
        return _MEANINGS[self]


_MEANINGS: dict[ExitCode, str] = {
    ExitCode.CLEAN: "no drift; outputs match the lock",
    ExitCode.DRIFT: "the lock and reality diverge",
    ExitCode.UNUSABLE_LOCK: "the lock is corrupt, or written by a newer prompticorn",
    ExitCode.TAMPERED: "a generated file was modified by hand",
}
