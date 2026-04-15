# KiloBuilder Comprehensive Guide

A detailed guide for building Kilo IDE agent configurations from Agent IR models.

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

**KiloBuilder** is the builder for [Kilo IDE](https://kilo.ai), a command-line IDE designed for AI-assisted software development. It transforms Agent IR (Intermediate Representation) models into Kilo agent configuration files with YAML frontmatter and markdown sections.

### What KiloBuilder Does

- **Input:** Agent IR models (Python dataclasses with agent definition)
- **Output:** YAML frontmatter + Markdown files (`.md` format)
- **Target:** `.kilo/agents/{agent_name}.md` files for Kilo IDE
- **Supports:** System prompts, tools, skills, workflows, subagents, and optional variants

### Output Format

KiloBuilder generates files with this structure:

```yaml
---
name: "agent_name"
description: "Agent description"
model: "anthropic/claude-opus-4-1"
state_management: ".promptosaurus/sessions/"
---

# System Prompt

[System prompt content]

# Tools

- tool1
- tool2

# Skills

[Skills content]

# Workflows

[Workflows content]

# Subagents

- subagent1
- subagent2
```

### Key Features

✅ YAML frontmatter for metadata
✅ Markdown sections for content
✅ Variant support (minimal/verbose)
✅ Subagent composition
✅ Component selection and bundling
✅ Validation before building

---

## Quick Start

### Most Basic Example

```python
from pathlib import Path
from promptosaurus.builders.kilo_builder import KiloBuilder
from promptosaurus.builders.base import BuildOptions
from promptosaurus.ir.models import Agent

# Create a builder
builder = KiloBuilder(agents_dir=".kilo/agents")

# Create an agent
agent = Agent(
    name="code",
    description="Generates and refactors code",
    system_prompt="You are an expert software engineer skilled in all programming languages.",
    tools=["bash", "python"],
)

# Build the agent
options = BuildOptions(variant="minimal", agent_name="code")
output = builder.build(agent, options)

# output is a string with YAML frontmatter + Markdown
print(output)
```

### Expected Output

```yaml
---
name: code
description: Generates and refactors code
model: anthropic/claude-opus-4-1
state_management: .promptosaurus/sessions/
---

# System Prompt

You are an expert software engineer skilled in all programming languages.

# Tools

- bash
- python
```

---

## Installation & Setup

### Prerequisites

- Python 3.11+
- Agent IR models available in your codebase
- Component files (skills, workflows, rules) in appropriate directories

### Import

```python
from promptosaurus.builders.kilo_builder import KiloBuilder
from promptosaurus.builders.base import BuildOptions, BuilderValidationError
from promptosaurus.ir.models import Agent
```

### Initialize

```python
# Option 1: With default agents directory
builder = KiloBuilder()

# Option 2: With custom agents directory
builder = KiloBuilder(agents_dir="/path/to/agents")

# Option 3: With Path object
from pathlib import Path
builder = KiloBuilder(agents_dir=Path("custom/path/agents"))
```

### Check Tool Information

```python
# Get tool name
tool_name = builder.get_tool_name()  # Returns: "kilo"

# Get output format
output_format = builder.get_output_format()  
# Returns: "Kilo IDE Agent File (YAML frontmatter + Markdown)"

# Check feature support
supports_skills = builder.supports_feature("skills")  # True
supports_workflows = builder.supports_feature("workflows")  # True
supports_subagents = builder.supports_feature("subagents")  # True
```

---

## Basic Usage

### 1. Create an Agent IR Model

```python
from promptosaurus.ir.models import Agent

agent = Agent(
    name="test_runner",
    description="Runs tests and reports coverage",
    system_prompt="""You are an expert test engineer.
    
Your responsibilities:
- Write comprehensive test suites
- Analyze test coverage
- Identify untested code paths
- Generate test reports

Always follow TDD practices.""",
    tools=["bash", "python", "grep"],
    skills=["test_writing", "coverage_analysis"],
    subagents=["static_analyzer", "performance_profiler"],
)
```

### 2. Validate Before Building

```python
# Always validate first
errors = builder.validate(agent)

if errors:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("Agent is valid!")
```

### 3. Create Build Options

```python
from promptosaurus.builders.base import BuildOptions

# Minimal variant (smaller output)
options_min = BuildOptions(
    variant="minimal",
    agent_name="test_runner",
    include_subagents=False,
    include_workflows=False,
)

# Verbose variant (full output)
options_verbose = BuildOptions(
    variant="verbose",
    agent_name="test_runner",
    include_skills=True,
    include_workflows=True,
    include_subagents=True,
)
```

### 4. Build the Configuration

```python
try:
    output = builder.build(agent, options_verbose)
    print(output)
except BuilderValidationError as e:
    print(f"Build failed: {e.message}")
    for error in e.errors:
        print(f"  - {error}")
```

### 5. Save to File

```python
from pathlib import Path

# Generate output
output = builder.build(agent, options_verbose)

# Save to file
output_path = Path(".kilo/agents/test_runner.md")
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(output)

print(f"Saved to {output_path}")
```

---

## Advanced Usage Patterns

### Pattern 1: Building with Subagents

KiloBuilder can generate subagent configuration files in nested directories.

```python
# Parent agent with subagents
parent_agent = Agent(
    name="orchestrator",
    description="Orchestrates multiple specialized agents",
    system_prompt="You coordinate between specialized agents...",
    tools=["coordination_tool"],
    subagents=["coder", "tester", "reviewer"],
)

# Build parent
parent_output = builder.build(parent_agent, options)

# Build subagents
subagent_files = builder.build_subagents(parent_agent, options)

# subagent_files is a dict like:
# {
#     "coder": "---\nname: coder\n...",
#     "tester": "---\nname: tester\n...",
#     "reviewer": "---\nname: reviewer\n...",
# }

# Save subagent files
for subagent_name, content in subagent_files.items():
    path = Path(f".kilo/agents/orchestrator/{subagent_name}.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
```

### Pattern 2: Building Multiple Agents

```python
agents = [
    Agent(name="code", description="Code generation", system_prompt="..."),
    Agent(name="test", description="Test writing", system_prompt="..."),
    Agent(name="review", description="Code review", system_prompt="..."),
]

options = BuildOptions(variant="verbose")

for agent in agents:
    try:
        output = builder.build(agent, options)
        path = Path(f".kilo/agents/{agent.name}.md")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output)
        print(f"✓ Built {agent.name}")
    except BuilderValidationError as e:
        print(f"✗ Failed to build {agent.name}: {e.message}")
```

### Pattern 3: Conditional Component Inclusion

```python
# Build without subagents
options_no_subs = BuildOptions(
    variant="verbose",
    include_subagents=False,  # Skip subagents
    include_workflows=True,
    include_skills=True,
)

output = builder.build(agent, options_no_subs)

# Build with only tools and system prompt
options_minimal = BuildOptions(
    variant="minimal",
    include_tools=True,
    include_skills=False,
    include_workflows=False,
    include_subagents=False,
)

output = builder.build(agent, options_minimal)
```

### Pattern 4: Custom Variants

```python
# Create agents with different system prompts for variants
base_agent = Agent(
    name="developer",
    description="Develops features",
    system_prompt="You are a developer.",
)

minimal_agent = Agent(
    name="developer",
    description="Develops features",
    system_prompt="You are a developer.",  # Shorter for minimal
)

# Build both
minimal_output = builder.build(minimal_agent, BuildOptions(variant="minimal"))
verbose_output = builder.build(base_agent, BuildOptions(variant="verbose"))
```

### Pattern 5: Dynamic Tool and Skill Registration

```python
# Build agent with dynamic tool list
def build_agent_with_tools(agent_name: str, tools: list[str]) -> str:
    agent = Agent(
        name=agent_name,
        description=f"Agent with tools: {', '.join(tools)}",
        system_prompt=f"You have access to: {', '.join(tools)}",
        tools=tools,
    )
    
    return builder.build(agent, BuildOptions(variant="verbose"))

# Use it
output = build_agent_with_tools("debugger", ["bash", "python", "strace"])
```

---

## Configuration Options

### BuildOptions Class

```python
@dataclass
class BuildOptions:
    variant: str = "minimal"                  # minimal or verbose
    agent_name: str = ""                      # Name of the agent
    include_subagents: bool = True            # Include subagents
    include_skills: bool = True               # Include skills
    include_workflows: bool = True            # Include workflows
    include_rules: bool = True                # Include rules
    include_tools: bool = True                # Include tools
```

### Variant Behavior

**minimal:** 
- Lightweight output
- Shorter system prompts
- Fewer optional sections
- Faster to process

**verbose:**
- Full detail
- Complete system prompts
- All available sections
- Comprehensive documentation

### Option Combinations

| Option | Effect | Example |
|--------|--------|---------|
| `variant="minimal"` | Compact output | Agent without detailed descriptions |
| `variant="verbose"` | Full output | Complete agent configuration |
| `include_tools=False` | Skip tools section | Agents without tool requirements |
| `include_skills=False` | Skip skills section | Simple agents without special skills |
| `include_workflows=False` | Skip workflows | Agents without complex workflows |
| `include_subagents=False` | Skip subagents | Standalone agents |

---

## Common Patterns & Best Practices

### ✅ DO: Validate Before Building

```python
# GOOD
errors = builder.validate(agent)
if not errors:
    output = builder.build(agent, options)
```

```python
# BAD - No validation
output = builder.build(agent, options)  # May fail silently
```

### ✅ DO: Use Specific Error Handling

```python
# GOOD
try:
    output = builder.build(agent, options)
except BuilderValidationError as e:
    print(f"Validation failed: {e.message}")
    for error in e.errors:
        print(f"  - {error}")
```

```python
# BAD - Generic exception
try:
    output = builder.build(agent, options)
except Exception as e:
    print(f"Error: {e}")  # Doesn't distinguish builder errors
```

### ✅ DO: Set Correct Output Paths

```python
# GOOD - Follows Kilo convention
path = Path(".kilo/agents/agent_name.md")

# GOOD - Subagent structure
path = Path(".kilo/agents/parent/subagent.md")
```

```python
# BAD - Wrong location
path = Path("agents/agent_name.md")  # Not in .kilo/
```

### ✅ DO: Include Meaningful System Prompts

```python
# GOOD - Clear, detailed system prompt
agent = Agent(
    name="refactor",
    description="Improves code quality",
    system_prompt="""You are an expert code refactorer.

Your role is to:
1. Identify code smells
2. Suggest improvements
3. Maintain functionality
4. Follow SOLID principles

Always explain your changes.""",
)
```

```python
# BAD - Vague system prompt
agent = Agent(
    name="refactor",
    description="Refactors code",
    system_prompt="You refactor code.",  # Too brief
)
```

### ✅ DO: Organize Tools and Skills Logically

```python
# GOOD - Related tools grouped
code_agent = Agent(
    name="developer",
    tools=["bash", "python", "node"],  # All language tools
    skills=["code_generation", "debugging"],
)

test_agent = Agent(
    name="tester",
    tools=["pytest", "coverage", "bash"],  # Test-related tools
    skills=["test_writing", "coverage_analysis"],
)
```

### ✅ DO: Create Consistent Agent Naming

```python
# GOOD - Consistent, descriptive names
agents = {
    "code_generator": "Generates new code",
    "test_writer": "Writes comprehensive tests",
    "code_reviewer": "Reviews code for quality",
}

# BAD - Inconsistent naming
agents = {
    "coder": "Code generation",
    "testing": "Writes tests",
    "review_bot": "Code review",
}
```

---

## Troubleshooting

### Issue: "Agent name is required and must not be empty"

**Problem:**
```python
agent = Agent(
    name="",  # Empty name!
    description="Test",
    system_prompt="Test",
)
```

**Solution:**
```python
agent = Agent(
    name="meaningful_agent_name",  # Use non-empty name
    description="Test",
    system_prompt="Test",
)
```

### Issue: "System prompt is required and must not be empty"

**Problem:**
```python
agent = Agent(
    name="agent",
    description="Test",
    system_prompt="",  # Empty prompt!
)
```

**Solution:**
```python
agent = Agent(
    name="agent",
    description="Test",
    system_prompt="You are a helpful assistant...",  # Provide meaningful prompt
)
```

### Issue: Output file not created

**Problem:**
```python
# Trying to save but directory doesn't exist
Path("agents/agent.md").write_text(output)
```

**Solution:**
```python
# Create parent directories first
path = Path("agents/agent.md")
path.parent.mkdir(parents=True, exist_ok=True)  # Create dirs
path.write_text(output)
```

### Issue: Subagents not appearing in output

**Problem:**
```python
agent = Agent(
    name="parent",
    subagents=["child1", "child2"],
)

options = BuildOptions(
    include_subagents=False,  # Disabled!
)

output = builder.build(agent, options)
# Subagents won't appear
```

**Solution:**
```python
options = BuildOptions(
    include_subagents=True,  # Enable subagents
)

output = builder.build(agent, options)
# Subagents will appear
```

---

## API Reference

### KiloBuilder Class

#### Constructor

```python
def __init__(self, agents_dir: Path | str = "agents") -> None:
    """Initialize KiloBuilder.
    
    Args:
        agents_dir: Base directory for agent configurations
    """
```

#### Main Methods

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `build` | `build(agent: Agent, options: BuildOptions) -> str` | String | Builds YAML+MD output |
| `validate` | `validate(agent: Agent) -> list[str]` | List | Returns validation errors |
| `build_subagents` | `build_subagents(agent: Agent, options: BuildOptions) -> dict[str, str]` | Dict | Builds subagent files |
| `get_output_format` | `get_output_format() -> str` | String | Returns format description |
| `get_tool_name` | `get_tool_name() -> str` | String | Returns "kilo" |
| `supports_feature` | `supports_feature(feature: str) -> bool` | Bool | Checks feature support |

#### Validation Methods

```python
def validate(self, agent: Agent) -> list[str]:
    """Validate an Agent IR model for Kilo.
    
    Checks:
    - Agent name is non-empty
    - Agent description is non-empty
    - System prompt is non-empty
    
    Returns:
        List of error messages (empty if valid)
    """
```

#### Building Methods

```python
def build(self, agent: Agent, options: BuildOptions) -> str:
    """Build a Kilo agent configuration file.
    
    Args:
        agent: The Agent IR model
        options: Build configuration
    
    Returns:
        String with YAML frontmatter + Markdown content
    
    Raises:
        BuilderValidationError: If validation fails
    """

def build_subagents(self, agent: Agent, options: BuildOptions) -> dict[str, str]:
    """Build Kilo subagent configuration files.
    
    Generates subagent files in nested directory structure.
    
    Args:
        agent: Parent Agent IR model
        options: Build configuration
    
    Returns:
        Dict mapping subagent names to file contents
    
    Raises:
        BuilderValidationError: If any subagent is invalid
    """
```

#### Utility Methods

```python
def get_output_format(self) -> str:
    """Returns: "Kilo IDE Agent File (YAML frontmatter + Markdown)" """

def get_tool_name(self) -> str:
    """Returns: "kilo" """

def supports_feature(self, feature_name: str) -> bool:
    """Check if builder supports a feature.
    
    Supported features:
    - skills
    - workflows
    - rules
    - subagents
    - tools
    
    Args:
        feature_name: Name of feature to check
    
    Returns:
        True if supported, False otherwise
    """
```

### BuildOptions Class

```python
@dataclass
class BuildOptions:
    """Configuration for building agent output.
    
    Attributes:
        variant: "minimal" or "verbose"
        agent_name: Name of agent being built
        include_subagents: Include subagents (default: True)
        include_skills: Include skills (default: True)
        include_workflows: Include workflows (default: True)
        include_rules: Include rules (default: True)
        include_tools: Include tools (default: True)
    """
    
    variant: str = "minimal"
    agent_name: str = ""
    include_subagents: bool = True
    include_skills: bool = True
    include_workflows: bool = True
    include_rules: bool = True
    include_tools: bool = True
    
    def __post_init__(self) -> None:
        """Validate variant is 'minimal' or 'verbose'."""
```

---

## Full Working Examples

### Example 1: Simple Agent Builder

```python
from pathlib import Path
from promptosaurus.builders.kilo_builder import KiloBuilder
from promptosaurus.builders.base import BuildOptions, BuilderValidationError
from promptosaurus.ir.models import Agent

def build_simple_agent():
    """Build a simple agent with minimal configuration."""
    
    # Initialize builder
    builder = KiloBuilder(agents_dir=".kilo/agents")
    
    # Create agent
    agent = Agent(
        name="helper",
        description="Provides helpful assistance",
        system_prompt="You are a helpful assistant.",
        tools=["search"],
    )
    
    # Configure options
    options = BuildOptions(
        variant="minimal",
        agent_name="helper",
    )
    
    # Build
    try:
        output = builder.build(agent, options)
        
        # Save
        path = Path(".kilo/agents/helper.md")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output)
        
        print(f"✓ Built {agent.name}")
        return path
        
    except BuilderValidationError as e:
        print(f"✗ Build failed: {e.message}")
        return None

if __name__ == "__main__":
    path = build_simple_agent()
    if path:
        print(path.read_text())
```

### Example 2: Complex Multi-Subagent System

```python
from pathlib import Path
from promptosaurus.builders.kilo_builder import KiloBuilder
from promptosaurus.builders.base import BuildOptions, BuilderValidationError
from promptosaurus.ir.models import Agent

def build_multi_subagent_system():
    """Build a system with parent agent and multiple subagents."""
    
    builder = KiloBuilder(agents_dir=".kilo/agents")
    
    # Parent agent
    parent = Agent(
        name="orchestrator",
        description="Coordinates multiple specialized agents",
        system_prompt="""You are an orchestrator that delegates to specialists.

Your responsibilities:
- Route tasks to appropriate specialists
- Coordinate between agents
- Ensure quality output
- Manage overall workflow""",
        tools=["coordination", "logging"],
        subagents=["code_expert", "test_expert", "review_expert"],
    )
    
    # Build parent
    options = BuildOptions(variant="verbose")
    
    try:
        parent_output = builder.build(parent, options)
        parent_path = Path(".kilo/agents/orchestrator.md")
        parent_path.parent.mkdir(parents=True, exist_ok=True)
        parent_path.write_text(parent_output)
        print(f"✓ Built parent: orchestrator")
        
        # Build subagents
        subagent_files = builder.build_subagents(parent, options)
        
        for name, content in subagent_files.items():
            path = Path(f".kilo/agents/orchestrator/{name}.md")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            print(f"✓ Built subagent: {name}")
            
    except BuilderValidationError as e:
        print(f"✗ Build failed: {e.message}")

if __name__ == "__main__":
    build_multi_subagent_system()
```

### Example 3: Batch Building with Variants

```python
from pathlib import Path
from promptosaurus.builders.kilo_builder import KiloBuilder
from promptosaurus.builders.base import BuildOptions, BuilderValidationError
from promptosaurus.ir.models import Agent

def build_all_variants():
    """Build agents in both minimal and verbose variants."""
    
    builder = KiloBuilder(agents_dir=".kilo/agents")
    
    agents = [
        Agent(
            name="code",
            description="Generates code",
            system_prompt="You are an expert code generator.",
            tools=["bash", "python"],
            skills=["code_generation", "debugging"],
        ),
        Agent(
            name="test",
            description="Writes tests",
            system_prompt="You are an expert test engineer.",
            tools=["pytest", "coverage"],
            skills=["test_writing", "coverage_analysis"],
        ),
    ]
    
    variants = ["minimal", "verbose"]
    
    for agent in agents:
        for variant in variants:
            options = BuildOptions(
                variant=variant,
                agent_name=agent.name,
            )
            
            try:
                output = builder.build(agent, options)
                
                # Save with variant suffix
                dir_name = f".kilo/agents/{variant}"
                path = Path(dir_name) / f"{agent.name}.md"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(output)
                
                print(f"✓ {variant}: {agent.name}")
                
            except BuilderValidationError as e:
                print(f"✗ {variant}: {agent.name} - {e.message}")

if __name__ == "__main__":
    build_all_variants()
```

### Example 4: Dynamic Agent Configuration

```python
from pathlib import Path
from promptosaurus.builders.kilo_builder import KiloBuilder
from promptosaurus.builders.base import BuildOptions
from promptosaurus.ir.models import Agent

def build_from_config(config: dict) -> str:
    """Build agent from configuration dictionary."""
    
    builder = KiloBuilder()
    
    # Create agent from config
    agent = Agent(
        name=config["name"],
        description=config["description"],
        system_prompt=config["system_prompt"],
        tools=config.get("tools", []),
        skills=config.get("skills", []),
        subagents=config.get("subagents", []),
    )
    
    # Configure options from config
    options = BuildOptions(
        variant=config.get("variant", "minimal"),
        agent_name=agent.name,
        include_tools=config.get("include_tools", True),
        include_skills=config.get("include_skills", True),
        include_workflows=config.get("include_workflows", True),
        include_subagents=config.get("include_subagents", True),
    )
    
    # Build and return
    return builder.build(agent, options)

if __name__ == "__main__":
    # Example config
    config = {
        "name": "analyzer",
        "description": "Analyzes code for issues",
        "system_prompt": "You are a code analyzer focused on finding bugs.",
        "tools": ["grep", "bash"],
        "skills": ["static_analysis", "code_review"],
        "variant": "verbose",
    }
    
    output = build_from_config(config)
    print(output)
```

---

## Related Builders

For building other tools, see:
- [ClineBuilder Guide](./CLINE_BUILDER_GUIDE.md) - For Cline AI
- [ClaudeBuilder Guide](./CLAUDE_BUILDER_GUIDE.md) - For Claude API
- [CopilotBuilder Guide](./COPILOT_BUILDER_GUIDE.md) - For GitHub Copilot
- [CursorBuilder Guide](./CURSOR_BUILDER_GUIDE.md) - For Cursor IDE

---

## Support & Resources

- **Source Code:** `promptosaurus/builders/kilo_builder.py`
- **Base Class:** `promptosaurus/builders/base.py` (Builder)
- **IR Models:** `promptosaurus/ir/models.py` (Agent dataclass)
- **Examples:** `promptosaurus/builders/examples_usage.py`

