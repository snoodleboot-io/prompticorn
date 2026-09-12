"""Captured configurations, ready to apply to another project.

A profile answers "set this project up the way that one is". Files under
``~/.prompticorn/profiles`` are the authority; versions are immutable, so
comparing two of them is a real comparison and rolling back is a copy rather
than a reconstruction.
"""

from prompticorn.profiles.errors import (
    InvalidProfileError,
    InvalidProfileNameError,
    ProfileError,
    ProfileNotFoundError,
)
from prompticorn.profiles.file_profile_store import FileProfileStore
from prompticorn.profiles.profile import FIRST_VERSION, Profile

__all__ = [
    "FIRST_VERSION",
    "FileProfileStore",
    "InvalidProfileError",
    "InvalidProfileNameError",
    "Profile",
    "ProfileError",
    "ProfileNotFoundError",
]
