"""Unit-ID grammar, arity, and traversal safety (PRO-103).

This validator is the single traversal-safety control that pack loading and
remote unpacking both reuse, so the rejection table is the load-bearing part of
this file — not the happy path.
"""

import pytest

from prompticorn.content import InvalidUnitIdError, UnitId, UnitKind

# Every valid form in the grammar.
#
# Arities follow the bundled tree, verified against it in PRO-104: an agent is
# authored as a single prompt.md (no variant), while skills and workflows are
# authored per variant. IDs address authored source, not rendered output.
VALID_IDS = [
    ("agent/code", UnitKind.AGENT, ("code",)),
    ("agent/orchestrator", UnitKind.AGENT, ("orchestrator",)),
    (
        "subagent/orchestrator/devops/minimal",
        UnitKind.SUBAGENT,
        ("orchestrator", "devops", "minimal"),
    ),
    (
        "skill/multiagent-orchestration/minimal",
        UnitKind.SKILL,
        ("multiagent-orchestration", "minimal"),
    ),
    (
        "workflow/async-workflow-execution/verbose",
        UnitKind.WORKFLOW,
        ("async-workflow-execution", "verbose"),
    ),
    ("convention/core/system", UnitKind.CONVENTION, ("core", "system")),
    ("convention/language/python", UnitKind.CONVENTION, ("language", "python")),
    # Underscores are in the charset, and real configuration names use them.
    ("configuration/agent_skill_mapping", UnitKind.CONFIGURATION, ("agent_skill_mapping",)),
    ("configuration/personas", UnitKind.CONFIGURATION, ("personas",)),
    # Charset edges that must be accepted: digits, dots, underscores, hyphens.
    (
        "skill/python3.14_typing-rules/verbose",
        UnitKind.SKILL,
        ("python3.14_typing-rules", "verbose"),
    ),
    ("convention/language/c-plus-plus", UnitKind.CONVENTION, ("language", "c-plus-plus")),
]

# (raw_id, substring the reason must contain). One row per hostile input class.
INVALID_IDS = [
    # Structural
    ("", "empty"),
    ("agent", "segment"),
    ("/agent/code", "absolute"),
    ("subagent//devops/minimal", "empty segment"),
    ("agent/code/", "empty segment"),
    # Traversal — the control other loaders must not re-derive
    ("agent/../../etc/passwd", "traversal"),
    ("skill/..", "traversal"),
    ("convention/language/../../../secrets", "traversal"),
    # Separator and byte smuggling
    ("agent\\code\\minimal", "backslash"),
    ("skill/foo\\bar", "backslash"),
    ("skill/foo\x00bar", "NUL"),
    # Case — a correctness requirement, not style
    ("agent/Code", "uppercase"),
    ("skill/MultiAgent/minimal", "uppercase"),
    ("Agent/code", "unknown kind"),
    # Charset
    ("skill/foo bar/minimal", "[a-z0-9]"),
    ("skill/.hidden/minimal", "[a-z0-9]"),
    ("skill/-leading-hyphen/minimal", "[a-z0-9]"),
    ("skill/foo@bar/minimal", "[a-z0-9]"),
    ("skill/café/minimal", "[a-z0-9]"),
    # Unknown kind — including the kind dropped in PRO-104, since personas.yaml
    # is one file and is addressed as configuration/personas.
    ("nonsense/foo", "unknown kind"),
    ("agents/code", "unknown kind"),
    ("persona/software_engineer", "unknown kind"),
    # Arity — an ID whose shape disagrees with how the content is authored
    ("agent/code/minimal", "segment"),  # agents have no variant on disk
    ("skill/mutation-testing", "segment"),  # skills are authored per variant
    ("workflow/code", "segment"),  # so are workflows
    ("subagent/orchestrator/devops", "segment"),
    ("workflow/a/b/c", "segment"),
    ("convention/core", "segment"),
    ("configuration/a/b", "segment"),
    # Discriminator
    ("convention/typo/general", "core, language"),
    ("convention/languages/python", "core, language"),
]


@pytest.mark.unit
class TestUnitIdParsing:
    @pytest.mark.parametrize(("raw", "kind", "segments"), VALID_IDS)
    def test_parses_valid_ids(self, raw, kind, segments):
        unit = UnitId.parse(raw)
        assert unit.kind is kind
        assert unit.segments == segments

    @pytest.mark.parametrize(("raw", "kind", "segments"), VALID_IDS)
    def test_round_trips_through_render(self, raw, kind, segments):
        assert UnitId.parse(raw).render() == raw

    @pytest.mark.parametrize(("raw", "kind", "segments"), VALID_IDS)
    def test_str_is_render(self, raw, kind, segments):
        assert str(UnitId.parse(raw)) == raw

    @pytest.mark.parametrize(("raw", "expected_reason"), INVALID_IDS)
    def test_rejects_invalid_ids(self, raw, expected_reason):
        with pytest.raises(InvalidUnitIdError) as exc:
            UnitId.parse(raw)
        assert expected_reason in exc.value.reason, (
            f"{raw!r} rejected for the wrong reason: {exc.value.reason}"
        )

    @pytest.mark.parametrize(("raw", "expected_reason"), INVALID_IDS)
    def test_error_carries_the_raw_input(self, raw, expected_reason):
        """The author needs to see what they typed, un-normalised."""
        with pytest.raises(InvalidUnitIdError) as exc:
            UnitId.parse(raw)
        assert exc.value.raw_id == raw

    def test_rejects_non_string_input(self):
        with pytest.raises(InvalidUnitIdError) as exc:
            UnitId.parse(None)  # type: ignore[arg-type]
        assert "expected a string" in exc.value.reason


@pytest.mark.unit
class TestUnitIdValueSemantics:
    def test_equal_ids_are_equal_and_hash_alike(self):
        a, b = UnitId.parse("agent/code"), UnitId.parse("agent/code")
        assert a == b
        assert hash(a) == hash(b)
        assert len({a, b}) == 1

    def test_different_ids_are_distinct(self):
        assert UnitId.parse("agent/code") != UnitId.parse("agent/review")

    def test_is_usable_as_a_dict_key(self):
        """Resolvers and lockfiles index by ID; that requires hashability."""
        index = {UnitId.parse("skill/mutation-testing/minimal"): "content"}
        assert index[UnitId.parse("skill/mutation-testing/minimal")] == "content"

    def test_is_immutable(self):
        unit = UnitId.parse("agent/code")
        with pytest.raises(Exception):
            unit.kind = UnitKind.SKILL  # type: ignore[misc]

    def test_variants_of_one_unit_are_distinct_ids(self):
        assert UnitId.parse("skill/code-review-practices/minimal") != UnitId.parse(
            "skill/code-review-practices/verbose"
        )


@pytest.mark.unit
class TestUnitKind:
    def test_every_kind_declares_arities_and_a_template(self):
        for kind in UnitKind:
            assert kind.arities, f"{kind} has no arity"
            assert all(n > 0 for n in kind.arities)
            assert kind.template, f"{kind} has no template"

    def test_only_convention_constrains_its_first_segment(self):
        constrained = {k for k in UnitKind if k.discriminators}
        assert constrained == {UnitKind.CONVENTION}

    def test_grammar_module_imports_nothing_filesystem_related(self):
        """The grammar must not learn to touch disk — parsing an ID says nothing
        about whether the content exists. Checked by inspecting the module's
        imports rather than grepping source, so a docstring mentioning a path
        cannot fail it and a real import cannot slip past it.
        """
        import ast
        from pathlib import Path

        import prompticorn.content.unit_id as module

        tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])

        forbidden = {"os", "pathlib", "shutil", "glob", "io", "tempfile"}
        assert not (imported & forbidden), (
            f"unit_id.py imports filesystem modules: {sorted(imported & forbidden)}"
        )
