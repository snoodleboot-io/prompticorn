# ClaudeBuilder Comprehensive Guide

A detailed guide for building Claude Markdown agent configuration files from Agent IR models.

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

**ClaudeBuilder** is the builder for [Claude](https://claude.ai) agent configurations. It transforms Agent IR models into Markdown files written to the `.claude/` directory, following the Claude agent file format.

### What ClaudeBuilder Does

- **Input:** Agent IR models (Python dataclasses with agent definitions)
- **Output:** Markdown files written to `.claude/` directory
- **Target:** `.claude/agents/`, `.claude/subagents/`, `.claude/workflows/`, and `CLAUDE.md`
- **Supports:** System prompts, tools, skills, workflows, and subagents

### Output Format

ClaudeBuilder generates a `dict[str, str]` mapping file paths to Markdown content:

```python
{
    ".claude/agents/code-agent.md": "# Code Agent\n...",
    ".claude/subagents/feature.md": "# Feature\n...",
    ".claude/workflows/feature.md": "# Feature Workflow\n...",
    "CLAUDE.md": "# Claude Configuration\n..."
}
```

### Key Features

✅ Markdown files output
✅ File path → content mapping
✅ `.claude/` directory structure
✅ Agents, subagents, and workflows support
✅ Skills and workflows support
✅ Programmatic integration

---

## Quick Start

### Most Basic Example

```python
from prompticorn.builders.claude_builder import ClaudeBuilder
from prompticorn.builders.base import BuildOptions
from prompticorn.ir.models import Agent

# Create a builder
builder = ClaudeBuilder()

# Create an agent
agent = Agent(
    name="code_expert",
    description="Writes high-quality code",
    system_prompt="You are an expert code writer with deep knowledge of Python.",
    tools=["bash", "python"],
)

# Build Markdown file configuration
options = BuildOptions(variant="minimal", agent_name="code_expert")
config = builder.build(agent, options)

# config is a dict[str, str] mapping file paths to Markdown content
for file_path, content in config.items():
    print(f"File: {file_path}")
    print(content[:100])
```

### Expected Output

```python
{
    ".claude/agents/code_expert.md": "# Code Expert\n\nYou are an expert code writer...",
    "CLAUDE.md": "# Claude Configuration\n..."
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
from prompticorn.builders.claude_builder import ClaudeBuilder
from prompticorn.builders.base import BuildOptions, BuilderValidationError
from prompticorn.ir.models import Agent
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
from prompticorn.ir.models import Agent

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
from prompticorn.builders.base import BuildOptions

# For API integration
options = BuildOptions(
    variant="verbose",
    agent_name="research_assistant",
    include_tools=True,
    include_skills=True,
    include_instructions=True,
)
```

### 4. Build Markdown File Configuration

```python
try:
    config = builder.build(agent, options)
    
    # config is a dict[str, str] mapping file paths to Markdown content
    for file_path, content in config.items():
        print(f"File: {file_path}")
        print(content[:100])
    
except BuilderValidationError as e:
    print(f"Build failed: {e.message}")
    for error in e.errors:
        print(f"  - {error}")
```

---

## Advanced Usage Patterns

### Pattern 1: Building Multiple Agents

ClaudeBuilder can generate file configurations for multiple agents.

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

# config is a dict[str, str] with file paths as keys
for file_path, content in config.items():
    print(f"File: {file_path}")
    print(content[:200])
```

### Pattern 2: Skills and Workflows in Output

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

# Output is file paths → Markdown content
for file_path, content in config.items():
    print(f"File: {file_path}")
    print(content[:200])
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
| `.claude/agents/{name}.md` | string | Agent Markdown file |
| `.claude/subagents/{name}.md` | string | Subagent Markdown file |
| `CLAUDE.md` | string | Claude configuration file |

---

## Common Patterns & Best Practices

### ✅ DO: Write Output Files to Disk

```python
# GOOD - Write each Markdown file to its path
from pathlib import Path
config = builder.build(agent, options)
for file_path, content in config.items():
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
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

### Issue: "Output files not written to disk"

**Problem:**
```python
config = builder.build(agent, options)
# Files not created on disk
```

**Cause:** `build()` returns a `dict[str, str]`; you must write the files yourself.

**Solution:**
```python
from pathlib import Path
config = builder.build(agent, options)
for file_path, content in config.items():
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"✓ Written: {file_path}")
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

### Issue: Agent content not appearing in Markdown output

**Problem:**
```python
config = builder.build(agent, options)
# Content seems incomplete
```

**Why:** Check that `BuildOptions` flags are set correctly.

**Solution:**
```python
options = BuildOptions(
    variant="verbose",
    include_tools=True,
    include_skills=True,
    include_workflows=True,
)
config = builder.build(agent, options)
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
def build(self, agent: Agent, options: BuildOptions) -> dict[str, str]:
    """Build Markdown files written to `.claude/` directory from an Agent IR model.
    
    Args:
        agent: The Agent IR model to build from
        options: Build configuration options
    
    Returns:
        Dictionary mapping file paths to Markdown content
    
    Raises:
        BuilderValidationError: If the agent model is invalid
    """
```

#### Output Dictionary Structure

```python
{
    ".claude/agents/code-agent.md": "# Code Agent\n...",
    ".claude/subagents/feature.md": "# Feature\n...",
    "CLAUDE.md": "# Claude Configuration\n..."
}
```

---

## Full Working Examples

### Example 1: Simple Code Agent

```python
from prompticorn.builders.claude_builder import ClaudeBuilder
from prompticorn.builders.base import BuildOptions
from prompticorn.ir.models import Agent
from pathlib import Path

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
    
    # Write each file to disk
    for file_path, content in config.items():
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    
    return config

if __name__ == "__main__":
    config = build_code_agent()
    for file_path in config:
        print(f"Written: {file_path}")
```

### Example 2: Multi-Tool System

```python
from prompticorn.builders.claude_builder import ClaudeBuilder
from prompticorn.builders.base import BuildOptions
from prompticorn.ir.models import Agent
from pathlib import Path

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
    
    # Write each Markdown file to disk
    for file_path, content in config.items():
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    
    return config

if __name__ == "__main__":
    config = build_devops_agent()
    print("✓ DevOps agent built and saved")
```

### Example 3: Writing Files to Disk

```python
from prompticorn.builders.claude_builder import ClaudeBuilder
from prompticorn.builders.base import BuildOptions
from prompticorn.ir.models import Agent
from pathlib import Path

def write_claude_agent_files():
    """Use ClaudeBuilder to generate Markdown files."""
    
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
    
    # Write each Markdown file
    for file_path, content in config.items():
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        print(f"Written: {file_path}")

if __name__ == "__main__":
    write_claude_agent_files()
```

### Example 4: Configuration Management

```python
from prompticorn.builders.claude_builder import ClaudeBuilder
from prompticorn.builders.base import BuildOptions
from prompticorn.ir.models import Agent
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
    all_configs = {}
    
    for agent in agents:
        try:
            config = builder.build(agent, options)
            all_configs[agent.name] = config
            # Write each Markdown file to disk
            for file_path, content in config.items():
                path = Path(file_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            print(f"✓ Built {agent.name}")
        except Exception as e:
            print(f"✗ Failed {agent.name}: {e}")
    
    print(f"\n✓ Built {len(all_configs)} agent configurations")
    
    return all_configs

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

- **Source Code:** `prompticorn/builders/claude_builder.py`
- **Base Class:** `prompticorn/builders/base.py` (Builder)
- **IR Models:** `prompticorn/ir/models.py` (Agent dataclass)
- **Examples:** `prompticorn/builders/examples_usage.py`
- **Claude API Docs:** [api.anthropic.com](https://api.anthropic.com)
- **Messages API:** [docs.anthropic.com/messages](https://docs.anthropic.com/messages/overview)

