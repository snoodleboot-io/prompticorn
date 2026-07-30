"""BuiltinContentSource: the bundled tree behind the interface (PRO-104)."""

from __future__ import annotations

from pathlib import Path

import pytest

from prompticorn.content import (
    BUILTIN_LAYER,
    BuiltinContentSource,
    SourceUnavailableError,
    UnitId,
    UnitKind,
)
from tests.unit.content.content_source_contract import ContentSourceContract


@pytest.mark.unit
class TestBuiltinContentSourceContract(ContentSourceContract):
    """The bundled source must satisfy the same contract as every other."""

    @pytest.fixture
    def source(self):
        return BuiltinContentSource()


@pytest.mark.unit
class TestBuiltinContentSource:
    @pytest.fixture
    def source(self):
        return BuiltinContentSource()

    def test_enumerates_every_shipped_content_file(self, source):
        """The mapping must be total in both directions: nothing shipped is
        invisible to the resolver, and nothing enumerated is a phantom."""
        root = source.root
        on_disk = set()
        for pattern in (
            "agents/**/prompt.md",
            "agents/core/*.md",
            "skills/**/SKILL.md",
            "workflows/**/workflow.md",
            "configurations/*.yaml",
            "personas/personas.yaml",
        ):
            on_disk |= {p.resolve() for p in root.glob(pattern) if p.is_file()}

        mapped = {source.path_for(unit.id).resolve() for unit in source.units()}

        assert not sorted(on_disk - mapped), "shipped files not enumerated"
        assert not sorted(mapped - on_disk), "enumerated units with no file"

    def test_covers_every_kind_that_has_content(self, source):
        kinds = {unit.kind for unit in source.units()}
        assert kinds == set(UnitKind), f"kinds with no units: {set(UnitKind) - kinds}"

    @pytest.mark.parametrize(
        ("unit_id", "expected_suffix"),
        [
            ("agent/code", "agents/code/prompt.md"),
            ("subagent/code/feature/minimal", "agents/code/subagents/feature/minimal/prompt.md"),
            ("skill/mutation-testing/verbose", "skills/mutation-testing/verbose/SKILL.md"),
            ("workflow/code/minimal", "workflows/code/minimal/workflow.md"),
            ("convention/core/system", "agents/core/system.md"),
            ("convention/language/python", "agents/core/conventions-python.md"),
            ("configuration/languages", "configurations/languages.yaml"),
            ("configuration/personas", "personas/personas.yaml"),
        ],
    )
    def test_maps_ids_to_the_expected_paths(self, source, unit_id, expected_suffix):
        path = source.path_for(UnitId.parse(unit_id))
        assert path.as_posix().endswith(expected_suffix)
        assert path.is_file(), f"{unit_id} maps to a file that does not exist"

    def test_language_conventions_are_distinguished_from_core(self, source):
        """`conventions-python.md` is a language convention; `system.md` is a core
        one. Collapsing them would make `convention/core/python` resolve."""
        rendered = {unit.id.render() for unit in source.units()}
        assert "convention/language/python" in rendered
        assert "convention/core/system" in rendered
        assert "convention/core/conventions-python" not in rendered

    def test_core_directory_is_not_treated_as_an_agent(self, source):
        """`agents/core/` holds conventions, not an agent."""
        rendered = {unit.id.render() for unit in source.units()}
        assert "agent/core" not in rendered

    def test_reads_content_verbatim(self, source):
        unit_id = UnitId.parse("agent/code")
        assert source.read(unit_id) == source.path_for(unit_id).read_text(encoding="utf-8")

    def test_layer_is_builtin(self, source):
        assert source.name == BUILTIN_LAYER
        assert all(unit.layer == BUILTIN_LAYER for unit in source.units())

    def test_root_is_resolved_from_the_package_not_the_cwd(self, source, tmp_path, monkeypatch):
        """A CWD-relative default is silently wrong whenever the process runs
        outside the repo root — the latent defect this seam exists to remove."""
        monkeypatch.chdir(tmp_path)
        relocated = BuiltinContentSource()
        assert relocated.root == source.root
        assert list(relocated.units())

    def test_unavailable_root_raises_rather_than_reading_as_empty(self, tmp_path):
        """An unavailable source that enumerates as empty turns a broken install
        into a silently degraded build."""
        source = BuiltinContentSource(root=tmp_path / "does-not-exist")
        with pytest.raises(SourceUnavailableError) as exc:
            list(source.units())
        assert exc.value.source == BUILTIN_LAYER

    def test_empty_root_enumerates_nothing_without_error(self, tmp_path):
        """An existing but empty root is a legitimate (if useless) source — that
        is different from an absent one."""
        assert list(BuiltinContentSource(root=tmp_path).units()) == []

    def test_accepts_an_explicit_root(self, tmp_path):
        skill = tmp_path / "skills" / "example" / "minimal"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("content\n", encoding="utf-8")

        source = BuiltinContentSource(root=tmp_path)
        rendered = [unit.id.render() for unit in source.units()]
        assert rendered == ["skill/example/minimal"]
        assert source.read(UnitId.parse("skill/example/minimal")) == "content\n"

    def test_unit_count_matches_the_shipped_tree(self, source):
        """A coarse guard: a mapping change that silently halves coverage should
        fail loudly rather than merely shifting a number nobody reads."""
        units = list(source.units())
        assert len(units) > 600, f"only {len(units)} units enumerated"


@pytest.mark.unit
class TestPathTraversalSafety:
    """The grammar is the traversal control; confirm the source inherits it
    rather than re-deriving one."""

    @pytest.mark.parametrize(
        "hostile",
        [
            "skill/../../../../etc/passwd/minimal",
            "agent/../../../etc",
            "convention/core/../../../../etc/passwd",
        ],
    )
    def test_traversal_ids_never_reach_the_filesystem(self, hostile):
        from prompticorn.content import InvalidUnitIdError

        with pytest.raises(InvalidUnitIdError):
            UnitId.parse(hostile)

    def test_a_parsed_id_can_never_escape_the_root(self, tmp_path):
        """Belt and braces: every mapped path stays inside the root."""
        source = BuiltinContentSource()
        root = source.root
        for unit in source.units():
            path = source.path_for(unit.id).resolve()
            assert root in path.parents, f"{unit.id.render()} maps outside the root: {path}"


@pytest.mark.unit
class TestDefaultDigestBehaviour:
    def test_digest_defaults_to_hashing_read(self, tmp_path):
        """The ABC's default is what keeps implementations consistent; a source
        that overrides `read` gets a correct digest for free."""
        from prompticorn.content import digest_text

        skill = tmp_path / "skills" / "example" / "minimal"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("hello\r\n", encoding="utf-8")

        source = BuiltinContentSource(root=tmp_path)
        unit_id = UnitId.parse("skill/example/minimal")
        assert source.digest(unit_id) == digest_text("hello\r\n")
        # CRLF is canonicalised away, so the digest matches the LF form.
        assert source.digest(unit_id) == digest_text("hello\n")


@pytest.mark.unit
class TestPathForUnmappedInput:
    def test_path_for_returns_a_path_for_every_kind(self):
        """Every kind must map, or a unit could enumerate and then fail to read."""
        source = BuiltinContentSource()
        samples = {
            UnitKind.AGENT: "agent/code",
            UnitKind.SUBAGENT: "subagent/code/feature/minimal",
            UnitKind.SKILL: "skill/mutation-testing/minimal",
            UnitKind.WORKFLOW: "workflow/code/minimal",
            UnitKind.CONVENTION: "convention/core/system",
            UnitKind.CONFIGURATION: "configuration/languages",
        }
        assert set(samples) == set(UnitKind), "a kind has no sample here"
        for raw in samples.values():
            assert isinstance(source.path_for(UnitId.parse(raw)), Path)
