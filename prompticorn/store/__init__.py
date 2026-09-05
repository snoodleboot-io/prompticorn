"""Machine-local state shared by every repo on this machine.

One user, one machine, no server. ``~/.prompticorn`` holds the blob cache, the
install index, saved profiles and the user content layer; a project's own truth
stays in its lock, inside the repo.
"""

from prompticorn.store.blob_store import DEFAULT_MAX_BYTES, BlobStore
from prompticorn.store.errors import BlobTooLargeError, StoreError
from prompticorn.store.store_paths import (
    HOME_VARIABLE,
    cas_root,
    cas_staging,
    database_path,
    ensure_directory,
    home,
    profiles_root,
    user_content_root,
)

__all__ = [
    "DEFAULT_MAX_BYTES",
    "HOME_VARIABLE",
    "BlobStore",
    "BlobTooLargeError",
    "StoreError",
    "cas_root",
    "cas_staging",
    "database_path",
    "ensure_directory",
    "home",
    "profiles_root",
    "user_content_root",
]
