"""`.prompticorn/provenance.json` (PRO-112).

AC 4: deterministic and sorted by path. Same reasoning as the lock — the sidecar
is committed alongside the outputs it describes, so one that reorders itself on
every run is one reviewers stop reading.
"""

import json

import pytest

from prompticorn.provenance import ProvenanceRecord, ProvenanceSidecar

RECORD_A = ProvenanceRecord("agent/code", "builtin", "0.5.0", "a" * 64)
RECORD_B = ProvenanceRecord("skill/threat-modeling/minimal", "builtin", "0.5.0", "b" * 64)


def test_entries_are_sorted_by_path() -> None:
    sidecar = ProvenanceSidecar({"z.md": RECORD_A, "a.md": RECORD_B, "m.json": RECORD_A})

    assert sidecar.paths == ("a.md", "m.json", "z.md")
    assert list(json.loads(sidecar.render())) == ["a.md", "m.json", "z.md"]


def test_insertion_order_does_not_affect_the_file() -> None:
    forward = ProvenanceSidecar({"a.md": RECORD_A, "z.md": RECORD_B})
    backward = ProvenanceSidecar({"z.md": RECORD_B, "a.md": RECORD_A})

    assert forward.render() == backward.render()


def test_rendering_is_deterministic() -> None:
    sidecar = ProvenanceSidecar({"a.md": RECORD_A})

    assert sidecar.render() == sidecar.render()


def test_record_keys_are_sorted_too() -> None:
    """Otherwise the file's bytes depend on dict construction order."""
    entry = json.loads(ProvenanceSidecar({"a.md": RECORD_A}).render())["a.md"]

    assert list(entry) == sorted(entry)


def test_the_file_ends_with_a_newline() -> None:
    """A file without one is a diff hazard in every editor that adds it back."""
    assert ProvenanceSidecar({"a.md": RECORD_A}).render().endswith("\n")


def test_it_round_trips() -> None:
    sidecar = ProvenanceSidecar({"a.md": RECORD_A, "b.json": RECORD_B})

    assert ProvenanceSidecar.parse(sidecar.render()).entries == sidecar.entries


def test_an_empty_sidecar_is_valid() -> None:
    assert ProvenanceSidecar.parse(ProvenanceSidecar({}).render()).entries == {}


def test_every_field_survives_the_round_trip() -> None:
    parsed = ProvenanceSidecar.parse(ProvenanceSidecar({"a.md": RECORD_A}).render())

    assert parsed.record_for("a.md") == RECORD_A


def test_a_missing_path_has_no_record() -> None:
    assert ProvenanceSidecar({"a.md": RECORD_A}).record_for("absent.md") is None


# ── AC 2: JSON outputs are covered here, since they carry no header ───────────


def test_json_outputs_are_covered() -> None:
    """The reason the sidecar is the general mechanism rather than a fallback."""
    sidecar = ProvenanceSidecar({".amazonq/cli-agents/build.json": RECORD_A, "CLAUDE.md": RECORD_B})

    assert sidecar.record_for(".amazonq/cli-agents/build.json") == RECORD_A
    assert set(sidecar.paths) == {".amazonq/cli-agents/build.json", "CLAUDE.md"}


# ── writing ───────────────────────────────────────────────────────────────────


def test_writing_creates_the_file_and_its_parent(tmp_path) -> None:
    path = tmp_path / ".prompticorn" / "provenance.json"

    assert ProvenanceSidecar({"a.md": RECORD_A}).write(path) is True
    assert path.is_file()


def test_writing_the_same_content_twice_is_a_no_op(tmp_path) -> None:
    path = tmp_path / "provenance.json"
    sidecar = ProvenanceSidecar({"a.md": RECORD_A})
    sidecar.write(path)
    before = path.read_bytes()

    assert sidecar.write(path) is False
    assert path.read_bytes() == before


def test_a_changed_record_rewrites_the_file(tmp_path) -> None:
    path = tmp_path / "provenance.json"
    ProvenanceSidecar({"a.md": RECORD_A}).write(path)

    assert ProvenanceSidecar({"a.md": RECORD_B}).write(path) is True


def test_reading_an_absent_sidecar_gives_an_empty_one(tmp_path) -> None:
    """A project that has never built is not a corrupt one."""
    assert ProvenanceSidecar.read(tmp_path / "absent.json").entries == {}


def test_reading_back_what_was_written(tmp_path) -> None:
    path = tmp_path / "provenance.json"
    sidecar = ProvenanceSidecar({"a.md": RECORD_A, "b.json": RECORD_B})
    sidecar.write(path)

    assert ProvenanceSidecar.read(path).entries == sidecar.entries


@pytest.mark.parametrize("payload", ["[]", '"a string"', "42"])
def test_a_non_mapping_sidecar_is_rejected(payload: str) -> None:
    with pytest.raises(ValueError, match="must be a mapping"):
        ProvenanceSidecar.parse(payload)


def test_a_record_missing_a_field_is_rejected() -> None:
    """Half a record would be believed as if it were whole."""
    with pytest.raises(KeyError):
        ProvenanceSidecar.parse('{"a.md": {"unit": "agent/code"}}')
