"""Usage examples for the Registry and RegistryDiscovery classes.

This module demonstrates how to use the registry system to discover and
retrieve agents from the filesystem.
"""

# Example 1: Create a registry from filesystem discovery
# ======================================================

from src.registry import Registry, RegistryDiscovery

# Option A: Use the convenience class method
registry = Registry.from_discovery("./agents")

# Option B: Manual discovery and registration
discovery = RegistryDiscovery("./agents")
agents_dict = discovery.discover()
registry = Registry(agents_dict)


# Example 2: List available agents
# =================================

# Get only top-level agents
top_agents = registry.list_agents()
print(f"Top-level agents: {top_agents}")
# Output: ['architect', 'ask', 'code', 'compliance', ...]

# Get all agents including subagents
all_agents = registry.list_agents(include_subagents=True)
print(f"All agents (including subagents): {len(all_agents)}")

# Get subagents for a specific agent
code_subagents = registry.list_subagents("code")
print(f"Code subagents: {code_subagents}")
# Output: ['boilerplate', 'feature', 'house-style', ...]


# Example 3: Retrieve agents by name
# ===================================

# Get a top-level agent
code_agent = registry.get_agent("code")
print(f"Code agent: {code_agent.name}")
print(f"Description: {code_agent.description}")
print(f"System prompt: {code_agent.system_prompt[:100]}...")

# Get a subagent
boilerplate_subagent = registry.get_agent("code/boilerplate")
print(f"Boilerplate subagent: {boilerplate_subagent.name}")

# Get agent with explicit variant (minimal by default)
agent = registry.get_agent("code", variant="minimal")

# Get all agent data
all_agents_dict = registry.get_all_agents()
print(f"Total agents (all): {len(all_agents_dict)}")


# Example 4: Check if agents exist
# =================================

# Check if agent exists
if registry.has_agent("code"):
    agent = registry.get_agent("code")

# Check if subagent exists
if registry.has_subagent("code", "boilerplate"):
    subagent = registry.get_agent("code/boilerplate")


# Example 5: Validate directory structure
# ========================================

discovery = RegistryDiscovery("./agents")
issues = discovery.validate_structure()

if issues:
    print("Directory structure issues:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("Directory structure is valid!")


# Example 6: Access agent properties
# ===================================

agent = registry.get_agent("code")

# All Agent properties
print(f"Name: {agent.name}")
print(f"Description: {agent.description}")
print(f"System prompt: {agent.system_prompt}")
print(f"Tools: {agent.tools}")  # List of tool names
print(f"Skills: {agent.skills}")  # List of skill names
print(f"Workflows: {agent.workflows}")  # List of workflow names
print(f"Subagents: {agent.subagents}")  # List of subagent names


# Example 7: Error handling
# ==========================

from src.registry import AgentNotFoundError, InvalidVariantError, RegistryLoadError

# Handle missing agent
try:
    nonexistent = registry.get_agent("nonexistent_agent")
except AgentNotFoundError as e:
    print(f"Error: {e}")  # Error: Agent not found: nonexistent_agent

# Handle missing subagent
try:
    missing_sub = registry.get_agent("code/nonexistent_subagent")
except AgentNotFoundError as e:
    print(f"Error: {e}")

# Handle registry loading errors
try:
    bad_registry = Registry.from_discovery("/nonexistent/path")
except RegistryLoadError as e:
    print(f"Error: {e}")


# Example 8: Iterate over agents
# ===============================

# Iterate over top-level agents
for agent_name in registry.list_agents():
    agent = registry.get_agent(agent_name)
    print(f"Agent: {agent_name}")
    print(f"  Description: {agent.description}")

    # Iterate over subagents
    for subagent_name in registry.list_subagents(agent_name):
        subagent = registry.get_agent(f"{agent_name}/{subagent_name}")
        print(f"  Subagent: {subagent_name}")
        print(f"    Description: {subagent.description}")


# Example 9: Agent discovery process
# ===================================

# Discover agents and see what was found
discovery = RegistryDiscovery("./agents")

# Discover top-level agents
top_agents = discovery.discover_agents()
print(f"Discovered {len(top_agents)} top-level agents")

# Discover all agents (top-level + subagents)
all_discovered = discovery.discover()
print(f"Discovered {len(all_discovered)} total agents (including subagents)")

# Discover subagents for a specific agent
code_subagents = discovery.discover_subagents("code")
print(f"Discovered {len(code_subagents)} subagents for 'code' agent")
