"""Patches reach the emitted file, and a dead patch fails the build (PRO-119).

The unit tests drive PatchApplier directly. This drives the builder the CLI
runs, because the question is not "does the applier edit a string" but "does
the org's rule reach the file a tool reads" — and, separately, whether a patch
that matches nothing actually stops a build rather than being logged and
forgotten. The slot work found exactly that gap: a required slot raised
correctly and the build swallowed it, exit 0.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from prompticorn.config_handler import create_default_config
from prompticorn.content.builtin_content_source import BuiltinContentSource
from prompticorn.content.content_resolver import (
    ContentResolver,
    install_resolver,
    reset_default_resolver,
)
from prompticorn.content.directory_content_source import DirectoryContentSource
from prompticorn.content.errors import PatchMatchedNothingError, PatchTargetMissingError
from prompticorn.prompt_builder import get_prompt_builder

EMITTED = Path(".claude/skills/code-review-practices/SKILL.md")


def patches_layer(root: Path, document: str) -> Path:
    (root / "configurations").mkdir(parents=True, exist_ok=True)
    (root / "configurations" / "patches.yaml").write_text(
        textwrap.dedent(document), encoding="utf-8"
    )
    return root


def build(root: Path, output: Path) -> str:
    resolver = ContentResolver(
        sources=(DirectoryContentSource(root=root, layer="org"), BuiltinContentSource())
    )
    install_resolver(resolver)
    try:
        config = create_default_config("python")
        config["variant"] = "minimal"
        config["active_personas"] = ["fullstack_software_engineer"]
        get_prompt_builder("claude").build(output, config=config, dry_run=False)
    finally:
        reset_default_resolver()
    return (output / EMITTED).read_text(encoding="utf-8")


def test_an_appended_policy_reaches_the_emitted_file(tmp_path):
    root = patches_layer(
        tmp_path / "org",
        """
        patches:
          - op: append
            units: "skill/code-review-practices/minimal"
            content: "ORG POLICY: two approvals required."
    """,
    )
    assert "ORG POLICY: two approvals required." in build(root, tmp_path / "out")


def test_a_glob_reaches_every_matching_unit(tmp_path):
    root = patches_layer(
        tmp_path / "org",
        """
        patches:
          - op: append
            units: "skill/*/minimal"
            content: "REVIEWED BY ORG"
    """,
    )
    output = tmp_path / "out"
    build(root, output)
    skills = sorted((output / ".claude/skills").iterdir())
    assert len(skills) > 5, "the glob should have reached many skills"
    for skill in skills:
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        assert "REVIEWED BY ORG" in text, f"{skill.name} was not patched"


def test_a_patch_matching_nothing_fails_the_build(tmp_path):
    """Not logged and forgotten — the build must stop."""
    root = patches_layer(
        tmp_path / "org",
        """
        patches:
          - op: append
            units: "skill/no-such-skill/minimal"
            content: "orphaned"
    """,
    )
    with pytest.raises(PatchMatchedNothingError, match="no-such-skill"):
        build(root, tmp_path / "out")


def test_allow_empty_lets_a_conditional_patch_through(tmp_path):
    root = patches_layer(
        tmp_path / "org",
        """
        patches:
          - op: append
            units: "skill/no-such-skill/minimal"
            content: "orphaned"
            allow_empty: true
    """,
    )
    build(root, tmp_path / "out")


def test_a_missing_anchor_heading_fails_the_build(tmp_path):
    root = patches_layer(
        tmp_path / "org",
        """
        patches:
          - op: replace_section
            units: "skill/code-review-practices/minimal"
            heading: "## No Such Heading"
            content: "replaced"
    """,
    )
    with pytest.raises(PatchTargetMissingError, match="No Such Heading"):
        build(root, tmp_path / "out")
