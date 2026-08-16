"""Provenance on real generated output (PRO-112).

The unit tests pin the mechanism in isolation. These pin the thing the ticket
actually asks for: that files a *build* wrote carry provenance, that the digests
they claim describe the bytes on disk after every other pass has run, and that
the sidecar covers the JSON outputs no header can reach.

The tools here are chosen to cover the shapes rather than the list: ``claude``
writes markdown agents and skills, ``amazonq`` writes JSON agents plus rules,
``kilo-ide`` writes rules and separate workflow files, ``aider`` writes almost
nothing. The whole matrix is swept by the golden corpus, which now pins the
sidecar for every cell.
"""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from prompticorn.prompt_builder import get_prompt_builder
from prompticorn.provenance import OutputFormat, ProvenanceHeader

TOOLS = ("claude", "amazonq", "kilo-ide", "aider")

SIDECAR = ".prompticorn/provenance.json"

CONFIG = {
    "spec": {"language": "python"},
    "active_personas": ["software_engineer"],
    "variant": "minimal",
}


def build(tool: str, root: Path) -> dict[str, dict[str, str]]:
    get_prompt_builder(tool).build(root, dict(CONFIG), dry_run=False)
    return json.loads((root / SIDECAR).read_text(encoding="utf-8"))


@pytest.mark.parametrize("tool", TOOLS)
def test_the_sidecar_covers_every_file_the_build_wrote(tool: str) -> None:
    """A gap here is an audit trail with a hole in it, which is worse than none:
    the reader cannot tell an uncovered file from an unbuilt one."""
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        sidecar = build(tool, root)

        on_disk = {
            path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()
        } - {SIDECAR}

        assert on_disk == set(sidecar)


@pytest.mark.parametrize("tool", TOOLS)
def test_every_claimed_digest_describes_the_file_on_disk(tool: str) -> None:
    """Provenance runs after the ``{{PRIMARY_AGENTS_LIST}}`` pass, which rewrites
    files in place. Taken any earlier, these digests would describe bytes that no
    longer exist."""
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        sidecar = build(tool, root)

        mismatched = [
            relative
            for relative, record in sidecar.items()
            if ProvenanceHeader.body_digest(
                (root / relative).read_text(encoding="utf-8"), OutputFormat.of(relative)
            )
            != record["digest"]
        ]

        assert mismatched == []


@pytest.mark.parametrize("tool", TOOLS)
def test_commentable_outputs_carry_an_inline_header_and_json_does_not(tool: str) -> None:
    """AC 2: JSON has no comment syntax, and a `_prompticorn` key would pollute a
    schema the consuming tool validates."""
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        sidecar = build(tool, root)

        wrong: list[str] = []
        for relative in sidecar:
            text = (root / relative).read_text(encoding="utf-8")
            headed = ProvenanceHeader.has_header(text)
            if headed is (OutputFormat.of(relative) is OutputFormat.JSON):
                wrong.append(relative)

        assert wrong == []


def test_a_header_names_the_unit_its_file_came_from() -> None:
    """AC 3, at the level that matters: a skill file must say which *skill* it
    came from, not merely which agent pulled it in."""
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        sidecar = build("claude", root)

        assert sidecar[".claude/agents/code-agent.md"]["unit"] == "agent/code"
        assert (
            sidecar[".claude/skills/code-review-practices/SKILL.md"]["unit"]
            == "skill/code-review-practices/minimal"
        )
        assert sidecar["CLAUDE.md"]["unit"] == "generated/claude-md"


def test_rebuilding_over_an_existing_build_is_a_no_op() -> None:
    """Headers must not accumulate and the sidecar must not churn, or every
    rebuild produces a diff nobody can review."""
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        build("claude", root)
        first = {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }

        build("claude", root)
        second = {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }

        assert second == first


def test_a_dry_run_writes_no_sidecar() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        get_prompt_builder("claude").build(root, dict(CONFIG), dry_run=True)

        assert not (root / SIDECAR).exists()
