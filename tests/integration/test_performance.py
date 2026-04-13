"""Performance testing for prompt builders.

Tests measure execution time and memory usage for:
- Single agent build with all 5 tools
- Multiple agents with all 5 tools
- Builder comparison (execution time per tool)
- Scaling tests (5, 10, 15, 20 agents)

Benchmarks establish performance baselines and identify bottlenecks.
"""

import time
import tracemalloc
from collections.abc import Generator
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from promptosaurus.builders.base import AbstractBuilder, BuildOptions
from promptosaurus.builders.claude_builder import ClaudeBuilder
from promptosaurus.builders.cline_builder import ClineBuilder
from promptosaurus.builders.copilot_builder import CopilotBuilder
from promptosaurus.builders.cursor_builder import CursorBuilder
from promptosaurus.builders.kilo_builder import KiloBuilder
from promptosaurus.ir.models import Agent

# Performance targets (in seconds)
TARGET_SINGLE_TOOL = 2.0  # <2 seconds per tool
TARGET_ALL_TOOLS_SINGLE_AGENT = 10.0  # <10 seconds for all 5 tools, 1 agent
TARGET_ALL_TOOLS_10_AGENTS = 100.0  # <100 seconds for 10 agents, all tools


def create_test_agent(name: str, index: int = 0) -> Agent:
    """Create a test agent with realistic components.

    Args:
        name: Agent name
        index: Agent index (used for variant generation)

    Returns:
        Agent with tools, skills, workflows
    """
    return Agent(
        name=name,
        description=f"Test agent {index}",
        system_prompt=f"You are a test agent {index}.\n" * 50,  # Realistic size
        tools=[f"tool_{i}" for i in range(5)],
        skills=["skill_1", "skill_2"],
        workflows=["workflow_1", "workflow_2"],
        subagents=["subagent_1", "subagent_2"],
    )


def create_test_agents_directory(temp_dir: str | Path, agent_count: int = 5) -> Path:
    """Create test agents directory with multiple agents.

    Args:
        temp_dir: Temporary directory
        agent_count: Number of agents to create

    Returns:
        Path to agents directory
    """
    agents_path = Path(temp_dir) / "agents"
    agents_path.mkdir(exist_ok=True)

    for i in range(agent_count):
        agent_name = f"agent_{i}"

        # Create minimal variant
        minimal_dir = agents_path / agent_name / "minimal"
        minimal_dir.mkdir(parents=True, exist_ok=True)
        (minimal_dir / "prompt.md").write_text(
            f"# {agent_name.title()} Agent\n\n## system_prompt\n\nYou are test agent {i}.\n" * 20
        )

        # Create verbose variant
        verbose_dir = agents_path / agent_name / "verbose"
        verbose_dir.mkdir(parents=True, exist_ok=True)
        (verbose_dir / "prompt.md").write_text(
            f"# {agent_name.title()} Agent (Verbose)\n\n"
            f"## system_prompt\n\n"
            f"You are a comprehensive test agent {i}.\n" * 50
        )

    return agents_path


@pytest.fixture(scope="session")
def builders_and_agents_1() -> Generator[
    tuple[dict[str, AbstractBuilder], Agent, Path], None, None
]:
    """Session-scoped fixture: 1 agent with all builders."""
    with TemporaryDirectory() as temp_dir:
        agents_dir = create_test_agents_directory(temp_dir, 1)
        builders = {
            "kilo": KiloBuilder(agents_dir=agents_dir),
            "claude": ClaudeBuilder(agents_dir=agents_dir),
            "cline": ClineBuilder(agents_dir=agents_dir),
            "cursor": CursorBuilder(agents_dir=agents_dir),
            "copilot": CopilotBuilder(agents_dir=agents_dir),
        }
        agent = create_test_agent("agent_0", 0)
        yield builders, agent, agents_dir


@pytest.fixture(scope="session")
def builders_and_agents_5() -> Generator[
    tuple[dict[str, AbstractBuilder], list[Agent], Path], None, None
]:
    """Session-scoped fixture: 5 agents with all builders."""
    with TemporaryDirectory() as temp_dir:
        agents_dir = create_test_agents_directory(temp_dir, 5)
        builders = {
            "kilo": KiloBuilder(agents_dir=agents_dir),
            "claude": ClaudeBuilder(agents_dir=agents_dir),
            "cline": ClineBuilder(agents_dir=agents_dir),
            "cursor": CursorBuilder(agents_dir=agents_dir),
            "copilot": CopilotBuilder(agents_dir=agents_dir),
        }
        agents = [create_test_agent(f"agent_{i}", i) for i in range(5)]
        yield builders, agents, agents_dir


@pytest.fixture(scope="session")
def builders_and_agents_10() -> Generator[
    tuple[dict[str, AbstractBuilder], list[Agent], Path], None, None
]:
    """Session-scoped fixture: 10 agents with all builders."""
    with TemporaryDirectory() as temp_dir:
        agents_dir = create_test_agents_directory(temp_dir, 10)
        builders = {
            "kilo": KiloBuilder(agents_dir=agents_dir),
            "claude": ClaudeBuilder(agents_dir=agents_dir),
            "cline": ClineBuilder(agents_dir=agents_dir),
            "cursor": CursorBuilder(agents_dir=agents_dir),
            "copilot": CopilotBuilder(agents_dir=agents_dir),
        }
        agents = [create_test_agent(f"agent_{i}", i) for i in range(10)]
        yield builders, agents, agents_dir


class TestPerformanceSingleAgent:
    """Performance tests for single agent with all builders."""

    def test_kilo_builder_performance(
        self, builders_and_agents_1: tuple[dict[str, AbstractBuilder], Agent, Path]
    ) -> None:
        """Test KiloBuilder performance on single agent."""
        builders, test_agent, _ = builders_and_agents_1
        builder = builders["kilo"]
        options = BuildOptions()

        start = time.perf_counter()
        result = builder.build(test_agent, options)
        elapsed = time.perf_counter() - start

        assert result
        assert elapsed < TARGET_SINGLE_TOOL, (
            f"KiloBuilder took {elapsed:.3f}s, target <{TARGET_SINGLE_TOOL}s"
        )

    def test_claude_builder_performance(
        self, builders_and_agents_1: tuple[dict[str, AbstractBuilder], Agent, Path]
    ) -> None:
        """Test ClaudeBuilder performance on single agent."""
        builders, test_agent, _ = builders_and_agents_1
        builder = builders["claude"]
        options = BuildOptions()

        start = time.perf_counter()
        result = builder.build(test_agent, options)
        elapsed = time.perf_counter() - start

        assert result
        assert elapsed < TARGET_SINGLE_TOOL, (
            f"ClaudeBuilder took {elapsed:.3f}s, target <{TARGET_SINGLE_TOOL}s"
        )

    def test_cline_builder_performance(
        self, builders_and_agents_1: tuple[dict[str, AbstractBuilder], Agent, Path]
    ) -> None:
        """Test ClineBuilder performance on single agent."""
        builders, test_agent, _ = builders_and_agents_1
        builder = builders["cline"]
        options = BuildOptions()

        start = time.perf_counter()
        result = builder.build(test_agent, options)
        elapsed = time.perf_counter() - start

        assert result
        assert elapsed < TARGET_SINGLE_TOOL, (
            f"ClineBuilder took {elapsed:.3f}s, target <{TARGET_SINGLE_TOOL}s"
        )

    def test_cursor_builder_performance(
        self, builders_and_agents_1: tuple[dict[str, AbstractBuilder], Agent, Path]
    ) -> None:
        """Test CursorBuilder performance on single agent."""
        builders, test_agent, _ = builders_and_agents_1
        builder = builders["cursor"]
        options = BuildOptions()

        start = time.perf_counter()
        result = builder.build(test_agent, options)
        elapsed = time.perf_counter() - start

        assert result
        assert elapsed < TARGET_SINGLE_TOOL, (
            f"CursorBuilder took {elapsed:.3f}s, target <{TARGET_SINGLE_TOOL}s"
        )

    def test_copilot_builder_performance(
        self, builders_and_agents_1: tuple[dict[str, AbstractBuilder], Agent, Path]
    ) -> None:
        """Test CopilotBuilder performance on single agent."""
        builders, test_agent, _ = builders_and_agents_1
        builder = builders["copilot"]
        options = BuildOptions()

        start = time.perf_counter()
        result = builder.build(test_agent, options)
        elapsed = time.perf_counter() - start

        assert result
        assert elapsed < TARGET_SINGLE_TOOL, (
            f"CopilotBuilder took {elapsed:.3f}s, target <{TARGET_SINGLE_TOOL}s"
        )

    def test_all_builders_single_agent(
        self, builders_and_agents_1: tuple[dict[str, AbstractBuilder], Agent, Path]
    ) -> None:
        """Test building all 5 tools for single agent.

        Acceptance Criteria:
        - All 5 builders complete successfully
        - Total time <10 seconds
        - All outputs are non-empty
        """
        builders, test_agent, _ = builders_and_agents_1
        options = BuildOptions()
        results = {}

        start = time.perf_counter()
        for tool_name, builder in builders.items():
            result = builder.build(test_agent, options)
            results[tool_name] = result
        total_time = time.perf_counter() - start

        # Verify all builders produced output
        for tool_name, result in results.items():
            assert result, f"{tool_name} produced empty output"

        # Verify total time is acceptable
        assert total_time < TARGET_ALL_TOOLS_SINGLE_AGENT, (
            f"All tools took {total_time:.3f}s, target <{TARGET_ALL_TOOLS_SINGLE_AGENT}s"
        )

    def test_memory_usage_single_agent(
        self, builders_and_agents_1: tuple[dict[str, AbstractBuilder], Agent, Path]
    ) -> None:
        """Test memory usage during single agent build."""
        builders, test_agent, _ = builders_and_agents_1
        builder = builders["kilo"]
        options = BuildOptions()

        tracemalloc.start()
        result = builder.build(test_agent, options)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak / (1024 * 1024)
        assert peak_mb < 100, f"Peak memory {peak_mb:.1f}MB exceeds target 100MB"
        assert result


class TestPerformanceMultipleAgents:
    """Performance tests for multiple agents."""

    def test_5_agents_all_tools(
        self, builders_and_agents_5: tuple[dict[str, AbstractBuilder], list[Agent], Path]
    ) -> None:
        """Test building all 5 tools for 5 agents."""
        builders, agents, _ = builders_and_agents_5
        options = BuildOptions()

        start = time.perf_counter()
        results = {}
        for agent in agents:
            agent_results = {}
            for tool_name, builder in builders.items():
                result = builder.build(agent, options)
                agent_results[tool_name] = result
                assert result, f"{tool_name} produced empty output for {agent.name}"
            results[agent.name] = agent_results
        total_time = time.perf_counter() - start

        # Verify all agents built all tools
        assert len(results) == 5, f"Expected 5 agent results, got {len(results)}"
        for agent_name, agent_results in results.items():
            assert len(agent_results) == 5, (
                f"Expected 5 tools for {agent_name}, got {len(agent_results)}"
            )

        assert total_time < 15.0, f"5 agents all tools took {total_time:.3f}s, expected <15s"

    def test_10_agents_all_tools(
        self, builders_and_agents_10: tuple[dict[str, AbstractBuilder], list[Agent], Path]
    ) -> None:
        """Test building all 5 tools for 10 agents."""
        builders, agents, _ = builders_and_agents_10
        options = BuildOptions()

        start = time.perf_counter()
        results = {}
        for agent in agents:
            agent_results = {}
            for tool_name, builder in builders.items():
                result = builder.build(agent, options)
                agent_results[tool_name] = result
                assert result, f"{tool_name} produced empty output for {agent.name}"
            results[agent.name] = agent_results
        total_time = time.perf_counter() - start

        # Verify all agents built all tools
        assert len(results) == 10, f"Expected 10 agent results, got {len(results)}"
        for agent_name, agent_results in results.items():
            assert len(agent_results) == 5, (
                f"Expected 5 tools for {agent_name}, got {len(agent_results)}"
            )

        assert total_time < TARGET_ALL_TOOLS_10_AGENTS, (
            f"10 agents all tools took {total_time:.3f}s, target <{TARGET_ALL_TOOLS_10_AGENTS}s"
        )

    def test_memory_usage_10_agents(
        self, builders_and_agents_10: tuple[dict[str, AbstractBuilder], list[Agent], Path]
    ) -> None:
        """Test memory usage for 10 agents, all tools."""
        builders, agents, _ = builders_and_agents_10
        options = BuildOptions()

        tracemalloc.start()
        for agent in agents:
            for builder in builders.values():
                builder.build(agent, options)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak / (1024 * 1024)
        assert peak_mb < 200, f"Peak memory {peak_mb:.1f}MB exceeds target 200MB for 10 agents"


class TestPerformanceBuilderComparison:
    """Compare performance across all 5 builders."""

    def test_builder_performance_comparison(
        self, builders_and_agents_1: tuple[dict[str, AbstractBuilder], Agent, Path]
    ) -> None:
        """Compare build time across all 5 builders."""
        builders, agent, _ = builders_and_agents_1
        options = BuildOptions()

        times = {}
        for tool_name, builder in builders.items():
            start = time.perf_counter()
            result = builder.build(agent, options)
            elapsed = time.perf_counter() - start
            times[tool_name] = elapsed
            assert result, f"{tool_name} produced empty output"

        # All should be fast
        for tool_name, elapsed in times.items():
            assert elapsed < TARGET_SINGLE_TOOL, (
                f"{tool_name} took {elapsed:.3f}s, target <{TARGET_SINGLE_TOOL}s"
            )

        # Find fastest and slowest
        fastest = min(times.items(), key=lambda x: x[1])
        slowest = max(times.items(), key=lambda x: x[1])

        # Slowest should not be more than 3x fastest (different format complexity)
        ratio = slowest[1] / fastest[1]
        assert ratio < 10.0, f"{slowest[0]} is {ratio:.1f}x slower than {fastest[0]}"

    def test_builder_output_consistency(
        self, builders_and_agents_1: tuple[dict[str, AbstractBuilder], Agent, Path]
    ) -> None:
        """Test that all builders produce valid output."""
        builders, agent, _ = builders_and_agents_1
        options = BuildOptions()

        results = {}
        for tool_name, builder in builders.items():
            result = builder.build(agent, options)
            results[tool_name] = result
            assert result, f"{tool_name} produced empty output"

        # ClaudeBuilder returns dict, others return strings
        assert isinstance(results["claude"], dict), "ClaudeBuilder should return dict"
        assert isinstance(results["kilo"], str), "KiloBuilder should return string"
        assert isinstance(results["cline"], str), "ClineBuilder should return string"
        assert isinstance(results["cursor"], str), "CursorBuilder should return string"
        assert isinstance(results["copilot"], str), "CopilotBuilder should return string"

        # String outputs should be reasonably sized
        for tool_name, result in results.items():
            if isinstance(result, str):
                assert len(result) > 100, f"{tool_name} output too small"
                assert len(result) < 100_000, f"{tool_name} output too large"
            else:
                # Dict output (Claude)
                assert "system" in result, "Claude missing 'system' key"
                assert "tools" in result, "Claude missing 'tools' key"


class TestPerformanceScaling:
    """Test how performance scales with number of agents."""

    def test_scaling_5_10_agents(self) -> None:
        """Test scaling from 5 to 10 agents."""
        options = BuildOptions()

        # Test with 5 agents
        with TemporaryDirectory() as temp_dir:
            agents_dir_5 = create_test_agents_directory(temp_dir, 5)
            builders_5: dict[str, AbstractBuilder] = {
                "kilo": KiloBuilder(agents_dir=agents_dir_5),
            }
            agents_5 = [create_test_agent(f"agent_{i}", i) for i in range(5)]

            start = time.perf_counter()
            for agent in agents_5:
                builders_5["kilo"].build(agent, options)
            time_5 = time.perf_counter() - start

        # Test with 10 agents
        with TemporaryDirectory() as temp_dir:
            agents_dir_10 = create_test_agents_directory(temp_dir, 10)
            builders_10: dict[str, AbstractBuilder] = {
                "kilo": KiloBuilder(agents_dir=agents_dir_10),
            }
            agents_10 = [create_test_agent(f"agent_{i}", i) for i in range(10)]

            start = time.perf_counter()
            for agent in agents_10:
                builders_10["kilo"].build(agent, options)
            time_10 = time.perf_counter() - start

        # Verify performance is acceptable
        assert time_5 < 5.0, f"5 agents took {time_5:.2f}s, expected <5s"
        assert time_10 < 12.0, f"10 agents took {time_10:.2f}s, expected <12s"

    def test_builder_cache_effects(self) -> None:
        """Test repeated builds are not slower."""
        with TemporaryDirectory() as temp_dir:
            agents_dir = create_test_agents_directory(temp_dir, 1)
            builder = KiloBuilder(agents_dir=agents_dir)
            agent = create_test_agent("agent_0", 0)
            options = BuildOptions()

            # First build
            start = time.perf_counter()
            builder.build(agent, options)
            time_1 = time.perf_counter() - start

            # Second build (same agent, same builder)
            start = time.perf_counter()
            builder.build(agent, options)
            time_2 = time.perf_counter() - start

            # Second should not be significantly slower
            assert time_2 <= time_1 * 1.5, (
                f"Second build {time_2:.3f}s is 1.5x slower than first {time_1:.3f}s"
            )
