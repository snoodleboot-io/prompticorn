"""The install index's schema, and how it moves forward (PRO-128).

This is mutable state living outside git, so it needs a version and a migration
path **from the first commit**. Retrofitting one after real users have data is
the migration nobody wants to run, and the cost of doing it now is a table with
one row in it.

Migrations are a list, applied in order from whatever version the database is
at. Each is idempotent enough to survive being interrupted, because a CLI can be
killed between statements.

**Two tables the ticket lists are deliberately absent.** ``blobs`` would record
what the content-addressed store already knows authoritatively (PRO-127), and a
second record of the same thing is exactly the index-disagreeing-with-the-truth
problem this file exists to avoid. ``sources`` arrives with the ticket that
configures sources, through the migration path established here — which also
proves the path works, rather than asserting that it does.
"""

from __future__ import annotations

import sqlite3

SCHEMA_VERSION = 1

# Every statement runs inside one transaction per migration step, so a killed
# process leaves the database at the previous version rather than half-migrated.
_MIGRATIONS: tuple[tuple[int, tuple[str, ...]], ...] = (
    (
        1,
        (
            """
            CREATE TABLE IF NOT EXISTS repos (
                repo_id       TEXT PRIMARY KEY,
                path          TEXT NOT NULL,
                last_seen_at  TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS installs (
                repo_id       TEXT NOT NULL,
                artifact_id   TEXT NOT NULL,
                version       TEXT NOT NULL,
                digest        TEXT NOT NULL,
                source        TEXT,
                installed_at  TEXT NOT NULL,
                PRIMARY KEY (repo_id, artifact_id),
                FOREIGN KEY (repo_id) REFERENCES repos (repo_id) ON DELETE CASCADE
            )
            """,
            "CREATE INDEX IF NOT EXISTS installs_by_artifact ON installs (artifact_id)",
        ),
    ),
)


def current_version(connection: sqlite3.Connection) -> int:
    """The schema version this database is at.

    Uses SQLite's own ``user_version`` rather than a table of our own: it needs
    no schema to read, so a database at version 0 answers correctly instead of
    failing on a missing table.
    """
    return int(connection.execute("PRAGMA user_version").fetchone()[0])


def migrate(connection: sqlite3.Connection) -> int:
    """Bring the database up to :data:`SCHEMA_VERSION`. Returns the version.

    A database from a *newer* prompticorn is left alone and reported, not
    downgraded. Rewriting a schema this version does not understand would lose
    data that the version which wrote it can still use.
    """
    version = current_version(connection)
    if version > SCHEMA_VERSION:
        return version

    for target, statements in _MIGRATIONS:
        if target <= version:
            continue
        with connection:
            for statement in statements:
                connection.execute(statement)
            connection.execute(f"PRAGMA user_version = {target}")
        version = target
    return version
