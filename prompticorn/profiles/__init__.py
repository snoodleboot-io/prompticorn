"""Captured configurations, ready to apply to another project.

A profile answers "set this project up the way that one is". Files under
``~/.prompticorn/profiles`` are the authority; versions are immutable, so
comparing two of them is a real comparison and rolling back is a copy rather
than a reconstruction.
"""

from prompticorn.profiles.apply_outcome import ApplyOutcome
from prompticorn.profiles.config_diff import ConfigDiff, KeyChange
from prompticorn.profiles.errors import (
    InvalidProfileError,
    InvalidProfileNameError,
    ProfileError,
    ProfileNotFoundError,
)
from prompticorn.profiles.file_profile_store import FileProfileStore
from prompticorn.profiles.profile import FIRST_VERSION, Profile
from prompticorn.profiles.profile_service import PORTABLE_KEYS, ProfileService, portable_payload

__all__ = [
    "FIRST_VERSION",
    "PORTABLE_KEYS",
    "ApplyOutcome",
    "ConfigDiff",
    "FileProfileStore",
    "InvalidProfileError",
    "InvalidProfileNameError",
    "Profile",
    "ProfileError",
    "ProfileNotFoundError",
    "ProfileService",
    "KeyChange",
    "portable_payload",
]
