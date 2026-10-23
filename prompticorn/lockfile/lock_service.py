"""What `lock` and `build --frozen` actually do (PRO-111).

Kept out of ``cli.py`` so the behaviour is testable without a terminal, and so
the exit-code contract is decided in one place rather than scattered across
click handlers.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from prompticorn.config_handler import ConfigHandler
from prompticorn.lockfile.drift_detector import DriftDetector
from prompticorn.lockfile.drift_report import DriftReport
from prompticorn.lockfile.errors import LockError
from prompticorn.lockfile.lock_file import LockFile
from prompticorn.lockfile.lock_reader import LockReader
from prompticorn.lockfile.lock_resolver import LOCK_FILENAME, LockResolver
from prompticorn.lockfile.lock_writer import LockWriter
from prompticorn.sources.errors import SourceError

NO_LOCK_HINT = (
    "No lock file. Run `prompticorn lock` to record what this build resolved to, "
    "so future builds can detect drift."
)


@dataclass(frozen=True)
class LockOutcome:
    """The result of a lock or frozen-build attempt.

    Attributes:
        report: What diverged, if anything.
        lock: The freshly resolved lock, or None when resolution never produced
            one — an unusable lock, or a source that could not supply an
            artifact. Both are reported rather than raised, so a caller reads it
            through :attr:`resolved` once it has cleared both failure checks.
        had_existing_lock: Whether a lock was present to compare against.
        unusable_reason: Why an existing lock could not be read, if it could not.
        unavailable_reason: Why a source could not supply an artifact, if one
            could not (PRO-164). Separate from ``unusable_reason`` because the
            lock is fine and the remedy is elsewhere.
        changed: Whether writing altered the file. False on a no-op re-lock.
    """

    report: DriftReport
    lock: LockFile | None
    had_existing_lock: bool
    unusable_reason: str | None = None
    unavailable_reason: str | None = None
    changed: bool = False

    @property
    def is_unusable(self) -> bool:
        """Whether an existing lock was present but could not be read."""
        return self.unusable_reason is not None

    @property
    def is_unavailable(self) -> bool:
        """Whether a source could not supply an artifact resolution needed."""
        return self.unavailable_reason is not None

    @property
    def resolved(self) -> LockFile:
        """The freshly resolved lock, for a caller that has handled failure.

        Raises:
            LockError: If resolution never completed. Reaching this means a
                caller skipped :attr:`is_unusable` or :attr:`is_unavailable`,
                which is a defect here rather than a condition a user caused.
        """
        if self.lock is None:
            raise LockError(
                "no resolution was produced: check is_unusable and is_unavailable "
                "before reading the resolved lock"
            )
        return self.lock


class LockService:
    """Resolves, compares, and writes the lock."""

    @staticmethod
    def lock_path(root: Path) -> Path:
        """Where the lock lives, beside the manifest."""
        return root / ConfigHandler.DEFAULT_CONFIG_DIR.name / LOCK_FILENAME

    @classmethod
    def resolve_current(
        cls,
        root: Path,
        config: dict,
        resolved_at: str,
        output_paths: tuple[str, ...] = (),
        resolver: LockResolver | None = None,
        pinned_to: LockFile | None = None,
    ) -> LockFile:
        """Resolve the project at ``root`` into a lock.

        ``pinned_to`` makes resolution honour an existing lock where it can —
        see :meth:`LockResolver.resolve`.
        """
        manifest_path = (
            root / ConfigHandler.DEFAULT_CONFIG_DIR.name / ConfigHandler.DEFAULT_CONFIG_FILE
        )
        manifest_text = (
            manifest_path.read_text(encoding="utf-8") if manifest_path.is_file() else None
        )
        engine = resolver if resolver is not None else LockResolver.create()
        return engine.resolve(
            config=config,
            resolved_at=resolved_at,
            manifest_text=manifest_text,
            output_root=root,
            output_paths=output_paths,
            pinned_to=pinned_to,
        )

    @classmethod
    def inspect(
        cls,
        root: Path,
        config: dict,
        resolved_at: str,
        output_paths: tuple[str, ...] = (),
        resolver: LockResolver | None = None,
        honour_lock: bool = False,
    ) -> LockOutcome:
        """Compare the recorded lock against a fresh resolution. Writes nothing.

        Every failure is reported rather than raised, so the caller can turn it
        into the documented exit code instead of a traceback. That covers a lock
        that cannot be read and, since PRO-164, a source that cannot supply an
        artifact — which previously escaped as an exception and exited 1, the
        code that means drift.

        Args:
            honour_lock: Resolve against the recorded lock where possible rather
                than afresh (PRO-151). Set for a frozen build, which reproduces
                what the lock names. Left unset for `lock` and an ordinary
                `build`, because re-resolving is the only way a moved tag is
                noticed.
        """
        recorded: LockFile | None = None
        path = cls.lock_path(root)
        if path.exists():
            try:
                recorded = LockReader.read(path)
            except LockError as exc:
                # Returned before resolving. There is nothing to compare against,
                # so resolving would be work done to answer no question — and it
                # could fail, which is how a corrupt lock beside an unreachable
                # remote used to exit 1 with a traceback instead of the
                # documented 3 (PRO-164).
                return LockOutcome(
                    DriftReport(), None, had_existing_lock=True, unusable_reason=str(exc)
                )

        try:
            current = cls.resolve_current(
                root,
                config,
                resolved_at,
                output_paths,
                resolver,
                pinned_to=recorded if honour_lock else None,
            )
        except SourceError as exc:
            return LockOutcome(
                DriftReport(),
                None,
                had_existing_lock=recorded is not None,
                unavailable_reason=str(exc),
            )

        if recorded is None:
            return LockOutcome(DriftReport(), current, had_existing_lock=False)
        return LockOutcome(
            DriftDetector.compare(recorded, current), current, had_existing_lock=True
        )

    @classmethod
    def write(cls, root: Path, lock: LockFile) -> bool:
        """Persist a resolved lock. Returns whether the file changed."""
        return LockWriter.write(lock, cls.lock_path(root))
