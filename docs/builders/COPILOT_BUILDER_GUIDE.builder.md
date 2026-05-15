# CopilotBuilder Comprehensive Guide

A detailed guide for building GitHub Copilot instructions files from Agent IR models.

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

**CopilotBuilder** is the builder for [GitHub Copilot](https://github.com/features/copilot), GitHub's AI-powered code completion and generation tool. It transforms Agent IR models into Copilot instructions files with YAML frontmatter and markdown sections.

### What CopilotBuilder Does

- **Input:** Agent IR models (Python dataclasses with agent definitions)
- **Output:** YAML frontmatter + Markdown files
- **Target:** `.github/instructions/` directory for Copilot configuration
- **Supports:** System prompts, tool definitions, skills, workflows, and subagents

### Output Format

CopilotBuilder generates files with YAML metadata and markdown content:

```yaml
---
applyTo:
  - model: "code"
  - parentAgents: []
---

# Copilot Code Agent Instructions

You are an expert software engineer...

## Tools

- bash
- python

## Skills

### Skill: code-generation
Invoke by: `use_skill code_generation`

## Workflows

1. Understand requirements
2. Design solution
3. Implement code

## Subagents

### Subagent: test-writer
Specializes in test-writer tasks.
Invoke by: `use_skill test_writer` or request 'test-writer subagent'
```

### Key Features

✅ YAML frontmatter with applyTo metadata
✅ Markdown sections for content
✅ GitHub Copilot compatible format
✅ Skill and workflow support
✅ Subagent delegation
✅ Model-specific configuration

---

## Quick Start

### Most Basic Example

```python
from prompticorn.builders.copilot_builder import CopilotBuilder
from prompticorn.builders.base import BuildOptions
from prompticorn.ir.models import Agent

# Create a builder
builder = CopilotBuilder(agents_dir=".github/instructions")

# Create an agent
agent = Agent(
    name="code",
    description="Code generation and refinement",
    system_prompt="You are an expert software engineer skilled in clean code principles.",
    tools=["bash", "python"],
)

# Build the instructions
options = BuildOptions(variant="minimal", agent_name="code")
output = builder.build(agent, options)

print(output)
```

### Expected Output

```yaml
---
applyTo:
  - model: code
  - parentAgents: []
---

# Copilot Code Agent Instructions

You are an expert software engineer skilled in clean code principles.

## Tools

- bash
- python
```

---

## Installation & Setup

### Prerequisites

- Python 3.11+
- GitHub Copilot integration in your IDE
- Agent IR models properly defined

### Import

```python
from prompticorn.builders.copilot_builder import CopilotBuilder
from prompticorn.builders.base import BuildOptions, BuilderValidationError
from prompticorn.ir.models import Agent
```

### Initialize

```python
# Option 1: Default initialization
builder = CopilotBuilder()

# Option 2: With custom instructions directory
builder = CopilotBuilder(agents_dir=".github/instructions")

# Option 3: Using Path object
from pathlib import Path
builder = CopilotBuilder(agents_dir=Path(".github/copilot-instructions"))
```

### Verify Setup

```python
# Check tool information
print(builder.get_tool_name())          # Returns: "copilot"
print(builder.get_output_format())      # Returns: "GitHub Copilot Instructions File..."

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
    name="refactor",
    description="Code refactoring and optimization",
    system_prompt="""You are an expert code refactorer.

Your responsibilities:
- Identify code smells
- Suggest improvements
- Maintain backward compatibility
- Follow SOLID principles
- Improve readability and performance""",
    tools=["bash", "python", "git"],
    skills=["refactoring", "optimization"],
)
```

### 2. Validate Agent

```python
# Validate before building
errors = builder.validate(agent)

if errors:
    print("Validation failed:")
    for error in errors:
        print(f"  - {error}")
else:
    print("Agent validation passed!")
```

### 3. Create Build Options

```python
from prompticorn.builders.base import BuildOptions

options = BuildOptions(
    variant="verbose",
    agent_name="refactor",
    include_tools=True,
    include_skills=True,
    include_workflows=True,
)
```

### 4. Build Instructions

```python
try:
    instructions = builder.build(agent, options)
    print(instructions)
except BuilderValidationError as e:
    print(f"Build failed: {e.message}")
```

### 5. Save to .github/instructions/

```python
from pathlib import Path

# Generate output
instructions = builder.build(agent, options)

# Save to instructions directory
instructions_path = Path(".github/instructions/refactor.md")
instructions_path.parent.mkdir(parents=True, exist_ok=True)
instructions_path.write_text(instructions)

print(f"✓ Saved to {instructions_path}")
```

---

## Advanced Usage Patterns

### Pattern 1: Multiple Model Instructions

Copilot supports different modes (code, edit, etc.). Build instructions for each.

```python
models = ["code", "edit", "explain"]

for model_name in models:
    agent = Agent(
        name=model_name,
        description=f"Copilot {model_name} mode",
        system_prompt=f"You are a {model_name} assistant...",
        tools=["bash"],
    )
    
    options = BuildOptions(variant="verbose", agent_name=model_name)
    
    try:
        instructions = builder.build(agent, options)
        path = Path(f".github/instructions/{model_name}.md")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(instructions)
        print(f"✓ Built {model_name}")
    except BuilderValidationError as e:
        print(f"✗ Failed {model_name}: {e.message}")
```

### Pattern 2: Skill-Based Delegation

```python
# Agent with delegation to skills
orchestrator = Agent(
    name="orchestrator",
    description="Coordinates Copilot skills",
    system_prompt="""You are an orchestrator.

When you encounter:
- Code quality issues → use_skill refactoring
- Performance concerns → use_skill optimization
- Testing requirements → use_skill test_writing
- Documentation needs → use_skill documentation""",
    tools=["coordination"],
    skills=["refactoring", "optimization", "test_writing", "documentation"],
)

options = BuildOptions(
    variant="verbose",
    include_skills=True,
)

output = builder.build(orchestrator, options)
# Output includes all skill invocations
```

### Pattern 3: Hierarchical Subagents

```python
# Parent agent with specialized subagents
parent = Agent(
    name="chief_engineer",
    description="Oversees code development",
    system_prompt="""You are the chief engineer.

You may delegate to:
- Architects (design decisions)
- Implementers (code writing)
- Reviewers (quality assurance)
- Testers (test writing)""",
    tools=["coordination"],
    subagents=["architect", "implementer", "reviewer", "tester"],
)

# Build parent and subagents
parent_options = BuildOptions(
    variant="verbose",
    include_subagents=True,
)

parent_instructions = builder.build(parent, parent_options)

# Save parent
parent_path = Path(".github/instructions/chief.md")
parent_path.parent.mkdir(parents=True, exist_ok=True)
parent_path.write_text(parent_instructions)

print("✓ Built chief engineer instructions")
```

### Pattern 4: Tool-Specific Instructions

```python
# Build instructions tailored to specific tools
def build_tool_specific(tool_name: str) -> str:
    agent = Agent(
        name=f"tool_{tool_name}",
        description=f"Specialized in {tool_name}",
        system_prompt=f"""You are a {tool_name} specialist.

Expert in:
- {tool_name} best practices
- Common patterns
- Error handling
- Performance optimization""",
        tools=[tool_name],
        skills=[f"{tool_name}_expertise"],
    )
    
    options = BuildOptions(
        variant="verbose",
        agent_name=f"tool_{tool_name}",
        include_tools=True,
    )
    
    return builder.build(agent, options)

# Build for different tools
for tool in ["python", "javascript", "typescript"]:
    instructions = build_tool_specific(tool)
    path = Path(f".github/instructions/{tool}.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(instructions)
```

### Pattern 5: Dynamic Configuration

```python
from typing import Any

def build_copilot_from_config(config: dict[str, Any]) -> str:
    """Build Copilot instructions from configuration."""
    
    agent = Agent(
        name=config.get("name", "default"),
        description=config.get("description", ""),
        system_prompt=config.get("system_prompt", ""),
        tools=config.get("tools", []),
        skills=config.get("skills", []),
        subagents=config.get("subagents", []),
    )
    
    options = BuildOptions(
        variant=config.get("variant", "verbose"),
        agent_name=agent.name,
        include_tools=config.get("include_tools", True),
        include_skills=config.get("include_skills", True),
        include_workflows=config.get("include_workflows", True),
        include_subagents=config.get("include_subagents", True),
    )
    
    return builder.build(agent, options)

# Usage
config = {
    "name": "feature_dev",
    "description": "Feature development assistant",
    "system_prompt": "You develop new features...",
    "tools": ["bash", "python", "git"],
    "skills": ["feature_design", "implementation"],
    "variant": "verbose",
}

instructions = build_copilot_from_config(config)
```

---

## Configuration Options

### BuildOptions for Copilot

```python
@dataclass
class BuildOptions:
    variant: str = "minimal"          # minimal or verbose
    agent_name: str = ""              # Agent/model name
    include_subagents: bool = True    # Include subagents
    include_skills: bool = True       # Include skills
    include_workflows: bool = True    # Include workflows
    include_rules: bool = True        # Include rules
    include_tools: bool = True        # Include tools
```

### ApplyTo Metadata

Copilot instructions use the `applyTo` field to specify where they apply:

```yaml
applyTo:
  - model: "code"              # Apply to code mode
  - parentAgents: []           # Root agent (no parent)
```

### When to Use Variants

**minimal:**
- Simple, focused instructions
- Smaller files
- Specific to one task

**verbose:**
- Complete guidelines
- Full skill definitions
- Detailed workflows

---

## Common Patterns & Best Practices

### ✅ DO: Include Clear Model Names

```python
# GOOD - Clear, specific names
agents = [
    Agent(name="code", description="Code generation", ...),
    Agent(name="refactor", description="Code refactoring", ...),
    Agent(name="test", description="Test writing", ...),
]
```

```python
# BAD - Generic names
agents = [
    Agent(name="agent1", ...),
    Agent(name="agent2", ...),
]
```

### ✅ DO: Write Instructions for Copilot's Workflow

```python
# GOOD - Instructions that Copilot understands
agent = Agent(
    name="code",
    system_prompt="""When asked to generate code:
1. Understand the requirements
2. Check existing patterns
3. Generate clean code
4. Consider edge cases""",
)
```

### ✅ DO: Use Skill Invocation Syntax

```python
# GOOD - Copilot-compatible syntax
agent = Agent(
    name="main",
    system_prompt="""For complex tasks, delegate:

- Code review → use_skill code_review
- Performance → use_skill optimization
- Tests → use_skill test_generation""",
)
```

### ✅ DO: Organize Tools by Category

```python
# GOOD - Grouped logically
devtools = Agent(
    name="dev",
    tools=["bash", "python", "git"],  # Development tools
)

data_tools = Agent(
    name="data",
    tools=["python", "sql", "bash"],  # Data tools
)
```

### ✅ DO: Keep System Prompts Focused

```python
# GOOD - Focused on role and responsibilities
agent = Agent(
    name="refactor",
    system_prompt="""You are a refactoring specialist.

Your goals:
1. Improve code clarity
2. Reduce complexity
3. Maintain functionality
4. Follow SOLID principles""",
)
```

---

## Troubleshooting

### Issue: "Agent name is required"

**Problem:**
```python
agent = Agent(name="", ...)
```

**Solution:**
```python
agent = Agent(name="meaningful_name", ...)
```

### Issue: "System prompt is required"

**Problem:**
```python
agent = Agent(system_prompt="", ...)
```

**Solution:**
```python
agent = Agent(system_prompt="You are a helpful assistant...", ...)
```

### Issue: Instructions file not recognized by Copilot

**Problem:**
- File not in `.github/instructions/`
- YAML frontmatter malformed
- Model name not recognized

**Solution:**
```python
# Ensure proper location
path = Path(".github/instructions/code.md")

# Verify YAML frontmatter
instructions = builder.build(agent, options)
# Should start with: ---
#                   applyTo:
#                   ...
```

### Issue: Subagents not available to Copilot

**Problem:**
```python
options = BuildOptions(include_subagents=False)  # Disabled!
```

**Solution:**
```python
options = BuildOptions(include_subagents=True)  # Enable
```

---

## API Reference

### CopilotBuilder Class

#### Constructor

```python
def __init__(self, agents_dir: Path | str = "agents") -> None:
    """Initialize CopilotBuilder.
    
    Args:
        agents_dir: Base directory for agent configurations
    """
```

#### Core Methods

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `build` | `build(agent: Agent, options: BuildOptions) -> str` | String | Builds instructions file |
| `validate` | `validate(agent: Agent) -> list[str]` | List | Returns validation errors |
| `get_output_format` | `get_output_format() -> str` | String | Returns format description |
| `get_tool_name` | `get_tool_name() -> str` | String | Returns "copilot" |
| `supports_feature` | `supports_feature(feature: str) -> bool` | Bool | Checks feature support |

#### Main Build Method

```python
def build(self, agent: Agent, options: BuildOptions) -> str:
    """Build a GitHub Copilot instructions file.
    
    Args:
        agent: The Agent IR model to build from
        options: Build configuration options
    
    Returns:
        String containing YAML frontmatter + markdown sections
    
    Raises:
        BuilderValidationError: If the agent model is invalid
    """
```

#### Internal Methods (Reference)

```python
def _build_frontmatter(self, agent: Agent) -> dict[str, Any]:
    """Build YAML frontmatter with applyTo metadata."""

def _build_apply_to_list(self, agent: Agent) -> list[dict[str, Any]]:
    """Build the applyTo list for Copilot context."""

def _format_header(self, agent: Agent) -> str:
    """Format header for Copilot instructions."""

def _format_tools_section(self, tools: list[str]) -> str:
    """Format tools section."""

def _format_skills_section(self, skills_content: str, skill_names: list[str]) -> str:
    """Format skills section."""

def _format_workflows_section(self, workflow_content: str) -> str:
    """Format workflows section."""

def _format_subagents_section(self, subagent_names: list[str]) -> str:
    """Format subagents section."""
```

---

## Full Working Examples

### Example 1: Simple Code Mode

```python
from prompticorn.builders.copilot_builder import CopilotBuilder
from prompticorn.builders.base import BuildOptions
from prompticorn.ir.models import Agent
from pathlib import Path

def build_code_mode_instructions():
    """Build instructions for Copilot code mode."""
    
    builder = CopilotBuilder(agents_dir=".github/instructions")
    
    agent = Agent(
        name="code",
        description="Code generation and completion",
        system_prompt="""You are GitHub Copilot's code generation engine.

Your role:
- Generate clean, well-formatted code
- Follow project conventions
- Handle edge cases
- Provide efficient solutions
- Include helpful comments""",
        tools=["bash", "python", "javascript"],
    )
    
    options = BuildOptions(
        variant="verbose",
        agent_name="code",
        include_tools=True,
    )
    
    instructions = builder.build(agent, options)
    
    # Save
    path = Path(".github/instructions/code.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(instructions)
    
    print(f"✓ Built Copilot code instructions: {path}")
    return instructions

if __name__ == "__main__":
    instructions = build_code_mode_instructions()
```

### Example 2: Complete Multi-Mode Setup

```python
from prompticorn.builders.copilot_builder import CopilotBuilder
from prompticorn.builders.base import BuildOptions
from prompticorn.ir.models import Agent
from pathlib import Path

def build_all_copilot_modes():
    """Build complete Copilot instructions for all modes."""
    
    builder = CopilotBuilder(agents_dir=".github/instructions")
    
    modes = {
        "code": {
            "description": "Code generation and completion",
            "system_prompt": "You generate clean, efficient code...",
            "tools": ["bash", "python", "javascript", "typescript"],
        },
        "refactor": {
            "description": "Code refactoring and optimization",
            "system_prompt": "You improve existing code for clarity and performance...",
            "tools": ["bash", "python"],
        },
        "test": {
            "description": "Test generation and coverage",
            "system_prompt": "You write comprehensive, maintainable tests...",
            "tools": ["pytest", "mocha"],
        },
        "explain": {
            "description": "Code explanation and documentation",
            "system_prompt": "You explain code clearly and concisely...",
            "tools": ["markdown"],
        },
    }
    
    options = BuildOptions(variant="verbose", include_tools=True)
    
    for mode_name, mode_config in modes.items():
        agent = Agent(
            name=mode_name,
            description=mode_config["description"],
            system_prompt=mode_config["system_prompt"],
            tools=mode_config["tools"],
        )
        
        try:
            instructions = builder.build(agent, options)
            path = Path(f".github/instructions/{mode_name}.md")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(instructions)
            print(f"✓ Built {mode_name}")
        except Exception as e:
            print(f"✗ Failed {mode_name}: {e}")

if __name__ == "__main__":
    build_all_copilot_modes()
```

### Example 3: Skill-Based Orchestration

```python
from prompticorn.builders.copilot_builder import CopilotBuilder
from prompticorn.builders.base import BuildOptions
from prompticorn.ir.models import Agent
from pathlib import Path

def build_skill_orchestrator():
    """Build Copilot orchestrator with skill delegation."""
    
    builder = CopilotBuilder()
    
    agent = Agent(
        name="orchestrator",
        description="Skill-based Copilot orchestrator",
        system_prompt="""You coordinate between Copilot skills.

Available skills and when to use them:

- code_generation: New code from requirements
- refactoring: Improve existing code
- test_writing: Create tests
- documentation: Write docs
- debugging: Fix bugs
- optimization: Improve performance

Match tasks to appropriate skills.""",
        tools=["coordination"],
        skills=[
            "code_generation",
            "refactoring",
            "test_writing",
            "documentation",
            "debugging",
            "optimization",
        ],
    )
    
    options = BuildOptions(
        variant="verbose",
        include_skills=True,
    )
    
    instructions = builder.build(agent, options)
    
    path = Path(".github/instructions/orchestrator.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(instructions)
    
    print(f"✓ Built skill orchestrator: {path}")
    return instructions

if __name__ == "__main__":
    instructions = build_skill_orchestrator()
```

### Example 4: Project-Specific Configuration

```python
from prompticorn.builders.copilot_builder import CopilotBuilder
from prompticorn.builders.base import BuildOptions
from prompticorn.ir.models import Agent
from pathlib import Path
import json

def build_project_config(project_config_path: str):
    """Build Copilot instructions from project configuration."""
    
    # Load project config
    with open(project_config_path) as f:
        project = json.load(f)
    
    builder = CopilotBuilder()
    
    agent = Agent(
        name="project_expert",
        description=f"Expert in {project['name']}",
        system_prompt=f"""You are an expert in {project['name']}.

Project details:
- Language: {project.get('language', 'multiple')}
- Framework: {project.get('framework', 'none')}
- Style: {project.get('style_guide', 'standard')}

Key principles:
{chr(10).join(f'- {p}' for p in project.get('principles', []))}""",
        tools=project.get("tools", []),
        skills=project.get("skills", []),
    )
    
    options = BuildOptions(
        variant="verbose",
        include_tools=True,
        include_skills=True,
    )
    
    instructions = builder.build(agent, options)
    
    path = Path(".github/instructions/project.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(instructions)
    
    print(f"✓ Built project instructions: {path}")

if __name__ == "__main__":
    build_project_config("project.json")
```

---

## Related Builders

For building other tools, see:
- [KiloBuilder Guide](./KILO_BUILDER_GUIDE.md) - For Kilo IDE
- [ClineBuilder Guide](./CLINE_BUILDER_GUIDE.md) - For Cline AI
- [ClaudeBuilder Guide](./CLAUDE_BUILDER_GUIDE.md) - For Claude API
- [CursorBuilder Guide](./CURSOR_BUILDER_GUIDE.md) - For Cursor IDE

---

## Support & Resources

- **Source Code:** `prompticorn/builders/copilot_builder.py`
- **Base Class:** `prompticorn/builders/base.py` (Builder)
- **IR Models:** `prompticorn/ir/models.py` (Agent dataclass)
- **Examples:** `prompticorn/builders/examples_usage.py`
- **Copilot Docs:** [github.com/features/copilot](https://github.com/features/copilot)
- **Copilot Instructions:** [docs.github.com/en/copilot](https://docs.github.com/en/copilot)

