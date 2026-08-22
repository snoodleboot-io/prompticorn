"""The pass that attaches provenance to a finished build's outputs (PRO-112).

What these pin is the contract the emitter has to hold for AC 2 and AC 3 to be
true of real generated files: JSON is covered by the sidecar and left otherwise
untouched, everything else gets a header that names its unit, and the digest a
file claims is the digest of the file as it ends up on disk.
"""

import json

import pytest

from prompticorn.provenance import (
    GENERATED_UNIT_PREFIX,
    OutputFormat,
    ProvenanceEmitter,
    ProvenanceHeader,
    ProvenanceSidecar,
)

EMITTER = ProvenanceEmitter(layer="builtin", version="1.2.3")


def write(root, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sidecar_of(root) -> ProvenanceSidecar:
    return ProvenanceSidecar.read(root / ".prompticorn" / "provenance.json")


def test_the_sidecar_path_is_returned_so_the_caller_can_report_it(tmp_path) -> None:
    write(tmp_path, "a.md", "# A\n")

    assert EMITTER.emit(tmp_path, {"a.md": "agent/a"}) == [".prompticorn/provenance.json"]


def test_a_markdown_output_gains_a_header_naming_its_unit(tmp_path) -> None:
    write(tmp_path, ".claude/agents/code.md", "# Code\n")

    EMITTER.emit(tmp_path, {".claude/agents/code.md": "agent/code"})

    record = ProvenanceHeader.parse((tmp_path / ".claude/agents/code.md").read_text())
    assert record is not None
    assert record.unit == "agent/code"
    assert record.layer == "builtin"
    assert record.version == "1.2.3"


def test_the_body_survives_the_header(tmp_path) -> None:
    write(tmp_path, "a.md", "# A\n\nbody\n")

    EMITTER.emit(tmp_path, {"a.md": "agent/a"})

    text = (tmp_path / "a.md").read_text()
    assert ProvenanceHeader.strip(text, OutputFormat.MARKDOWN) == "# A\n\nbody\n"


def test_the_claimed_digest_matches_the_file_as_written(tmp_path) -> None:
    """The self-reference property, end to end: a verifier reading the file back
    must be able to recompute what the header claims."""
    write(tmp_path, "a.md", "# A\n\nbody\n")

    EMITTER.emit(tmp_path, {"a.md": "agent/a"})

    text = (tmp_path / "a.md").read_text()
    record = ProvenanceHeader.parse(text)
    assert record is not None
    assert record.digest == ProvenanceHeader.body_digest(text, OutputFormat.MARKDOWN)


def test_json_is_left_byte_identical(tmp_path) -> None:
    """AC 2: a `_prompticorn` key or a comment would pollute a schema the
    consuming tool validates."""
    original = json.dumps({"name": "code"}, indent=2) + "\n"
    write(tmp_path, ".amazonq/cli-agents/code.json", original)

    EMITTER.emit(tmp_path, {".amazonq/cli-agents/code.json": "agent/code"})

    assert (tmp_path / ".amazonq/cli-agents/code.json").read_text() == original


def test_json_is_still_covered_by_the_sidecar(tmp_path) -> None:
    write(tmp_path, "a.json", '{"a": 1}\n')

    EMITTER.emit(tmp_path, {"a.json": "agent/a"})

    record = sidecar_of(tmp_path).record_for("a.json")
    assert record is not None
    assert record.unit == "agent/a"


@pytest.mark.parametrize(
    ("relative", "prefix"),
    [("a.md", "<!--"), ("a.yaml", "#"), ("a.yml", "#"), ("a.toml", "#")],
)
def test_each_commentable_format_uses_its_own_comment_syntax(tmp_path, relative, prefix) -> None:
    write(tmp_path, relative, "body\n")

    EMITTER.emit(tmp_path, {relative: "agent/a"})

    assert (tmp_path / relative).read_text().startswith(prefix)


def test_rerunning_the_pass_changes_nothing(tmp_path) -> None:
    """Rebuilds must not accumulate headers or churn the digest."""
    write(tmp_path, "a.md", "# A\n")
    attribution = {"a.md": "agent/a"}

    EMITTER.emit(tmp_path, attribution)
    once = (tmp_path / "a.md").read_text()
    once_sidecar = (tmp_path / ".prompticorn/provenance.json").read_text()
    EMITTER.emit(tmp_path, attribution)

    assert (tmp_path / "a.md").read_text() == once
    assert (tmp_path / ".prompticorn/provenance.json").read_text() == once_sidecar


def test_the_sidecar_covers_every_attributed_output(tmp_path) -> None:
    write(tmp_path, "a.md", "a\n")
    write(tmp_path, "b.json", "{}\n")
    write(tmp_path, "c.toml", "c = 1\n")

    EMITTER.emit(tmp_path, {"a.md": "agent/a", "b.json": "agent/b", "c.toml": "agent/c"})

    assert sidecar_of(tmp_path).paths == ("a.md", "b.json", "c.toml")


def test_a_missing_file_is_omitted_rather_than_raising(tmp_path) -> None:
    """A build that already succeeded must not be failed by the bookkeeping pass
    that describes it."""
    write(tmp_path, "a.md", "a\n")

    EMITTER.emit(tmp_path, {"a.md": "agent/a", "gone.md": "agent/gone"})

    assert sidecar_of(tmp_path).paths == ("a.md",)


def test_a_unit_containing_whitespace_cannot_break_the_header(tmp_path) -> None:
    """`to_header_body` neither quotes nor escapes, so whitespace in a value
    would render a header that parses back as something else."""
    write(tmp_path, "a.md", "a\n")

    EMITTER.emit(tmp_path, {"a.md": "agent/one two"})

    record = ProvenanceHeader.parse((tmp_path / "a.md").read_text())
    assert record is not None
    assert record.unit == "agent/one_two"


def test_an_aggregate_output_is_named_as_generated(tmp_path) -> None:
    write(tmp_path, "AGENTS.md", "# Agents\n")

    EMITTER.emit(tmp_path, {"AGENTS.md": f"{GENERATED_UNIT_PREFIX}/agents-md"})

    record = sidecar_of(tmp_path).record_for("AGENTS.md")
    assert record is not None
    assert record.unit == "generated/agents-md"


def test_an_empty_build_still_writes_a_sidecar(tmp_path) -> None:
    """Absence of the file would be indistinguishable from provenance never
    having run."""
    EMITTER.emit(tmp_path, {})

    assert (tmp_path / ".prompticorn/provenance.json").is_file()
    assert sidecar_of(tmp_path).paths == ()
