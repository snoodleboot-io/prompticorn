# ClaudeBuilder Comprehensive Guide

A detailed guide for building Claude Messages API JSON configurations from Agent IR models.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Installation & Setup](#installation--setup)
4. [Basic Usage](#basic-usage)
5. [Advanced Usage Patterns](#advanced-usage-patterns)
6. [Configuration Options](#configuration-options)
7. [Common Patterns & Best Practices](#common-patterns--best-practices)
8. [Troubleshooting](#troubleshooting)
9. [API Reference](#api-reference)
10. [Full Working Examples](#full-working-examples)

---

## Overview

**ClaudeBuilder** is the builder for the [Claude Messages API](https://docs.anthropic.com/messages/overview). It transforms Agent IR models into JSON dictionaries that can be directly used with Claude's API for programmatic agent definitions.

### What ClaudeBuilder Does

- **Input:** Agent IR models (Python dataclasses with agent definitions)
- **Output:** JSON-serializable Python dictionaries
- **Target:** Claude API system prompts and tool definitions
- **Supports:** System prompts, tool schemas, instructions, workflows, and subagents

### Output Format

ClaudeBuilder generates JSON-compatible dictionaries:

```python
{
    "system": "You are an expert software engineer...",
    "tools": [
        {
            "name": "bash",
            "description": "Tool: bash",
            "input_schema": {
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "Parameter"}
                },
                "required": ["param"]
            }
        }
    ],
    "instructions": "Follow these principles:\n- Read code before writing\n- Match existing patterns\n..."
}
```

### Key Features

✅ JSON-serializable output
✅ Claude Messages API compatible
✅ Tool schema generation
✅ Instructions as prose
✅ Skills and workflows support
✅ Programmatic integration

---

## Quick Start

### Most Basic Example

```python
from src.builders.claude_builder import ClaudeBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent
import json

# Create a builder
builder = ClaudeBuilder()

# Create an agent
agent = Agent(
    name="code_expert",
    description="Writes high-quality code",
    system_prompt="You are an expert code writer with deep knowledge of Python.",
    tools=["bash", "python"],
)

# Build JSON configuration
options = BuildOptions(variant="minimal", agent_name="code_expert")
config = builder.build(agent, options)

# config is a dict, JSON-serializable
json_str = json.dumps(config, indent=2)
print(json_str)
```

### Expected Output

```json
{
  "system": "You are an expert code writer with deep knowledge of Python.",
  "tools": [
    {
      "name": "bash",
      "description": "Tool: bash",
      "input_schema": {
        "type": "object",
        "properties": {
          "param": {"type": "string", "description": "Parameter for the tool"}
        },
        "required": ["param"]
      }
    },
    {
      "name": "python",
      "description": "Tool: python",
      "input_schema": {
        "type": "object",
        "properties": {
          "param": {"type": "string", "description": "Parameter for the tool"}
        },
        "required": ["param"]
      }
    }
  ],
  "instructions": ""
}
```

---

## Installation & Setup

### Prerequisites

- Python 3.11+
- Agent IR models defined
- Anthropic Claude API (optional, for using the output)

### Import

```python
from src.builders.claude_builder import ClaudeBuilder
from src.builders.base import BuildOptions, BuilderValidationError
from src.ir.models import Agent
import json
```

### Initialize

```python
# Option 1: Default initialization
builder = ClaudeBuilder()

# Option 2: With custom agents directory
builder = ClaudeBuilder(agents_dir="agents")

# Option 3: Using Path object
from pathlib import Path
builder = ClaudeBuilder(agents_dir=Path("config/agents"))
```

### Verify Installation

```python
# Check tool information
print(builder.get_tool_name())          # Returns: "claude"
print(builder.get_output_format())      # Returns: "Claude Messages API JSON (dict)"

# Verify feature support
print(builder.supports_feature("skills"))      # True
print(builder.supports_feature("workflows"))   # True
print(builder.supports_feature("tools"))       # True
```

---

## Basic Usage

### 1. Create Agent Model

```python
from src.ir.models import Agent

agent = Agent(
    name="research_assistant",
    description="Conducts research and synthesizes information",
    system_prompt="""You are a research assistant specializing in information synthesis.

Your expertise:
- Finding reliable information sources
- Synthesizing complex information
- Identifying gaps in knowledge
- Providing well-sourced conclusions""",
    tools=["search", "browser", "database"],
    skills=["information_synthesis", "source_verification"],
)
```

### 2. Validate Agent

```python
# Validate before building
errors = builder.validate(agent)

if errors:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
    exit(1)
```

### 3. Configure Build Options

```python
from src.builders.base import BuildOptions

# For API integration
options = BuildOptions(
    variant="verbose",
    agent_name="research_assistant",
    include_tools=True,
    include_skills=True,
    include_instructions=True,
)
```

### 4. Build JSON Configuration

```python
import json

try:
    config = builder.build(agent, options)
    
    # Verify it's JSON-serializable
    json_str = json.dumps(config, indent=2)
    print(json_str)
    
except BuilderValidationError as e:
    print(f"Build failed: {e.message}")
    for error in e.errors:
        print(f"  - {error}")
```

### 5. Use with Claude API

```python
from anthropic import Anthropic

# Build configuration
config = builder.build(agent, options)

# Use with Claude API
client = Anthropic()

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    system=config["system"],
    tools=config["tools"],
    messages=[
        {
            "role": "user",
            "content": "Your query here"
        }
    ]
)

print(response.content)
```

---

## Advanced Usage Patterns

### Pattern 1: Building Tool Schemas

ClaudeBuilder generates tool schemas automatically for the Claude API.

```python
# Agent with multiple tools
agent = Agent(
    name="automation_expert",
    description="Automates complex workflows",
    system_prompt="You are an automation expert.",
    tools=["bash", "python", "node", "docker"],
)

options = BuildOptions(
    variant="verbose",
    include_tools=True,
)

config = builder.build(agent, options)

# tools list has full JSON schemas
for tool in config["tools"]:
    print(f"Tool: {tool['name']}")
    print(f"  Schema: {tool['input_schema']}")
```

### Pattern 2: Instructions from Skills and Workflows

```python
# Agent with skills and workflows
agent = Agent(
    name="deployment_expert",
    description="Manages deployments",
    system_prompt="You are a deployment expert.",
    tools=["docker", "kubernetes"],
    skills=["deployment", "scaling", "monitoring"],
)

options = BuildOptions(
    variant="verbose",
    include_tools=True,
    include_skills=True,
    include_workflows=True,
)

config = builder.build(agent, options)

# Instructions will contain skills and workflow info
print("System prompt:")
print(config["system"])
print("\nTools:")
for tool in config["tools"]:
    print(f"  - {tool['name']}")
print("\nInstructions:")
print(config["instructions"])
```

### Pattern 3: Building from Configuration Files

```python
from pathlib import Path
import json

def build_from_json_config(config_path: str) -> dict:
    """Build Claude config from JSON agent definition."""
    
    # Load configuration
    with open(config_path) as f:
        config = json.load(f)
    
    # Create agent
    agent = Agent(
        name=config["name"],
        description=config["description"],
        system_prompt=config["system_prompt"],
        tools=config.get("tools", []),
        skills=config.get("skills", []),
    )
    
    # Build
    options = BuildOptions(
        variant=config.get("variant", "verbose"),
        agent_name=agent.name,
        include_tools=config.get("include_tools", True),
        include_skills=config.get("include_skills", True),
    )
    
    return builder.build(agent, options)

# Example usage
config = build_from_json_config("agents/code_expert.json")
```

### Pattern 4: Multiple Agents in Batch

```python
import json
from pathlib import Path

def build_all_agents(agents: list[Agent]) -> dict[str, dict]:
    """Build configurations for multiple agents."""
    
    configs = {}
    options = BuildOptions(variant="verbose")
    
    for agent in agents:
        try:
            config = builder.build(agent, options)
            configs[agent.name] = config
            print(f"✓ Built {agent.name}")
        except BuilderValidationError as e:
            print(f"✗ Failed {agent.name}: {e.message}")
    
    return configs

# Example
agents = [
    Agent(name="code", description="Code", system_prompt="Code expert"),
    Agent(name="test", description="Test", system_prompt="Test expert"),
]

configs = build_all_agents(agents)

# Save as JSON
with open("agents.json", "w") as f:
    json.dump(configs, f, indent=2)
```

### Pattern 5: Runtime Agent Configuration

```python
from typing import Any

def create_claude_agent_runtime(
    role: str,
    capabilities: list[str],
    tools: list[str],
) -> dict[str, Any]:
    """Create Claude agent configuration at runtime."""
    
    # Build prompt from parameters
    system_prompt = f"""You are a {role} agent.

Capabilities:
{chr(10).join(f'- {cap}' for cap in capabilities)}

Available tools:
{chr(10).join(f'- {tool}' for tool in tools)}"""
    
    # Create agent
    agent = Agent(
        name=role,
        description=f"{role.capitalize()} agent",
        system_prompt=system_prompt,
        tools=tools,
    )
    
    # Build configuration
    options = BuildOptions(variant="verbose", include_tools=True)
    return builder.build(agent, options)

# Runtime usage
config = create_claude_agent_runtime(
    role="data_scientist",
    capabilities=["data_analysis", "visualization", "statistics"],
    tools=["python", "bash", "sql"],
)

print(json.dumps(config, indent=2))
```

---

## Configuration Options

### BuildOptions for Claude

```python
@dataclass
class BuildOptions:
    variant: str = "minimal"          # minimal or verbose
    agent_name: str = ""              # Agent name
    include_subagents: bool = True    # Include subagents info
    include_skills: bool = True       # Include skills in instructions
    include_workflows: bool = True    # Include workflows in instructions
    include_rules: bool = True        # Include rules in instructions
    include_tools: bool = True        # Include tools with schemas
```

### Variant Impact

**minimal:**
- Compact JSON output
- Basic tool schemas
- No extra instructions

**verbose:**
- Full instructions section
- Detailed tool descriptions
- Complete skill/workflow info

### Output Structure

| Key | Type | Description |
|-----|------|-------------|
| `system` | string | System prompt for Claude |
| `tools` | list[dict] | Tool definitions with schemas |
| `instructions` | string | Additional instructions from skills/workflows |

---

## Common Patterns & Best Practices

### ✅ DO: Always Serialize to JSON

```python
# GOOD - Verify JSON compatibility
config = builder.build(agent, options)
json_str = json.dumps(config)  # Verify it works
```

```python
# BAD - Don't assume it's JSON-compatible
config = builder.build(agent, options)
# Don't use without verifying serialization
```

### ✅ DO: Validate Before Using with API

```python
# GOOD
errors = builder.validate(agent)
if not errors:
    config = builder.build(agent, options)
    # Use with Claude API
```

### ✅ DO: Include Meaningful Tool Lists

```python
# GOOD - Tools relevant to role
analyst_agent = Agent(
    name="analyst",
    tools=["python", "sql", "bash"],  # Data analysis tools
)

writer_agent = Agent(
    name="writer",
    tools=["markdown", "bash"],  # Documentation tools
)
```

### ✅ DO: Document Skills in System Prompt

```python
# GOOD - Explain available skills
agent = Agent(
    name="expert",
    system_prompt="""You have access to these skills:
    
- skill_a: For tasks of type A
- skill_b: For tasks of type B

Use them when appropriate.""",
    skills=["skill_a", "skill_b"],
)
```

### ✅ DO: Keep Instructions Concise

```python
# GOOD - Clear, actionable instructions
options = BuildOptions(
    variant="verbose",
    include_skills=True,
    include_workflows=True,
)

config = builder.build(agent, options)
# instructions are focused and useful
```

---

## Troubleshooting

### Issue: "Output is not JSON serializable"

**Problem:**
```python
config = builder.build(agent, options)
json.dumps(config)  # Raises TypeError
```

**Cause:** Non-JSON-serializable objects in config (dates, custom objects, etc.)

**Solution:**
```python
# Ensure all values are JSON-compatible types:
# strings, numbers, booleans, lists, dicts, null
try:
    config = builder.build(agent, options)
    json_str = json.dumps(config)
    print("✓ JSON serialization successful")
except TypeError as e:
    print(f"✗ Serialization error: {e}")
```

### Issue: "Agent name is required"

**Problem:**
```python
agent = Agent(name="", ...)  # Empty name
```

**Solution:**
```python
agent = Agent(name="meaningful_name", ...)
```

### Issue: Tool schemas are placeholder text

**Problem:**
```python
# The tool schemas contain:
# "input_schema": {
#     "properties": {
#         "param": {"type": "string"}
#     }
# }
```

**Why:** ClaudeBuilder generates basic schemas. For production, customize them.

**Solution:**
```python
config = builder.build(agent, options)

# Customize tool schemas if needed
for tool in config["tools"]:
    if tool["name"] == "bash":
        tool["input_schema"]["properties"] = {
            "command": {"type": "string", "description": "Shell command"},
            "timeout": {"type": "number", "description": "Timeout in seconds"},
        }
        tool["input_schema"]["required"] = ["command"]
```

---

## API Reference

### ClaudeBuilder Class

#### Constructor

```python
def __init__(self, agents_dir: Path | str = "agents") -> None:
    """Initialize ClaudeBuilder.
    
    Args:
        agents_dir: Base directory for agent configurations
    """
```

#### Core Methods

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `build` | `build(agent: Agent, options: BuildOptions) -> dict[str, Any]` | Dict | Builds JSON config |
| `validate` | `validate(agent: Agent) -> list[str]` | List | Returns validation errors |
| `get_output_format` | `get_output_format() -> str` | String | Returns format description |
| `get_tool_name` | `get_tool_name() -> str` | String | Returns "claude" |
| `supports_feature` | `supports_feature(feature: str) -> bool` | Bool | Checks feature support |

#### Main Build Method

```python
def build(self, agent: Agent, options: BuildOptions) -> dict[str, Any]:
    """Build Claude Messages API JSON output from an Agent IR model.
    
    Args:
        agent: The Agent IR model to build from
        options: Build configuration options
    
    Returns:
        Dictionary with system, tools, and instructions keys
        All values are JSON-serializable
    
    Raises:
        BuilderValidationError: If the agent model is invalid
    """
```

#### Output Dictionary Structure

```python
{
    "system": str,              # System prompt
    "tools": list[dict],        # Tool definitions with schemas
    "instructions": str,        # Additional instructions
}

# Each tool in tools list:
{
    "name": str,                # Tool name
    "description": str,         # Tool description
    "input_schema": {           # JSON schema for inputs
        "type": "object",
        "properties": dict,     # Parameter definitions
        "required": list,       # Required parameters
    }
}
```

---

## Full Working Examples

### Example 1: Simple Code Agent

```python
from src.builders.claude_builder import ClaudeBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent
import json

def build_code_agent():
    """Build a simple code generation agent."""
    
    builder = ClaudeBuilder()
    
    agent = Agent(
        name="code_generator",
        description="Generates clean, well-documented code",
        system_prompt="""You are an expert software engineer.

Your role is to:
1. Generate clean, readable code
2. Follow best practices
3. Include documentation
4. Handle edge cases
5. Write testable code""",
        tools=["bash", "python"],
    )
    
    options = BuildOptions(
        variant="minimal",
        agent_name="code_generator",
        include_tools=True,
    )
    
    config = builder.build(agent, options)
    
    return json.dumps(config, indent=2)

if __name__ == "__main__":
    json_output = build_code_agent()
    print(json_output)
```

### Example 2: Multi-Tool System

```python
from src.builders.claude_builder import ClaudeBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent
import json

def build_devops_agent():
    """Build a DevOps automation agent."""
    
    builder = ClaudeBuilder()
    
    agent = Agent(
        name="devops_expert",
        description="Manages infrastructure and deployments",
        system_prompt="""You are a DevOps expert.

Responsibilities:
- Infrastructure management
- Deployment automation
- Monitoring and alerting
- Security and compliance
- Cost optimization""",
        tools=["bash", "docker", "kubernetes", "terraform"],
        skills=["infrastructure_as_code", "deployment", "monitoring"],
    )
    
    options = BuildOptions(
        variant="verbose",
        include_tools=True,
        include_skills=True,
    )
    
    config = builder.build(agent, options)
    
    # Save configuration
    with open("devops-agent.json", "w") as f:
        json.dump(config, f, indent=2)
    
    return config

if __name__ == "__main__":
    config = build_devops_agent()
    print("✓ DevOps agent built and saved")
```

### Example 3: API Integration

```python
from src.builders.claude_builder import ClaudeBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent
from anthropic import Anthropic
import json

def use_claude_builder_with_api():
    """Use ClaudeBuilder to configure Claude API."""
    
    builder = ClaudeBuilder()
    
    agent = Agent(
        name="research_assistant",
        description="Conducts research and analysis",
        system_prompt="""You are a research assistant.

Help users by:
- Finding relevant information
- Analyzing data
- Synthesizing findings
- Providing citations""",
        tools=["search", "analysis"],
    )
    
    options = BuildOptions(
        variant="verbose",
        include_tools=True,
    )
    
    # Build configuration
    config = builder.build(agent, options)
    
    # Use with Claude API
    client = Anthropic()
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system=config["system"],
        tools=config["tools"],
        messages=[
            {
                "role": "user",
                "content": "What are the key trends in AI in 2024?"
            }
        ]
    )
    
    print("Claude Response:")
    for block in response.content:
        if hasattr(block, "text"):
            print(block.text)

if __name__ == "__main__":
    use_claude_builder_with_api()
```

### Example 4: Configuration Management

```python
from src.builders.claude_builder import ClaudeBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent
import json
from pathlib import Path

def manage_agent_configurations():
    """Manage multiple agent configurations."""
    
    builder = ClaudeBuilder()
    
    agents = [
        Agent(
            name="summarizer",
            description="Summarizes long texts",
            system_prompt="You are an expert summarizer.",
            tools=["text_analysis"],
        ),
        Agent(
            name="translator",
            description="Translates between languages",
            system_prompt="You are a professional translator.",
            tools=["translation"],
        ),
        Agent(
            name="analyst",
            description="Analyzes data and insights",
            system_prompt="You are a data analyst.",
            tools=["data_analysis", "visualization"],
        ),
    ]
    
    options = BuildOptions(variant="verbose", include_tools=True)
    configs = {}
    
    for agent in agents:
        try:
            config = builder.build(agent, options)
            configs[agent.name] = config
            print(f"✓ Built {agent.name}")
        except Exception as e:
            print(f"✗ Failed {agent.name}: {e}")
    
    # Save all configurations
    output_path = Path("agent_configs.json")
    output_path.write_text(json.dumps(configs, indent=2))
    
    print(f"\n✓ Saved {len(configs)} configurations to {output_path}")
    
    return configs

if __name__ == "__main__":
    configs = manage_agent_configurations()
```

---

## Related Builders

For building other tools, see:
- [KiloBuilder Guide](./KILO_BUILDER_GUIDE.md) - For Kilo IDE
- [ClineBuilder Guide](./CLINE_BUILDER_GUIDE.md) - For Cline AI
- [CopilotBuilder Guide](./COPILOT_BUILDER_GUIDE.md) - For GitHub Copilot
- [CursorBuilder Guide](./CURSOR_BUILDER_GUIDE.md) - For Cursor IDE

---

## Support & Resources

- **Source Code:** `src/builders/claude_builder.py`
- **Base Class:** `src/builders/base.py` (AbstractBuilder)
- **IR Models:** `src/ir/models.py` (Agent dataclass)
- **Examples:** `src/builders/examples_usage.py`
- **Claude API Docs:** [api.anthropic.com](https://api.anthropic.com)
- **Messages API:** [docs.anthropic.com/messages](https://docs.anthropic.com/messages/overview)

