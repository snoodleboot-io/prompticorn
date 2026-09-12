"""Capturing a working setup, and reproducing it elsewhere (PRO-132).

The two operations the profile milestone exists for. `save_from_repo` reads a
project's manifest into a named profile; `apply` writes one back into another
project.

**`apply` routes through `ConfigHandler` rather than writing YAML itself.** That
is not tidiness: `load_config` runs the established in-place migrations, so a
profile captured against an older manifest schema is raised to the current one
for free. Writing the payload directly would need a second migration path,
which would then be free to disagree with the first.

**Nothing is written until the payload is known to be valid.** A manifest that
fails to parse should fail before it reaches the file, not after — a project
left holding a half-applied configuration is worse off than one where the
command refused.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from prompticorn.config_handler import ConfigHandler
from prompticorn.manifest.errors import ManifestError
from prompticorn.manifest.manifest_schema import ManifestSchema
from prompticorn.profiles.apply_outcome import ApplyOutcome
from prompticorn.profiles.config_diff import ConfigDiff
from prompticorn.profiles.errors import InvalidProfileError, ProfileNotFoundError
from prompticorn.profiles.file_profile_store import FileProfileStore
from prompticorn.profiles.profile import Profile

# The manifest keys a profile carries. An allowlist rather than the whole
# document, so a key that is genuinely local to one checkout cannot travel to
# another project inside a profile. Anything missing from here shows up
# immediately as generated output that differs between the source project and
# the one the profile was applied to, which is what the defining test compares.
PORTABLE_KEYS: tuple[str, ...] = (
    "version",
    "repository",
    "spec",
    "project",
    "variant",
    "active_personas",
    "ai_tool",
    "artifacts",
    "sources",
)


@dataclass(frozen=True)
class ProfileService:
    """Saves and applies profiles.

    Attributes:
        store: Where profiles live.
    """

    store: FileProfileStore

    def save_from_repo(self, name: str, root: Path, description: str, created_at: str) -> Profile:
        """Capture the manifest at ``root`` as a new version of ``name``.

        Raises:
            ProfileNotFoundError: If the project has no manifest to capture —
                reusing the error for "the thing you named is not there".
        """
        config_path = self._config_path(root)
        if not config_path.is_file():
            raise ProfileNotFoundError(f"no manifest at {config_path}")
        config = ConfigHandler.load_config(config_path)
        return self.store.save(name, portable_payload(config), description, created_at)

    def apply(
        self,
        name: str,
        root: Path,
        version: int | None = None,
        dry_run: bool = False,
    ) -> ApplyOutcome:
        """Write a profile's payload into the project at ``root``.

        Args:
            name: Profile to apply.
            root: Project directory.
            version: Which version, defaulting to the newest.
            dry_run: Report what would change and write nothing.

        Returns:
            What happened, including the diff against the previous manifest.

        Raises:
            ProfileNotFoundError: If the profile or version does not exist.
            InvalidProfileError: If its payload is not a valid manifest. Raised
                before anything is written.
        """
        profile = self.store.load(name, version)
        payload = dict(profile.payload)
        self._validate(profile, payload)

        config_path = self._config_path(root)
        existing = ConfigHandler.load_config(config_path) if config_path.is_file() else {}
        diff = ConfigDiff.between(existing, payload)

        if dry_run:
            return ApplyOutcome(
                profile=profile, diff=diff, written=False, had_existing=bool(existing)
            )

        config_path.parent.mkdir(parents=True, exist_ok=True)
        ConfigHandler.save_config(payload, config_path)
        # Re-read through the established path so an older profile picks up the
        # in-place migrations, then persist whatever they changed.
        migrated = ConfigHandler.load_config(config_path)
        if migrated != payload:
            ConfigHandler.save_config(migrated, config_path)

        return ApplyOutcome(profile=profile, diff=diff, written=True, had_existing=bool(existing))

    @staticmethod
    def _validate(profile: Profile, payload: dict[str, Any]) -> None:
        """Refuse a payload the manifest schema cannot parse."""
        try:
            ManifestSchema.parse(payload)
        except ManifestError as error:
            raise InvalidProfileError(
                str(profile), f"payload is not a valid manifest: {error}"
            ) from error

    @staticmethod
    def _config_path(root: Path) -> Path:
        return root / ConfigHandler.DEFAULT_CONFIG_DIR.name / ConfigHandler.DEFAULT_CONFIG_FILE


def portable_payload(config: dict[str, Any]) -> dict[str, Any]:
    """The subset of a manifest worth carrying to another project.

    Keys are copied in :data:`PORTABLE_KEYS` order rather than the document's,
    so two captures of the same project produce the same payload regardless of
    how either manifest happened to be written.
    """
    return {key: config[key] for key in PORTABLE_KEYS if key in config}
