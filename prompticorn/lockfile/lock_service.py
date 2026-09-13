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

NO_LOCK_HINT = (
    "No lock file. Run `prompticorn lock` to record what this build resolved to, "
    "so future builds can detect drift."
)


@dataclass(frozen=True)
class LockOutcome:
    """The result of a lock or frozen-build attempt.

    Attributes:
        report: What diverged, if anything.
        lock: The freshly resolved lock.
        had_existing_lock: Whether a lock was present to compare against.
        unusable_reason: Why an existing lock could not be read, if it could not.
        changed: Whether writing altered the file. False on a no-op re-lock.
    """

    report: DriftReport
    lock: LockFile
    had_existing_lock: bool
    unusable_reason: str | None = None
    changed: bool = False

    @property
    def is_unusable(self) -> bool:
        """Whether an existing lock was present but could not be read."""
        return self.unusable_reason is not None


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

        A lock that cannot be read is reported rather than raised, so the caller
        can turn it into the documented exit code instead of a traceback.

        Args:
            honour_lock: Resolve against the recorded lock where possible rather
                than afresh (PRO-151). Set for a frozen build, which must not
                contact a remote whose locked commit is already cached. Left
                unset for `lock` and an ordinary `build`, because re-resolving
                is the only way a moved tag is noticed.
        """
        path = cls.lock_path(root)
        recorded: LockFile | None = None
        unusable: str | None = None
        if path.exists():
            try:
                recorded = LockReader.read(path)
            except LockError as exc:
                unusable = str(exc)

        current = cls.resolve_current(
            root,
            config,
            resolved_at,
            output_paths,
            resolver,
            pinned_to=recorded if honour_lock else None,
        )

        if not path.exists():
            return LockOutcome(DriftReport(), current, had_existing_lock=False)
        if unusable is not None or recorded is None:
            return LockOutcome(
                DriftReport(), current, had_existing_lock=True, unusable_reason=unusable
            )
        return LockOutcome(
            DriftDetector.compare(recorded, current), current, had_existing_lock=True
        )

    @classmethod
    def write(cls, root: Path, lock: LockFile) -> bool:
        """Persist a resolved lock. Returns whether the file changed."""
        return LockWriter.write(lock, cls.lock_path(root))
