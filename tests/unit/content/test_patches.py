"""Patch operations: edit a unit a layer does not own.

Every ambiguity is an error, never a guess — the table in PRO-119 is the
specification, and each row below is one of its cases.

Reference: PRO-119
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from prompticorn.content.builtin_content_source import BuiltinContentSource
from prompticorn.content.content_resolver import (
    ContentResolver,
    install_resolver,
    reset_default_resolver,
)
from prompticorn.content.directory_content_source import DirectoryContentSource
from prompticorn.content.errors import (
    AmbiguousPatchTargetError,
    ConflictingPatchWarning,
    MalformedConfigurationError,
    PatchMatchedNothingError,
    PatchTargetMissingError,
)
from prompticorn.content.patches import (
    AppendPatch,
    PatchApplier,
    PrependPatch,
    ReplaceSectionPatch,
)
from prompticorn.content.unit_id import UnitId

UNIT = UnitId.parse("skill/code-review-practices/minimal")

BODY = textwrap.dedent("""\
    # Code Review Practices (Minimal)

    ## Purpose
    Review changes.

    ## Core Techniques
    original body

    ## Warning Signs
    keep me
    """)


def section(content: str, heading: str = "## Core Techniques", **kwargs) -> ReplaceSectionPatch:
    kwargs.setdefault("units", "skill/*/minimal")
    kwargs.setdefault("layer", "org")
    kwargs.setdefault("index", 0)
    return ReplaceSectionPatch(content=content, heading=heading, **kwargs)


class TestOperations:
    def test_append_goes_after_everything(self):
        out = AppendPatch(units="*", content="org rule", layer="org", index=0).apply(UNIT, BODY)
        assert out.rstrip().endswith("org rule")
        assert "keep me" in out

    def test_prepend_goes_after_the_title_not_above_it(self):
        out = PrependPatch(units="*", content="org note", layer="org", index=0).apply(UNIT, BODY)
        lines = out.splitlines()
        assert lines[0].startswith("# Code Review Practices")
        assert "org note" in lines[:4]

    def test_replace_section_keeps_the_heading_and_swaps_the_body(self):
        out = section("replaced body").apply(UNIT, BODY)
        assert "## Core Techniques" in out
        assert "replaced body" in out
        assert "original body" not in out

    def test_replace_section_stops_at_the_next_same_level_heading(self):
        out = section("replaced body").apply(UNIT, BODY)
        assert "## Warning Signs" in out and "keep me" in out

    def test_replace_section_consumes_deeper_subsections(self):
        body = "## Top\nintro\n\n### Deeper\ndetail\n\n## After\nsafe\n"
        out = section("new", heading="## Top").apply(UNIT, body)
        assert "Deeper" not in out and "detail" not in out
        assert "## After" in out and "safe" in out

    def test_replace_section_matches_level_exactly(self):
        """A level-insensitive match would let a restructure relocate the rule."""
        with pytest.raises(PatchTargetMissingError):
            section("new", heading="### Core Techniques").apply(UNIT, BODY)


class TestFailureModes:
    """One test per row of the ticket's table."""

    def test_heading_absent_is_a_hard_error_naming_unit_and_heading(self):
        with pytest.raises(PatchTargetMissingError) as caught:
            section("new", heading="## Nowhere").apply(UNIT, BODY)
        message = str(caught.value)
        assert "## Nowhere" in message
        assert UNIT.render() in message
        assert "'org' layer" in message, "the author needs to know whose patch failed"

    def test_heading_twice_is_an_ambiguity_error_showing_both_lines(self):
        doubled = BODY + "\n## Core Techniques\nsecond one\n"
        with pytest.raises(AmbiguousPatchTargetError) as caught:
            section("new").apply(UNIT, doubled)
        assert len(caught.value.occurrences) == 2
        assert "ambiguous" in str(caught.value)

    def test_a_glob_matching_nothing_is_an_error(self):
        applier = PatchApplier(
            [AppendPatch(units="skill/nope/*", content="x", layer="org", index=0)]
        )
        applier.apply(UNIT, BODY)
        with pytest.raises(PatchMatchedNothingError) as caught:
            applier.verify_all_matched()
        assert "skill/nope/*" in str(caught.value)
        assert "allow_empty" in str(caught.value), "the message must offer the escape hatch"

    def test_allow_empty_makes_a_zero_match_acceptable(self):
        applier = PatchApplier(
            [AppendPatch(units="skill/nope/*", content="x", layer="org", index=0, allow_empty=True)]
        )
        applier.apply(UNIT, BODY)
        applier.verify_all_matched()

    def test_a_glob_that_matched_something_passes_verification(self):
        applier = PatchApplier(
            [AppendPatch(units="skill/*/minimal", content="x", layer="org", index=0)]
        )
        applier.apply(UNIT, BODY)
        applier.verify_all_matched()

    def test_two_patches_on_one_heading_last_wins_with_a_warning_naming_both(self):
        first = section("from org", layer="org", index=0)
        second = section("from project", layer="project", index=0)
        applier = PatchApplier([first, second])
        with pytest.warns(ConflictingPatchWarning) as recorded:
            out = applier.apply(UNIT, BODY)
        assert "from project" in out and "from org" not in out
        message = str(recorded[0].message)
        assert "'org' layer" in message and "'project' layer" in message


class TestOrdering:
    def test_patches_apply_in_the_order_given(self):
        applier = PatchApplier(
            [
                AppendPatch(units="*", content="first", layer="org", index=0),
                AppendPatch(units="*", content="second", layer="org", index=1),
            ]
        )
        out = applier.apply(UNIT, BODY)
        assert out.index("first") < out.index("second")

    def test_the_result_is_identical_across_runs(self):
        def build():
            applier = PatchApplier(
                [
                    AppendPatch(units="*", content="a", layer="org", index=0),
                    PrependPatch(units="*", content="b", layer="project", index=0),
                    section("c", layer="team", index=0),
                ]
            )
            return applier.apply(UNIT, BODY)

        assert build() == build() == build()

    def test_a_unit_no_patch_targets_is_returned_unchanged(self):
        applier = PatchApplier([AppendPatch(units="workflow/*", content="x", layer="org", index=0)])
        assert applier.apply(UNIT, BODY) == BODY


class TestDocumentShape:
    """A malformed patches.yaml fails loudly, naming the layer whose file it is."""

    def _collect(self, tmp_path: Path, document: str) -> PatchApplier:
        root = tmp_path / "content" / "configurations"
        root.mkdir(parents=True)
        (root / "patches.yaml").write_text(textwrap.dedent(document), encoding="utf-8")
        resolver = ContentResolver(
            sources=(
                DirectoryContentSource(root=tmp_path / "content", layer="project"),
                BuiltinContentSource(),
            )
        )
        return PatchApplier.collect(resolver)

    def test_a_valid_document_parses_every_operation(self, tmp_path):
        applier = self._collect(
            tmp_path,
            """
            patches:
              - op: append
                units: "skill/*/minimal"
                content: "appended"
              - op: prepend
                units: "skill/*/minimal"
                content: "prepended"
              - op: replace_section
                units: "skill/*/minimal"
                heading: "## Core Techniques"
                content: "replaced"
        """,
        )
        assert [patch.operation for patch in applier.patches] == [
            "append",
            "prepend",
            "replace_section",
        ]
        assert all(patch.layer == "project" for patch in applier.patches)

    def test_an_unknown_op_is_rejected_listing_the_known_ones(self, tmp_path):
        with pytest.raises(MalformedConfigurationError, match="expected one of"):
            self._collect(
                tmp_path,
                """
                patches:
                  - op: delete_section
                    units: "*"
                    content: "x"
            """,
            )

    def test_a_replace_section_with_no_heading_is_rejected(self, tmp_path):
        with pytest.raises(MalformedConfigurationError, match="no 'heading' to anchor to"):
            self._collect(
                tmp_path,
                """
                patches:
                  - op: replace_section
                    units: "*"
                    content: "x"
            """,
            )

    def test_an_unknown_key_is_rejected_rather_than_ignored(self, tmp_path):
        with pytest.raises(MalformedConfigurationError, match="unknown key"):
            self._collect(
                tmp_path,
                """
                patches:
                  - op: append
                    units: "*"
                    content: "x"
                    heading: "## Not valid on append"
            """,
            )

    def test_a_missing_content_is_rejected(self, tmp_path):
        with pytest.raises(MalformedConfigurationError, match="no 'content'"):
            self._collect(
                tmp_path,
                """
                patches:
                  - op: append
                    units: "*"
            """,
            )

    def test_a_non_boolean_allow_empty_is_rejected(self, tmp_path):
        with pytest.raises(MalformedConfigurationError, match="expected true or false"):
            self._collect(
                tmp_path,
                """
                patches:
                  - op: append
                    units: "*"
                    content: "x"
                    allow_empty: "yes"
            """,
            )

    def test_a_document_with_no_patches_key_is_rejected(self, tmp_path):
        with pytest.raises(MalformedConfigurationError, match="no 'patches' section"):
            self._collect(tmp_path, "something_else: []\n")

    def test_no_patches_document_anywhere_collects_nothing(self, tmp_path):
        resolver = ContentResolver(sources=(BuiltinContentSource(),))
        assert PatchApplier.collect(resolver).patches == ()


class TestCrossLayerCollection:
    """The load-bearing rule: a higher layer's replacement does not discard a
    lower layer's patch, or org enforcement would mean nothing."""

    @pytest.fixture
    def stack(self, tmp_path: Path):
        """An org layer that patches, and a project layer that replaces."""
        org = tmp_path / "org"
        (org / "configurations").mkdir(parents=True)
        (org / "configurations" / "patches.yaml").write_text(
            textwrap.dedent("""\
                patches:
                  - op: append
                    units: "skill/code-review-practices/minimal"
                    content: "ORG POLICY: two approvals required."
                """),
            encoding="utf-8",
        )
        project = tmp_path / "project"
        body = project / "skills" / "code-review-practices" / "minimal"
        body.mkdir(parents=True)
        (body / "SKILL.md").write_text(
            "# Ours (Minimal)\n\n## Purpose\nOur own version entirely.\n", encoding="utf-8"
        )
        # The project layer carries a patches.yaml too, deliberately: without
        # one, a first-wins collect() would still find the org's file and this
        # test would pass against the very bug it exists to catch.
        (project / "configurations").mkdir(parents=True)
        (project / "configurations" / "patches.yaml").write_text(
            textwrap.dedent("""\
                patches:
                  - op: append
                    units: "skill/code-review-practices/minimal"
                    content: "PROJECT NOTE: ours."
                """),
            encoding="utf-8",
        )
        # project is higher precedence, so it comes first in the source order
        return ContentResolver(
            sources=(
                DirectoryContentSource(root=project, layer="project"),
                DirectoryContentSource(root=org, layer="org"),
                BuiltinContentSource(),
            )
        )

    def test_the_lower_layers_patch_applies_to_the_replaced_unit(self, stack):
        install_resolver(stack)
        try:
            text = stack.read(UNIT)
        finally:
            reset_default_resolver()
        assert "Our own version entirely." in text, "the project's replacement still wins"
        assert "ORG POLICY: two approvals required." in text, (
            "the org's patch must survive the project's replacement"
        )
        assert "PROJECT NOTE: ours." in text, "both layers' patches apply, not just one"

    def test_patches_are_ordered_by_ascending_layer_precedence(self, tmp_path):
        """Lowest layer applies first, so the highest layer's patch lands last."""
        for name in ("low", "high"):
            root = tmp_path / name / "configurations"
            root.mkdir(parents=True)
            (root / "patches.yaml").write_text(
                f'patches:\n  - op: append\n    units: "skill/*/minimal"\n    content: "{name}"\n',
                encoding="utf-8",
            )
        resolver = ContentResolver(
            sources=(
                DirectoryContentSource(root=tmp_path / "high", layer="high"),
                DirectoryContentSource(root=tmp_path / "low", layer="low"),
                BuiltinContentSource(),
            )
        )
        applier = PatchApplier.collect(resolver)
        assert [patch.layer for patch in applier.patches] == ["low", "high"]
        out = applier.apply(UNIT, BODY)
        assert out.index("low") < out.index("high")

    def test_a_layer_with_only_patches_and_no_units_works(self, tmp_path):
        """The ticket's last criterion: a source may contribute patches alone."""
        root = tmp_path / "org" / "configurations"
        root.mkdir(parents=True)
        (root / "patches.yaml").write_text(
            'patches:\n  - op: append\n    units: "skill/*/minimal"\n    content: "only a patch"\n',
            encoding="utf-8",
        )
        resolver = ContentResolver(
            sources=(
                DirectoryContentSource(root=tmp_path / "org", layer="org"),
                BuiltinContentSource(),
            )
        )
        install_resolver(resolver)
        try:
            assert "only a patch" in resolver.read(UNIT)
        finally:
            reset_default_resolver()

    def test_a_configuration_unit_is_never_patched(self, tmp_path):
        """Patching configuration would rewrite the patch set itself."""
        root = tmp_path / "org" / "configurations"
        root.mkdir(parents=True)
        (root / "patches.yaml").write_text(
            'patches:\n  - op: append\n    units: "configuration/*"\n'
            '    content: "injected"\n    allow_empty: true\n',
            encoding="utf-8",
        )
        (root / "personas.yaml").write_text("personas: {}\n", encoding="utf-8")
        resolver = ContentResolver(
            sources=(
                DirectoryContentSource(root=tmp_path / "org", layer="org"),
                BuiltinContentSource(),
            )
        )
        install_resolver(resolver)
        try:
            assert "injected" not in resolver.read(UnitId.parse("configuration/personas"))
        finally:
            reset_default_resolver()
