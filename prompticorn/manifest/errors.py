"""Custom exceptions for the manifest module (PRO-109).

Mirrors ``prompticorn.content.errors`` and ``prompticorn.artifact.errors``: one
base class per module, typed subclasses carrying the context a caller needs.

The distinguishing feature here is the **key path**. A manifest is hand-edited
YAML, so "invalid version range" is not actionable on its own — the author needs
to know it was ``artifacts[1].version``. Every schema error carries one.
"""


class ManifestError(Exception):
    """Base class for every error raised by the manifest module."""


class ManifestSchemaError(ManifestError):
    """A manifest key was missing, malformed, or of the wrong type.

    Attributes:
        key_path: Dotted/indexed path to the offending key, e.g.
            ``artifacts[1].version``. The whole point of the type — an error
            without a location sends the author scanning the file by eye.
        reason: What is wrong, phrased for the person editing the YAML.
    """

    def __init__(self, key_path: str, reason: str) -> None:
        self.key_path = key_path
        self.reason = reason
        super().__init__(f"{key_path}: {reason}")


class ManifestVersionError(ManifestError):
    """The manifest declares a schema version this build cannot read.

    Distinct from :class:`ManifestSchemaError`: the file may be perfectly
    well-formed, just newer than this installation. Conflating the two would
    tell a user to fix a typo that is not there — the actual fix is to upgrade.

    Attributes:
        found: The version the manifest declares.
        supported: The versions this build understands.
    """

    def __init__(self, found: str, supported: tuple[str, ...]) -> None:
        self.found = found
        self.supported = supported
        readable = ", ".join(supported)
        super().__init__(
            f"manifest declares schema version {found!r}, which this version of "
            f"prompticorn cannot read (supported: {readable}). Upgrade prompticorn."
        )
