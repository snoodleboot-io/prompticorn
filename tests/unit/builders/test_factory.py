"""Unit tests for BuilderFactory."""

import pytest

from promptosaurus.builders.base import Builder, BuildOptions
from promptosaurus.builders.errors import BuilderNotFoundError
from promptosaurus.builders.factory import BuilderFactory
from promptosaurus.ir.models import Agent


class TestBuilder(Builder):
    """Test builder for factory testing."""

    def build(self, agent: Agent, options: BuildOptions) -> str:
        return "Built with TestBuilder"

    def validate(self, agent: Agent) -> list[str]:
        return []

    def get_tool_name(self) -> str:
        return "test-tool"

    def get_output_format(self) -> str:
        return "test output"


class AnotherTestBuilder(Builder):
    """Another test builder."""

    def build(self, agent: Agent, options: BuildOptions) -> str:
        return "Built with AnotherTestBuilder"

    def validate(self, agent: Agent) -> list[str]:
        return []

    def get_tool_name(self) -> str:
        return "another-tool"

    def get_output_format(self) -> str:
        return "another output"


class TestBuilderFactoryRegistration:
    """Test builder registration in factory."""

    def test_register_builder(self):
        """Test registering a builder."""
        factory = BuilderFactory()
        factory.register("test", TestBuilder)

        assert factory.has_builder("test")

    def test_register_multiple_builders(self):
        """Test registering multiple builders."""
        factory = BuilderFactory()
        factory.register("test1", TestBuilder)
        factory.register("test2", AnotherTestBuilder)

        assert factory.has_builder("test1")
        assert factory.has_builder("test2")

    def test_register_overwrites_existing(self):
        """Test registering same builder twice."""
        factory = BuilderFactory()
        factory.register("test", TestBuilder)
        factory.register("test", AnotherTestBuilder)

        builder = factory.get_builder("test")
        result = builder.build(
            Agent(
                name="test",
                description="test",
                system_prompt="test",
                tools=[],
                skills=[],
                workflows=[],
                subagents=[],
            ),
            BuildOptions(),
        )
        assert "AnotherTestBuilder" in result


class TestBuilderFactoryGetBuilder:
    """Test getting builders from factory."""

    def test_get_builder_exists(self):
        """Test getting registered builder."""
        factory = BuilderFactory()
        factory.register("test", TestBuilder)

        builder = factory.get_builder("test")
        assert builder is not None
        assert isinstance(builder, TestBuilder)

    def test_get_builder_not_found(self):
        """Test getting non-existent builder raises error."""
        factory = BuilderFactory()

        with pytest.raises(BuilderNotFoundError):
            factory.get_builder("nonexistent")

    def test_get_builder_returns_instance(self):
        """Test get_builder returns builder instance."""
        factory = BuilderFactory()
        factory.register("test", TestBuilder)

        builder = factory.get_builder("test")
        assert builder is not None


class TestBuilderFactoryListBuilders:
    """Test listing builders in factory."""

    def setup_method(self):
        """Clear the factory before each test."""
        BuilderFactory.clear()

    def teardown_method(self):
        """Restore builtin builders after each test."""
        # Register builtin builders back for other tests
        from promptosaurus.builders.claude_builder import ClaudeBuilder
        from promptosaurus.builders.cline_builder import ClineBuilder
        from promptosaurus.builders.kilo_builder import KiloBuilder

        BuilderFactory.clear()
        BuilderFactory.register("kilo", KiloBuilder)
        BuilderFactory.register("cline", ClineBuilder)
        BuilderFactory.register("claude", ClaudeBuilder)

    def test_list_builders_empty(self):
        """Test listing builders when empty."""
        factory = BuilderFactory()
        builders = factory.list_builders()

        assert builders == []

    def test_list_builders_single(self):
        """Test listing single builder."""
        factory = BuilderFactory()
        factory.register("test", TestBuilder)

        builders = factory.list_builders()
        assert len(builders) == 1
        assert "test" in builders

    def test_list_builders_multiple(self):
        """Test listing multiple builders."""
        factory = BuilderFactory()
        factory.register("test1", TestBuilder)
        factory.register("test2", AnotherTestBuilder)

        builders = factory.list_builders()
        assert len(builders) == 2
        assert "test1" in builders
        assert "test2" in builders


class TestBuilderFactoryHasBuilder:
    """Test checking builder existence in factory."""

    def test_has_builder_exists(self):
        """Test checking existing builder."""
        factory = BuilderFactory()
        factory.register("test", TestBuilder)

        assert factory.has_builder("test") is True

    def test_has_builder_not_exists(self):
        """Test checking non-existent builder."""
        factory = BuilderFactory()

        assert factory.has_builder("nonexistent") is False


class TestBuilderFactoryClear:
    """Test clearing factory."""

    def test_clear_factory(self):
        """Test clearing all builders from factory."""
        factory = BuilderFactory()
        factory.register("test1", TestBuilder)
        factory.register("test2", AnotherTestBuilder)

        factory.clear()

        assert factory.list_builders() == []
        assert factory.has_builder("test1") is False


class TestBuilderFactoryGetBuilderInfo:
    """Test getting builder info from factory."""

    def test_get_builder_info(self):
        """Test getting builder metadata."""
        factory = BuilderFactory()
        factory.register("test", TestBuilder)

        builder = factory.get_builder("test")
        info = {
            "tool_name": builder.get_tool_name(),
            "output_format": builder.get_output_format(),
        }

        assert info["tool_name"] == "test-tool"
        assert "test output" in info["output_format"]


class TestBuilderFactoryIntegration:
    """Test factory integration scenarios."""

    def setup_method(self):
        """Clear the factory before each test."""
        BuilderFactory.clear()

    def teardown_method(self):
        """Restore builtin builders after each test."""
        # Register builtin builders back for other tests
        from promptosaurus.builders.claude_builder import ClaudeBuilder
        from promptosaurus.builders.cline_builder import ClineBuilder
        from promptosaurus.builders.kilo_builder import KiloBuilder

        BuilderFactory.clear()
        BuilderFactory.register("kilo", KiloBuilder)
        BuilderFactory.register("cline", ClineBuilder)
        BuilderFactory.register("claude", ClaudeBuilder)

    def test_full_factory_workflow(self):
        """Test full factory workflow."""
        factory = BuilderFactory()

        # Register builders
        factory.register("test1", TestBuilder)
        factory.register("test2", AnotherTestBuilder)

        # List builders
        builders = factory.list_builders()
        assert len(builders) == 2

        # Get and use builder
        for builder_name in builders:
            builder = factory.get_builder(builder_name)
            agent = Agent(
                name="test",
                description="test",
                system_prompt="test",
                tools=[],
                skills=[],
                workflows=[],
                subagents=[],
            )
            result = builder.build(agent, BuildOptions())
            assert result is not None

    def test_factory_with_multiple_operations(self):
        """Test multiple operations on factory."""
        factory = BuilderFactory()

        # Register
        factory.register("tool1", TestBuilder)
        assert factory.has_builder("tool1")

        # Get
        builder = factory.get_builder("tool1")
        assert builder is not None

        # List
        builders = factory.list_builders()
        assert "tool1" in builders

        # Clear
        factory.clear()
        assert factory.has_builder("tool1") is False
