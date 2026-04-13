"""Unit tests for ComponentSelector and ComponentComposer."""

import tempfile
from pathlib import Path

import pytest

from promptosaurus.builders.component_selector import ComponentBundle, ComponentSelector, Variant
from promptosaurus.builders.errors import ComponentNotFoundError


@pytest.fixture
def temp_agents_dir():
    """Create temporary agents directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_agent_with_variants(temp_agents_dir):
    """Create test agent with minimal and verbose variants."""
    # Minimal variant
    minimal_dir = temp_agents_dir / "test-agent" / "minimal"
    minimal_dir.mkdir(parents=True)
    (minimal_dir / "prompt.md").write_text("---\nname: test\n---\nMinimal prompt")
    (minimal_dir / "skills.md").write_text("---\nname: skill1\n---\n")
    (minimal_dir / "workflow.md").write_text("---\nname: wf1\n---\n")

    # Verbose variant
    verbose_dir = temp_agents_dir / "test-agent" / "verbose"
    verbose_dir.mkdir(parents=True)
    (verbose_dir / "prompt.md").write_text("---\nname: test\n---\nVerbose prompt with details")
    (verbose_dir / "skills.md").write_text("---\nname: skill1\n---\n")
    (verbose_dir / "workflow.md").write_text("---\nname: wf1\n---\n")

    return temp_agents_dir


@pytest.fixture
def test_agent_minimal_only(temp_agents_dir):
    """Create test agent with only minimal variant."""
    minimal_dir = temp_agents_dir / "minimal-agent" / "minimal"
    minimal_dir.mkdir(parents=True)
    (minimal_dir / "prompt.md").write_text("---\nname: test\n---\nMinimal")

    return temp_agents_dir


class TestVariantEnum:
    """Test Variant enum."""

    def test_variant_minimal(self):
        """Test MINIMAL variant."""
        assert Variant.MINIMAL.value == "minimal"

    def test_variant_verbose(self):
        """Test VERBOSE variant."""
        assert Variant.VERBOSE.value == "verbose"

    def test_variant_count(self):
        """Test variant count."""
        variants = list(Variant)
        assert len(variants) == 2


class TestComponentSelectorInitialization:
    """Test ComponentSelector initialization."""

    def test_selector_with_default_agent_dir(self, temp_agents_dir):
        """Test selector with default agents directory."""
        selector = ComponentSelector(str(temp_agents_dir))

        assert selector.agents_dir == temp_agents_dir

    def test_selector_with_custom_agent_dir(self, test_agent_with_variants):
        """Test selector with custom agents directory."""
        selector = ComponentSelector(str(test_agent_with_variants))

        assert selector.agents_dir is not None


class TestComponentSelectorSelectVariant:
    """Test variant selection."""

    def test_select_minimal_variant(self, test_agent_with_variants):
        """Test selecting minimal variant."""
        from promptosaurus.ir.models import Agent

        selector = ComponentSelector(str(test_agent_with_variants))
        agent = Agent(
            name="test-agent",
            description="Test agent",
            system_prompt="You are a test",
            tools=[],
            skills=[],
            workflows=[],
            subagents=[],
        )
        bundle = selector.select(agent, Variant.MINIMAL)

        assert bundle is not None
        assert isinstance(bundle, ComponentBundle)

    def test_select_verbose_variant(self, test_agent_with_variants):
        """Test selecting verbose variant."""
        from promptosaurus.ir.models import Agent

        selector = ComponentSelector(str(test_agent_with_variants))
        agent = Agent(
            name="test-agent",
            description="Test agent",
            system_prompt="You are a test",
            tools=[],
            skills=[],
            workflows=[],
            subagents=[],
        )
        bundle = selector.select(agent, Variant.VERBOSE)

        assert bundle is not None

    def test_select_nonexistent_agent(self, test_agent_with_variants):
        """Test selecting from non-existent agent."""
        from promptosaurus.ir.models import Agent

        selector = ComponentSelector(str(test_agent_with_variants))
        agent = Agent(
            name="nonexistent",
            description="Test agent",
            system_prompt="You are a test",
            tools=[],
            skills=[],
            workflows=[],
            subagents=[],
        )

        with pytest.raises((ComponentNotFoundError, Exception)):
            selector.select(agent, Variant.MINIMAL)

    def test_select_nonexistent_variant_falls_back(self, test_agent_with_variants):
        """Test selecting minimal when not available falls back to verbose."""
        from promptosaurus.ir.models import Agent

        selector = ComponentSelector(str(test_agent_with_variants))

        # First, remove minimal variant to test fallback
        import shutil

        minimal_path = test_agent_with_variants / "test-agent" / "minimal"
        shutil.rmtree(minimal_path)

        agent = Agent(
            name="test-agent",
            description="Test agent",
            system_prompt="You are a test",
            tools=[],
            skills=[],
            workflows=[],
            subagents=[],
        )

        # Request minimal, but only verbose exists - should fall back
        bundle = selector.select(agent, Variant.MINIMAL)

        # Should fall back to verbose
        assert bundle is not None
        assert bundle.fallback_used is True
        assert bundle.variant == Variant.VERBOSE


class TestComponentSelectorCheckVariantExists:
    """Test checking variant existence."""

    def test_variant_exists(self, test_agent_with_variants):
        """Test checking existing variant."""
        selector = ComponentSelector(str(test_agent_with_variants))

        assert selector.variant_exists("test-agent", Variant.MINIMAL)
        assert selector.variant_exists("test-agent", Variant.VERBOSE)

    def test_variant_not_exists(self, test_agent_with_variants):
        """Test checking non-existent variant."""
        selector = ComponentSelector(str(test_agent_with_variants))

        # Agent doesn't exist
        assert not selector.variant_exists("nonexistent", Variant.MINIMAL)

    def test_variant_not_exists_for_agent(self, test_agent_minimal_only):
        """Test variant doesn't exist for agent."""
        selector = ComponentSelector(str(test_agent_minimal_only))

        # Agent has minimal but not verbose
        assert selector.variant_exists("minimal-agent", Variant.MINIMAL)
        assert not selector.variant_exists("minimal-agent", Variant.VERBOSE)


class TestComponentSelectorListVariants:
    """Test listing available variants."""

    def test_list_variants_both(self, test_agent_with_variants):
        """Test listing all available variants."""
        selector = ComponentSelector(str(test_agent_with_variants))
        variants = selector.list_available_variants("test-agent")

        assert len(variants) == 2
        assert Variant.MINIMAL in variants
        assert Variant.VERBOSE in variants

    def test_list_variants_minimal_only(self, test_agent_minimal_only):
        """Test listing when only minimal exists."""
        selector = ComponentSelector(str(test_agent_minimal_only))
        variants = selector.list_available_variants("minimal-agent")

        assert len(variants) == 1
        assert Variant.MINIMAL in variants

    def test_list_variants_nonexistent_agent(self, test_agent_with_variants):
        """Test listing variants for non-existent agent."""
        selector = ComponentSelector(str(test_agent_with_variants))
        variants = selector.list_available_variants("nonexistent")

        assert variants == []


class TestComponentBundle:
    """Test ComponentBundle namedtuple."""

    def test_bundle_creation(self):
        """Test creating component bundle."""
        bundle = ComponentBundle(
            variant=Variant.MINIMAL,
            prompt="Minimal prompt content",
            skills="Minimal skills content",
            workflow="Minimal workflow content",
        )

        assert bundle.prompt == "Minimal prompt content"
        assert bundle.skills == "Minimal skills content"
        assert bundle.workflow == "Minimal workflow content"
        assert bundle.variant == Variant.MINIMAL

    def test_bundle_with_none_optional(self):
        """Test bundle with None optional components."""
        bundle = ComponentBundle(
            variant=Variant.VERBOSE,
            prompt="Verbose prompt content",
            skills=None,
            workflow=None,
        )

        assert bundle.prompt is not None
        assert bundle.skills is None
        assert bundle.workflow is None
        assert bundle.variant == Variant.VERBOSE


class TestComponentSelectorIntegration:
    """Test selector integration scenarios."""

    def test_full_selection_workflow(self, test_agent_with_variants):
        """Test full variant selection workflow."""
        from promptosaurus.ir.models import Agent

        selector = ComponentSelector(str(test_agent_with_variants))
        agent = Agent(
            name="test-agent",
            description="Test agent",
            system_prompt="You are a test",
            tools=[],
            skills=[],
            workflows=[],
            subagents=[],
        )

        # Check variants exist
        assert selector.variant_exists("test-agent", Variant.MINIMAL)

        # Select variant
        bundle = selector.select(agent, Variant.MINIMAL)
        assert bundle is not None

        # Verify bundle content
        assert bundle.prompt is not None

    def test_fallback_workflow(self, test_agent_with_variants):
        """Test fallback when minimal variant doesn't exist."""
        from promptosaurus.ir.models import Agent

        selector = ComponentSelector(str(test_agent_with_variants))

        # First, remove minimal variant to test fallback
        import shutil

        minimal_path = test_agent_with_variants / "test-agent" / "minimal"
        shutil.rmtree(minimal_path)

        agent = Agent(
            name="test-agent",
            description="Test agent",
            system_prompt="You are a test",
            tools=[],
            skills=[],
            workflows=[],
            subagents=[],
        )

        # Request minimal but only verbose exists - should fall back to verbose
        bundle = selector.select(agent, Variant.MINIMAL)
        assert bundle is not None
        assert bundle.fallback_used is True

    def test_list_and_select(self, test_agent_with_variants):
        """Test listing variants then selecting."""
        from promptosaurus.ir.models import Agent

        selector = ComponentSelector(str(test_agent_with_variants))
        agent = Agent(
            name="test-agent",
            description="Test agent",
            system_prompt="You are a test",
            tools=[],
            skills=[],
            workflows=[],
            subagents=[],
        )

        # List available variants
        variants = selector.list_available_variants("test-agent")
        assert len(variants) > 0

        # Select each variant
        for variant in variants:
            bundle = selector.select(agent, variant)
            assert bundle is not None
