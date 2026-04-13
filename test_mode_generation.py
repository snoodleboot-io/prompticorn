#!/usr/bin/env python3
"""Test script to generate agent files and verify mode field."""

from promptosaurus.agent_registry.registry import Registry
from promptosaurus.builders.base import BuildOptions
from promptosaurus.builders.kilo_builder import KiloBuilder


def main():
    # Initialize registry and builder
    registry = Registry.from_discovery("promptosaurus/agents")
    builder = KiloBuilder()
    options = BuildOptions(
        include_skills=True, include_workflows=True, include_tools=True, include_subagents=True
    )

    # Try to get enforcement agent
    print("Looking for enforcement agent...")
    enforcement = registry.get_agent("enforcement")

    if enforcement:
        print("\n=== Enforcement Agent ===")
        print(f"Name: {enforcement.name}")
        print(f"Description: {enforcement.description}")
        print(f"Mode: {enforcement.mode}")
        print(f"Has system_prompt: {bool(enforcement.system_prompt)}")

        # Try to build it
        print("\nBuilding enforcement agent...")
        try:
            output = builder.build(enforcement, options)
            print("Build successful!")

            # Extract frontmatter
            parts = output.split("---")
            if len(parts) >= 2:
                print("\nGenerated frontmatter:")
                print(parts[1])
        except Exception as e:
            print(f"Build failed: {e}")
            import traceback

            traceback.print_exc()
    else:
        print("\nEnforcement agent NOT FOUND in registry!")
        print("\nAvailable agents:")
        agent_names = registry.get_all_agents()
        for name in sorted(agent_names):
            agent = registry.get_agent(name)
            if agent:
                print(f"  - {name} (mode: {agent.mode})")


if __name__ == "__main__":
    main()
