"""Moving a profile in and out of a file (PRO-133).

Export and import exist so a profile can be mailed, committed, or carried to
another machine — the only way a single-user store reaches a second machine
without a server.

**The round trip is byte-identical**, which means export writes exactly what the
store holds and import reads exactly what it is given. Anything that
canonicalised on the way through would make ``export`` then ``import`` a
silent edit.

**An imported file is untrusted input.** It arrived from somewhere else, so it
is parsed and validated as a profile before anything is written, and the name it
claims is checked as a name rather than used as a path.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from prompticorn.profiles.errors import InvalidProfileError
from prompticorn.profiles.file_profile_store import FileProfileStore
from prompticorn.profiles.profile import Profile


@dataclass(frozen=True)
class ProfileTransfer:
    """Reads and writes profile files outside the store.

    Attributes:
        store: Where imported profiles land and exported ones come from.
    """

    store: FileProfileStore

    def export(self, name: str, destination: Path, version: int | None = None) -> Profile:
        """Write one version of a profile to ``destination``.

        The bytes are the store's own, so importing the result reproduces the
        profile exactly.
        """
        profile = self.store.load(name, version)
        source = self.store.path_for(name, profile.version)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
        return profile

    def import_file(self, path: Path, created_at: str, name: str | None = None) -> Profile:
        """Read a profile file and store it as a new version.

        Args:
            path: The file to read.
            created_at: When this import happened.
            name: Store it under this name instead of the one in the file.

        Raises:
            InvalidProfileError: If the file is not a readable profile. Nothing
                is written — an import that half-succeeded would leave a version
                number claimed by a profile nobody can use.
            InvalidProfileNameError: If the name is not usable as a directory.
        """
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
            raise InvalidProfileError(str(path), str(error)) from error

        try:
            incoming = Profile.from_mapping(raw)
        except ValueError as error:
            raise InvalidProfileError(str(path), str(error)) from error

        target = name if name is not None else incoming.name
        # Validated before the store touches the filesystem: the name came from
        # a file somebody else wrote, and it becomes a directory.
        self.store.validate_name(target)
        return self.store.save(
            target,
            incoming.payload,
            incoming.description,
            created_at,
        )
