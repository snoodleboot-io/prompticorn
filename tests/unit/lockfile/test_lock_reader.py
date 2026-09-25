"""Reading a lock, and refusing to read a bad one (PRO-110).

The corruption table is the load-bearing part. The lock is generated, so a fault
in it is a tooling problem — every message has to say what to *do*, not ask the
reader to fix YAML by hand.

The exception is a lock from a newer prompticorn, which is not a fault at all and
whose correct advice is the opposite of "regenerate".
"""

import pytest

from prompticorn.artifact import ArtifactId
from prompticorn.content import UnitId
from prompticorn.lockfile import (
    LOCK_SCHEMA_VERSION,
    LockCorruptError,
    LockError,
    LockFile,
    LockReader,
    LockSchemaVersionError,
    LockWriter,
)

DIGEST = "a" * 64
STAMP = "2026-08-09T02:40:00Z"

VALID = f"""\
lock_version: '{LOCK_SCHEMA_VERSION}'
prompticorn_version: 0.5.0
resolved_at: '{STAMP}'
artifacts:
- digest: {DIGEST}
  identity: acme/sec@2.1.0
  source: acme
units:
- digest: {DIGEST}
  id: agent/code
  layer: builtin
outputs:
- digest: {DIGEST}
  path: .claude/CLAUDE.md
"""


def test_a_valid_lock_parses_into_the_model() -> None:
    lock = LockReader.parse(VALID, "test")

    assert lock.prompticorn_version == "0.5.0"
    assert lock.resolved_at == STAMP
    assert lock.artifacts[0].identity == ArtifactId.parse("acme/sec@2.1.0")
    assert lock.artifacts[0].source == "acme"
    assert lock.units[0].id == UnitId.parse("agent/code")
    assert lock.units[0].layer == "builtin"
    assert lock.outputs[0].path == ".claude/CLAUDE.md"


def test_absent_sections_read_as_empty() -> None:
    """A lock for a project with nothing resolved is valid, not broken."""
    minimal = f"lock_version: '{LOCK_SCHEMA_VERSION}'\nprompticorn_version: 0.5.0\nresolved_at: '{STAMP}'\n"

    lock = LockReader.parse(minimal, "test")

    assert lock.artifacts == ()
    assert lock.units == ()
    assert lock.outputs == ()


def test_an_absent_source_is_none_not_a_string() -> None:
    lock = LockReader.parse(VALID.replace("  source: acme\n", ""), "test")

    assert lock.artifacts[0].source is None


def test_the_generated_header_is_tolerated(tmp_path) -> None:
    """The writer emits comments; the reader must not choke on its own output."""
    path = tmp_path / "prompticorn.lock"
    LockWriter.write(LockFile("0.5.0", STAMP), path)

    assert LockReader.read(path).prompticorn_version == "0.5.0"


def test_reading_a_missing_file_is_corrupt_not_a_crash(tmp_path) -> None:
    with pytest.raises(LockCorruptError):
        LockReader.read(tmp_path / "absent.lock")


# ── the corruption table ───────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("text", "reason_fragment"),
    [
        ("", "is empty"),
        ("- a\n- b\n", "is not a mapping"),
        ("key: [unclosed\n", "not valid YAML"),
        # Missing required scalars.
        (VALID.replace(f"lock_version: '{LOCK_SCHEMA_VERSION}'\n", ""), "missing 'lock_version'"),
        (VALID.replace("prompticorn_version: 0.5.0\n", ""), "missing 'prompticorn_version'"),
        (VALID.replace(f"resolved_at: '{STAMP}'\n", ""), "missing 'resolved_at'"),
        # A timestamp in a tolerated-looking but non-canonical spelling. It would
        # round-trip fine and then break re-lock stability silently.
        (VALID.replace(STAMP, "2026-08-09T02:40:00+00:00"), "ISO-8601 UTC"),
        (VALID.replace(STAMP, "not-a-time"), "ISO-8601 UTC"),
        # Wrong container shapes.
        (VALID.replace("units:\n- digest", "units:\n  digest"), "'units' must be a list"),
        # Malformed digests — worse than absent ones, since verification then
        # appears to happen while never matching anything.
        (
            VALID.replace(f"- digest: {DIGEST}\n  identity", "- digest: nope\n  identity"),
            "not a sha256 digest",
        ),
        (
            VALID.replace(f"- digest: {DIGEST}\n  id: agent", f"- digest: {'A' * 64}\n  id: agent"),
            "not a sha256 digest",
        ),
        # Delegated grammar failures keep their reason.
        (
            VALID.replace("identity: acme/sec@2.1.0", "identity: acme/sec@not-a-version"),
            "artifacts[0].identity",
        ),
        (VALID.replace("id: agent/code", "id: nonsense/code"), "units[0].id"),
        # Wrong scalar types.
        (VALID.replace("layer: builtin", "layer: 3"), "must be a string"),
    ],
)
def test_corrupt_locks_are_rejected_with_a_reason(text: str, reason_fragment: str) -> None:
    with pytest.raises(LockCorruptError) as caught:
        LockReader.parse(text, "prompticorn.lock")

    assert reason_fragment in caught.value.reason or reason_fragment in str(caught.value)


def test_the_corrupt_message_says_what_to_do() -> None:
    """A generated file's error should not read like a YAML tutorial."""
    with pytest.raises(LockCorruptError) as caught:
        LockReader.parse("", "prompticorn.lock")

    assert "prompticorn lock" in str(caught.value)
    assert "do not hand-edit" in str(caught.value)


# ── schema version ─────────────────────────────────────────────────────────────


def test_a_newer_lock_is_a_version_error_not_corruption() -> None:
    """Different fault, opposite remedy."""
    with pytest.raises(LockSchemaVersionError) as caught:
        LockReader.parse(VALID.replace(f"'{LOCK_SCHEMA_VERSION}'", "'99.0'"), "prompticorn.lock")

    assert caught.value.found == "99.0"


def test_the_version_message_warns_against_regenerating() -> None:
    """Regenerating would discard whatever the newer version recorded."""
    with pytest.raises(LockSchemaVersionError) as caught:
        LockReader.parse(VALID.replace(f"'{LOCK_SCHEMA_VERSION}'", "'99.0'"), "prompticorn.lock")

    assert "Upgrade prompticorn" in str(caught.value)
    assert "do not regenerate" in str(caught.value)


def test_the_two_error_types_are_distinguishable() -> None:
    """A caller must not have to parse the message to tell them apart."""
    assert issubclass(LockCorruptError, LockError)
    assert issubclass(LockSchemaVersionError, LockError)
    assert not issubclass(LockSchemaVersionError, LockCorruptError)


def test_the_version_is_checked_before_the_body() -> None:
    """A newer lock may hold keys this build has never heard of.

    Reporting those as corruption would send the user to regenerate a file they
    must not touch.
    """
    from_the_future = f"lock_version: '99.0'\nunknown_future_key: {{a: 1}}\n"

    with pytest.raises(LockSchemaVersionError):
        LockReader.parse(from_the_future, "prompticorn.lock")


# ── commit ids (PRO-151, tightened by PRO-164) ────────────────────────────────
#
# A commit read out of the lock becomes a cache directory name and an argument to
# `git fetch`, so the reader is the only place that can insist it is a hex id and
# nothing else. It had no test at all, and it accepted a trailing newline.


def with_commit(commit: str) -> str:
    """The valid lock, with a git artifact pinned to ``commit``."""
    return VALID.replace("  source: acme\n", f"  source: acme\n  commit: {commit}\n")


@pytest.mark.parametrize(
    ("label", "commit"),
    [("sha-1", "a" * 40), ("sha-256", "b" * 64), ("mixed hex digits", "0123456789abcdef" * 4)],
)
def test_a_well_formed_commit_id_is_accepted(label: str, commit: str) -> None:
    assert LockReader.parse(with_commit(commit), "test").artifacts[0].commit == commit


def test_a_commit_with_a_trailing_newline_is_corrupt() -> None:
    """The defect. `re.match` with `$` also matches before a trailing newline, and
    a YAML block scalar produces exactly that — so `aaa…a\\n` was accepted and
    went on to name a cache directory and to be handed to `git fetch`."""
    block_scalar = VALID.replace(
        "  source: acme\n", "  source: acme\n  commit: |\n    " + "a" * 40 + "\n"
    )

    with pytest.raises(LockCorruptError) as caught:
        LockReader.parse(block_scalar, "prompticorn.lock")

    assert "not a git commit id" in str(caught.value)


@pytest.mark.parametrize(
    ("label", "commit"),
    [
        ("one character short", "a" * 39),
        ("one character long", "a" * 41),
        ("between the two widths", "a" * 50),
        ("not hex", "z" * 40),
        ("uppercase", "A" * 40),
        ("empty", "''"),
        ("abbreviated", "a" * 7),
    ],
)
def test_a_malformed_commit_id_is_corrupt(label: str, commit: str) -> None:
    with pytest.raises(LockCorruptError):
        LockReader.parse(with_commit(commit), "prompticorn.lock")


def test_a_non_string_commit_is_corrupt() -> None:
    """A bare number is still YAML-valid, and is not a commit id."""
    with pytest.raises(LockCorruptError):
        LockReader.parse(with_commit("12345"), "prompticorn.lock")


def test_a_digest_with_a_trailing_newline_is_corrupt() -> None:
    """Same anchoring defect, same fix: digests are compared, not just stored."""
    block_scalar = VALID.replace(
        f"- digest: {DIGEST}\n  identity", "- digest: |\n    " + DIGEST + "\n  identity"
    )

    with pytest.raises(LockCorruptError):
        LockReader.parse(block_scalar, "prompticorn.lock")
