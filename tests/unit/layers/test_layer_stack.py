"""The content layer stack (PRO-117).

`TestLayerBoundaryMatrix` is the one to read. Precedence is "higher wins" but the
resolver takes the *first* source holding a unit, so the stack must be built
highest-first. Built the other way the bundled library silently beats every
override — and a test that checks one layer at a time still passes. The matrix
puts the same unit in one, two and three layers so that mistake cannot hide.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from prompticorn.content.content_resolver import ContentResolver
from prompticorn.content.directory_content_source import DirectoryContentSource
from prompticorn.content.unit_id import UnitId
from prompticorn.layers import (
    ENABLE_VARIABLE,
    DuplicateLayerProviderError,
    Layer,
    LayerContext,
    LayerPrecedence,
    LayerProvider,
    LayerStack,
    ProjectLayerProvider,
    UserLayerProvider,
)
from tests.unit.content.content_source_contract import ContentSourceContract

SKILL = UnitId.parse("skill/testing-strategies/minimal")


def write_skill(root: Path, body: str) -> Path:
    skill = root / "skills" / "testing-strategies" / "minimal"
    skill.mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(body, encoding="utf-8")
    return root


class DirectoryProvider(LayerProvider):
    """A test provider over a directory, at any precedence."""

    def __init__(self, name: str, precedence: int, root: Path) -> None:
        self._name, self._precedence, self._root = name, precedence, root

    @property
    def name(self) -> str:
        return self._name

    @property
    def precedence(self) -> int:
        return self._precedence

    def provide(self, context: LayerContext) -> Layer | None:
        source = DirectoryContentSource(root=self._root, layer=self._name)
        return Layer(self._name, self._precedence, (source,)) if source.is_present else None


def resolver_over(tmp_path: Path, bodies: dict[str, str]) -> ContentResolver:
    """A resolver whose layers hold SKILL with the given body, by layer name."""
    precedence = {"low": 10, "mid": 30, "high": 50}
    providers = [
        DirectoryProvider(name, precedence[name], write_skill(tmp_path / name, body))
        for name, body in bodies.items()
    ]
    return LayerStack(providers=tuple(providers)).resolver(LayerContext(project_root=tmp_path))


class TestLayerBoundaryMatrix:
    @pytest.mark.parametrize(
        ("present", "winner"),
        [
            (["low"], "low"),
            (["mid"], "mid"),
            (["high"], "high"),
            (["low", "mid"], "mid"),
            (["low", "high"], "high"),
            (["mid", "high"], "high"),
            (["low", "mid", "high"], "high"),
        ],
        ids=lambda value: "+".join(value) if isinstance(value, list) else value,
    )
    def test_the_highest_layer_holding_a_unit_wins(self, tmp_path: Path, present, winner):
        resolver = resolver_over(tmp_path, {name: f"# from {name}\n" for name in present})

        assert resolver.read(SKILL) == f"# from {winner}\n"

    def test_the_winning_unit_reports_its_own_layer(self, tmp_path: Path):
        """The lock records which layer won; it must be the one that did."""
        resolver = resolver_over(tmp_path, {"low": "# low\n", "high": "# high\n"})

        assert {unit.layer for unit in resolver.units() if unit.id == SKILL} == {"high"}

    def test_bodies_are_replaced_never_merged(self, tmp_path: Path):
        """Replacement only, per the ticket. A merged body would contain both."""
        resolver = resolver_over(tmp_path, {"low": "# low only\n", "high": "# high only\n"})

        assert "low only" not in resolver.read(SKILL)


class TestDeterminism:
    def test_registration_order_does_not_change_the_winner(self, tmp_path: Path):
        low = DirectoryProvider("low", 10, write_skill(tmp_path / "low", "# low\n"))
        high = DirectoryProvider("high", 50, write_skill(tmp_path / "high", "# high\n"))
        context = LayerContext(project_root=tmp_path)

        forward = LayerStack(providers=(low, high)).resolver(context).read(SKILL)
        backward = LayerStack(providers=(high, low)).resolver(context).read(SKILL)

        assert forward == backward == "# high\n"

    def test_equal_precedence_breaks_ties_by_name(self, tmp_path: Path):
        """Never by registration order, which nobody chose."""
        a = DirectoryProvider("alpha", 30, write_skill(tmp_path / "a", "# alpha\n"))
        b = DirectoryProvider("beta", 30, write_skill(tmp_path / "b", "# beta\n"))
        context = LayerContext(project_root=tmp_path)

        assert [layer.name for layer in LayerStack(providers=(b, a)).layers(context)] == [
            "alpha",
            "beta",
        ]

    def test_two_providers_with_one_name_are_refused(self):
        class Named(LayerProvider):
            name = "same"  # type: ignore[assignment]
            precedence = 10  # type: ignore[assignment]

            def provide(self, context):
                return None

        with pytest.raises(DuplicateLayerProviderError):
            LayerStack.default(extra=[Named(), Named()])


class TestReservedSeams:
    def test_org_and_team_positions_exist_between_artifacts_and_project(self):
        assert (
            LayerPrecedence.BUILTIN
            < LayerPrecedence.ARTIFACTS
            < LayerPrecedence.ORG
            < LayerPrecedence.TEAM
            < LayerPrecedence.PROJECT
        )

    def test_a_provider_can_fill_the_org_seam_without_core_knowing_it(self, tmp_path: Path):
        """How EE plugs in: a provider at ORG precedence, supplied from outside."""
        org = DirectoryProvider("org", LayerPrecedence.ORG, write_skill(tmp_path / "org", "# org\n"))
        stack = LayerStack.default(extra=[org])

        resolver = stack.resolver(LayerContext(project_root=tmp_path / "no-project"))

        assert resolver.read(SKILL) == "# org\n"

    def test_the_project_overrides_the_org(self, tmp_path: Path):
        org = DirectoryProvider("org", LayerPrecedence.ORG, write_skill(tmp_path / "org", "# org\n"))
        project = tmp_path / "project"
        write_skill(project / ".prompticorn" / "content", "# project\n")

        resolver = LayerStack.default(extra=[org]).resolver(LayerContext(project_root=project))

        assert resolver.read(SKILL) == "# project\n"

    def test_a_core_only_install_resolves_the_bundled_library(self, tmp_path: Path):
        """No provider registered is a complete answer, not a degraded one."""
        stack = LayerStack.default()

        assert stack.describe(LayerContext(project_root=tmp_path)) == ["builtin (0)"]


class TestProjectLayer:
    def test_a_project_without_a_content_directory_has_no_project_layer(self, tmp_path: Path):
        """Most projects never create one; that must cost nothing."""
        assert ProjectLayerProvider().provide(LayerContext(project_root=tmp_path)) is None

    def test_the_project_layer_overrides_the_bundled_library(self, tmp_path: Path):
        project = tmp_path / "project"
        write_skill(project / ".prompticorn" / "content", "# ours\n")

        resolver = LayerStack.default().resolver(LayerContext(project_root=project))

        assert resolver.read(SKILL) == "# ours\n"

    def test_units_the_project_does_not_override_still_resolve(self, tmp_path: Path):
        """An override layer adds to the library; it does not replace all of it."""
        project = tmp_path / "project"
        write_skill(project / ".prompticorn" / "content", "# ours\n")

        resolver = LayerStack.default().resolver(LayerContext(project_root=project))

        assert len(resolver.units()) > 100


class TestUserLayer:
    def _context(self, tmp_path: Path, **environment: str) -> LayerContext:
        home = tmp_path / "home"
        write_skill(home / "content", "# mine\n")
        return LayerContext(
            project_root=tmp_path / "project",
            environment={"PROMPTICORN_HOME": str(home), **environment},
        )

    def test_the_user_layer_is_off_by_default(self, tmp_path: Path):
        """Machine-local content in a committed lock would read as tampering on
        every teammate's machine."""
        assert UserLayerProvider().provide(self._context(tmp_path)) is None

    @pytest.mark.parametrize("value", ["1", "true", "YES", "on"])
    def test_the_user_layer_can_be_enabled(self, tmp_path: Path, value: str):
        layer = UserLayerProvider().provide(self._context(tmp_path, **{ENABLE_VARIABLE: value}))

        assert layer is not None and layer.name == "user"

    def test_an_enabled_user_layer_wins_over_the_project(self, tmp_path: Path):
        context = self._context(tmp_path, **{ENABLE_VARIABLE: "1"})
        write_skill(context.project_root / ".prompticorn" / "content", "# project\n")

        assert LayerStack.default().resolver(context).read(SKILL) == "# mine\n"


class TestCompositeContract(ContentSourceContract):
    """The whole stack answers every question a single source does."""

    @pytest.fixture
    def source(self, tmp_path: Path) -> ContentResolver:
        project = tmp_path / "project"
        write_skill(project / ".prompticorn" / "content", "# ours\n")
        return LayerStack.default().resolver(LayerContext(project_root=project))

    def test_every_unit_declares_the_sources_layer(self, source):
        """Overridden for a composite: a unit carries the layer that *won* it,
        which is one of the stack's own layers — never the composite's name."""
        layers = {inner.name for inner in source.sources}

        for unit in source.units():
            assert unit.layer in layers
