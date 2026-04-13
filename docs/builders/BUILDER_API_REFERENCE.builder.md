# Builder API Reference

Complete documentation for all 5 tool-specific builders: Kilo, Cline, Claude, Copilot, and Cursor.

## Table of Contents

- [Overview](#overview)
- [Quick Comparison](#quick-comparison)
- [KiloBuilder](#kilobuilder)
- [ClineBuilder](#clinebuilder)
- [ClaudeBuilder](#claudebuilder)
- [CopilotBuilder](#copilotbuilder)
- [CursorBuilder](#cursorbuilder)
- [Common API](#common-api)
- [Error Handling](#error-handling)
- [Examples](#examples)

---

## Overview

The Builder system provides a unified interface for generating tool-specific configuration files from Agent IR models. Each builder extends `AbstractBuilder` and implements a specific output format for its target tool.

### Key Concepts

- **Agent IR Model**: The intermediate representation that holds agent configuration (name, description, system prompt, tools, skills, workflows, subagents)
- **BuildOptions**: Configuration for the build process (variant selection, component inclusion flags)
- **Output Format**: Each builder produces tool-specific output (Markdown, JSON, YAML+Markdown)
- **Validation**: Each builder validates the Agent IR before building to ensure required fields are present

### When to Use Each Builder

| Use Case | Builder | Output |
|----------|---------|--------|
| Kilo IDE agent configuration | KiloBuilder | `.kilo/agents/{name}.md` (YAML+Markdown) |
| Cline AI rules | ClineBuilder | `.clinerules` (Markdown) |
| Claude Messages API | ClaudeBuilder | JSON dict (system, tools, instructions) |
| GitHub Copilot instructions | CopilotBuilder | `.github/instructions/{mode}.md` (YAML+Markdown) |
| Cursor IDE rules | CursorBuilder | `.cursorrules` (Markdown) |

---

## Quick Comparison

| Feature | Kilo | Cline | Claude | Copilot | Cursor |
|---------|------|-------|--------|---------|--------|
| Output Format | YAML+Markdown | Markdown | JSON dict | YAML+Markdown | Markdown |
| File Extension | `.md` | `.clinerules` | N/A | `.md` | `.cursorrules` |
| System Prompt Format | Plain text | Prose | String | Plain text | Prose |
| Tools Support | ✓ List | ✓ Descriptions | ✓ JSON Schema | ✓ List | ✓ Descriptions |
| Skills Support | ✓ | ✓ (use_skill pattern) | ✓ (instructions) | ✓ | ✓ |
| Workflows Support | ✓ | ✓ | ✓ (instructions) | ✓ | ✓ |
| Subagents Support | ✓ List | ✓ (use_skill pattern) | ✓ (instructions) | ✓ | ✓ List |
| Variants (minimal/verbose) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Component Selector | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## KiloBuilder

Builder for Kilo IDE agent configurations. Generates `.kilo/agents/{name}.md` files with YAML frontmatter and markdown sections.

### Overview

- **Target Tool**: Kilo IDE
- **Output Format**: YAML frontmatter + Markdown sections
- **File Location**: `.kilo/agents/{agent_name}.md`
- **Purpose**: Create agent configuration files for Kilo IDE with system prompt, tools, skills, workflows, and subagents

### API Signature

```python
class KiloBuilder(AbstractBuilder):
    def __init__(self, agents_dir: Path | str = "agents") -> None: ...
    
    def build(self, agent: Agent, options: BuildOptions) -> str: ...
    
    def validate(self, agent: Agent) -> list[str]: ...
    
    def get_output_format(self) -> str: ...
    
    def get_tool_name(self) -> str: ...
    
    def build_subagents(self, agent: Agent, options: BuildOptions) -> dict[str, str]: ...
```

### Parameters

#### `__init__(agents_dir)`
- **agents_dir** (Path | str, default: "agents"): Base directory for agent configurations

#### `build(agent, options)`
- **agent** (Agent): IR model with fields:
  - `name` (str, required): Agent name
  - `description` (str, required): Agent description
  - `system_prompt` (str, required): System prompt content
  - `tools` (list[str], optional): Tool names
  - `skills` (list[str], optional): Skill names
  - `workflow` (str, optional): Workflow definitions
  - `subagents` (list[str], optional): Subagent names
  
- **options** (BuildOptions):
  - `variant` (str): "minimal" or "verbose" (default: "minimal")
  - `include_tools` (bool, default: True)
  - `include_skills` (bool, default: True)
  - `include_workflows` (bool, default: True)
  - `include_subagents` (bool, default: True)

#### `validate(agent)`
- **agent** (Agent): Agent to validate
- **Returns**: list[str] of validation error messages (empty if valid)
- **Validates**: 
  - Agent name is not empty
  - Agent description is not empty
  - System prompt is not empty

### Returns

**build()** returns a `str` containing:
```
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

### Usage Example

```python
from src.builders.kilo_builder import KiloBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent

# Create an agent
agent = Agent(
    name="code",
    description="Expert software engineer",
    system_prompt="You are an expert software engineer...",
    tools=["read", "write", "bash"],
    skills=["refactoring", "testing"],
    workflow="Code-first development",
    subagents=["test", "review"]
)

# Create builder
builder = KiloBuilder(agents_dir="agents")

# Build with minimal variant
options = BuildOptions(variant="minimal")
output = builder.build(agent, options)

# Or build with all components
options_full = BuildOptions(
    variant="verbose",
    include_tools=True,
    include_skills=True,
    include_workflows=True,
    include_subagents=True
)
output_full = builder.build(agent, options_full)

# Build subagent files
subagent_files = builder.build_subagents(agent, options)
# Returns: {"test": "...", "review": "..."}
```

### Output Example

```yaml
---
name: "code"
description: "Expert software engineer"
model: "anthropic/claude-opus-4-1"
state_management: ".promptosaurus/sessions/"
---

# System Prompt

You are an expert software engineer responsible for:
- Writing clean, maintainable code
- Following SOLID principles
- Testing thoroughly

# Tools

- read
- write
- bash

# Skills

## Code Review
Review code for quality and best practices

## Refactoring
Improve code structure and readability

# Workflows

1. Analyze requirements
2. Write tests first
3. Implement code
4. Review and optimize

# Subagents

- test
- review
```

### Error Cases

**Invalid Agent**:
```python
invalid_agent = Agent(name="", description="...", system_prompt="...")
builder.build(invalid_agent, options)
# Raises: BuilderValidationError(errors=["Agent name is required..."])
```

**Missing System Prompt**:
```python
incomplete_agent = Agent(name="code", description="...", system_prompt="")
builder.build(incomplete_agent, options)
# Raises: BuilderValidationError(errors=["System prompt is required..."])
```

### Special Features

**Subagent Support**: `build_subagents()` generates individual subagent files with parent references:
```python
subagent_files = builder.build_subagents(agent, options)
# Creates nested structure:
# .kilo/agents/code/test.md (includes parent_agent: code)
# .kilo/agents/code/review.md (includes parent_agent: code)
```

---

## ClineBuilder

Builder for Cline AI configuration files. Generates `.clinerules` files with markdown formatting.

### Overview

- **Target Tool**: Cline AI
- **Output Format**: Pure Markdown (no YAML frontmatter)
- **File Location**: `.clinerules`
- **Purpose**: Create rules files for Cline AI assistant with system prompt and skill activation patterns

### API Signature

```python
class ClineBuilder(AbstractBuilder):
    def __init__(self, agents_dir: Path | str = "agents") -> None: ...
    
    def build(self, agent: Agent, options: BuildOptions) -> str: ...
    
    def validate(self, agent: Agent) -> list[str]: ...
    
    def get_output_format(self) -> str: ...
    
    def get_tool_name(self) -> str: ...
```

### Parameters

Same as KiloBuilder, but note that Cline output is pure Markdown (no YAML).

### Returns

**build()** returns a `str` containing:
```markdown
# {Agent Name} Rules

[System prompt as prose - no markdown formatting]

## Tools

Available tools:

- **tool1**: [Tool description]

## Skills

The following skills are available. Use them by calling use_skill::

### Skill: skill-name

Invoke by: `use_skill skill_name`

[Raw skills content]

## Workflows

[Workflow content]

## Subagents

You may delegate to these specialists:

### Subagent: subagent-name

Specializes in subagent-name tasks.

Invoke by: `use_skill subagent_name` or request 'subagent-name subagent'
```

### Usage Example

```python
from src.builders.cline_builder import ClineBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent

# Create agent
agent = Agent(
    name="cline-assistant",
    description="Cline development assistant",
    system_prompt="You are a development assistant...",
    tools=["read", "write", "bash"],
    skills=["code-review", "testing"],
    workflow="Development workflow",
    subagents=["refactor", "test"]
)

# Create builder
builder = ClineBuilder(agents_dir="agents")

# Build Cline rules
options = BuildOptions(
    variant="verbose",
    include_skills=True
)
output = builder.build(agent, options)

# Write to .clinerules file
with open(".clinerules", "w") as f:
    f.write(output)
```

### Output Example

```markdown
# cline-assistant Rules

You are a development assistant responsible for analyzing code, identifying improvements, and implementing changes while maintaining code quality standards.

## Tools

Available tools:

- **read**: Read files and directories to understand context
- **write**: Write and edit files
- **bash**: Execute terminal commands

## Skills

The following skills are available. Use them by calling use_skill::

### Skill: code-review

Invoke by: `use_skill code_review`

Review code for quality, performance, and maintainability.

### Skill: testing

Invoke by: `use_skill testing`

Write and execute tests to verify functionality.

## Workflows

1. Read the code to understand its structure
2. Analyze for improvements and issues
3. Write changes with tests
4. Verify all tests pass

## Subagents

You may delegate to these specialists:

### Subagent: refactor

Specializes in refactor tasks.

Invoke by: `use_skill refactor` or request 'refactor subagent'

### Subagent: test

Specializes in test tasks.

Invoke by: `use_skill test` or request 'test subagent'
```

### Key Feature: Skill Activation Pattern

Cline uses the `use_skill` pattern for invoking skills. Each skill is documented with its invocation syntax:

```markdown
### Skill: code-review

Invoke by: `use_skill code_review`
```

This pattern allows Cline to understand how to invoke specialized capabilities.

---

## ClaudeBuilder

Builder for Claude Messages API JSON output. Generates JSON-compatible dictionaries for Claude's tool use and instruction features.

### Overview

- **Target Tool**: Claude API (Messages API)
- **Output Format**: JSON dict with system, tools, and instructions
- **Return Type**: `dict[str, Any]` (JSON-serializable)
- **Purpose**: Create Claude-compatible configuration for use with Claude's tool use and system prompt features

### API Signature

```python
class ClaudeBuilder(AbstractBuilder):
    def __init__(self, agents_dir: Path | str = "agents") -> None: ...
    
    def build(self, agent: Agent, options: BuildOptions) -> dict[str, Any]: ...
    
    def validate(self, agent: Agent) -> list[str]: ...
    
    def get_output_format(self) -> str: ...
    
    def get_tool_name(self) -> str: ...
```

### Parameters

Same as KiloBuilder. Note that `build()` returns a dict instead of string.

### Returns

**build()** returns a `dict[str, Any]` with three keys:

```python
{
    "system": "You are an expert software engineer...",
    "tools": [
        {
            "name": "read",
            "description": "Tool: read",
            "input_schema": {
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "Parameter for the tool"}
                },
                "required": ["param"]
            }
        },
        ...
    ],
    "instructions": "Skills:\n- refactoring: ...\n\nWorkflows:\n..."
}
```

### Usage Example

```python
from src.builders.claude_builder import ClaudeBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent
import json

# Create agent
agent = Agent(
    name="code-assistant",
    description="Code analysis and improvement",
    system_prompt="You are an expert software engineer...",
    tools=["read", "write", "bash"],
    skills=["analysis", "refactoring"],
    workflow="Code improvement workflow",
    subagents=["test"]
)

# Create builder
builder = ClaudeBuilder(agents_dir="agents")

# Build Claude output
options = BuildOptions(
    variant="verbose",
    include_tools=True,
    include_skills=True
)
output = builder.build(agent, options)

# JSON serialize
json_str = json.dumps(output, indent=2)

# Use with Claude API
import anthropic

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-opus-4-1",
    max_tokens=2048,
    system=output["system"],
    tools=output["tools"],
    messages=[
        {"role": "user", "content": "Review this code..."}
    ]
)
```

### Output Example

```json
{
  "system": "You are an expert software engineer responsible for analyzing and improving code while following best practices.",
  "tools": [
    {
      "name": "read",
      "description": "Tool: read",
      "input_schema": {
        "type": "object",
        "properties": {
          "param": {"type": "string", "description": "Parameter for the tool"}
        },
        "required": ["param"]
      }
    },
    {
      "name": "write",
      "description": "Tool: write",
      "input_schema": {
        "type": "object",
        "properties": {
          "param": {"type": "string", "description": "Parameter for the tool"}
        },
        "required": ["param"]
      }
    },
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
    }
  ],
  "instructions": "Skills:\n- analysis: Analyze code for improvements\n- refactoring: Refactor code for clarity\n\nWorkflows:\nCode improvement workflow instructions...\n\nSubagents:\n- test: Specialized agent for test tasks"
}
```

### Key Feature: JSON Serialization

Claude builder validates that output is JSON-serializable:

```python
try:
    json.dumps(output)  # Validates JSON serializability
except (TypeError, ValueError) as e:
    raise BuilderValidationError(...)
```

This ensures compatibility with Claude's Messages API.

---

## CopilotBuilder

Builder for GitHub Copilot instructions files. Generates `.github/instructions/{mode}.md` files with YAML frontmatter containing `applyTo` metadata.

### Overview

- **Target Tool**: GitHub Copilot
- **Output Format**: YAML frontmatter (with applyTo) + Markdown sections
- **File Location**: `.github/instructions/{mode}.md`
- **Purpose**: Create GitHub-specific instructions with context metadata for Copilot integration

### API Signature

```python
class CopilotBuilder(AbstractBuilder):
    def __init__(self, agents_dir: Path | str = "agents") -> None: ...
    
    def build(self, agent: Agent, options: BuildOptions) -> str: ...
    
    def validate(self, agent: Agent) -> list[str]: ...
    
    def get_output_format(self) -> str: ...
    
    def get_tool_name(self) -> str: ...
```

### Parameters

Same as KiloBuilder.

### Returns

**build()** returns a `str` containing:
```yaml
---
applyTo:
  - model: "agent_name"
  - parentAgents: []
---

# Copilot Agent_Name Agent Instructions

[System prompt as prose]

## Tools

- tool1
- tool2

## Skills

[Skills content]

## Workflows

[Workflows content]

## Subagents

You may delegate to specialized agents:

### Subagent: subagent-name
Specializes in subagent-name tasks.
```

### Usage Example

```python
from src.builders.copilot_builder import CopilotBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent

# Create agent
agent = Agent(
    name="code",
    description="GitHub Copilot code agent",
    system_prompt="You are a GitHub Copilot instance...",
    tools=["github-api", "git"],
    skills=["code-completion"],
    workflow="Code enhancement",
    subagents=["review"]
)

# Create builder
builder = CopilotBuilder(agents_dir="agents")

# Build Copilot instructions
options = BuildOptions(
    variant="verbose",
    include_tools=True
)
output = builder.build(agent, options)

# Write to .github/instructions/code.md
import os
os.makedirs(".github/instructions", exist_ok=True)
with open(".github/instructions/code.md", "w") as f:
    f.write(output)
```

### Output Example

```yaml
---
applyTo:
  - model: "code"
  - parentAgents: []
---

# Copilot Code Agent Instructions

You are a GitHub Copilot instance configured for code generation and completion. Focus on:
- Writing clean, maintainable code
- Following Python/JavaScript conventions
- Providing helpful context and explanations

## Tools

- github-api
- git

## Skills

Code completion techniques and best practices

## Workflows

1. Understand context from open file
2. Analyze surrounding code
3. Generate appropriate completions
4. Verify syntax and semantics

## Subagents

You may delegate to specialized agents:

### Subagent: review
Specializes in review tasks.
```

### Key Feature: applyTo Metadata

The `applyTo` field specifies when these instructions apply:

```yaml
applyTo:
  - model: "code"        # Applies to 'code' mode
  - parentAgents: []     # Applies to root agents
```

This allows GitHub Copilot to apply instructions contextually.

---

## CursorBuilder

Builder for Cursor IDE configuration files. Generates `.cursorrules` files with markdown formatting and constraint-based instructions.

### Overview

- **Target Tool**: Cursor IDE
- **Output Format**: Pure Markdown (no YAML frontmatter)
- **File Location**: `.cursorrules`
- **Purpose**: Create rules files for Cursor IDE with constraints, tools, and workflows

### API Signature

```python
class CursorBuilder(AbstractBuilder):
    def __init__(self, agents_dir: Path | str = "agents") -> None: ...
    
    def build(self, agent: Agent, options: BuildOptions) -> str: ...
    
    def validate(self, agent: Agent) -> list[str]: ...
    
    def get_output_format(self) -> str: ...
    
    def get_tool_name(self) -> str: ...
```

### Parameters

Same as KiloBuilder.

### Returns

**build()** returns a `str` containing:
```markdown
# {Agent Name} Rules

You are an expert [description].

## Core Constraints

- Type hints required on all public functions
- [Additional constraints]

## Available Tools

### read

Purpose: [Description]
Usage: [Usage information]

### write

Purpose: [Description]
Usage: [Usage information]

## Workflows

[Workflow content]

## Subagents Available

- **subagent1**: Specializes in subagent1 tasks
- **subagent2**: Specializes in subagent2 tasks
```

### Usage Example

```python
from src.builders.cursor_builder import CursorBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent

# Create agent
agent = Agent(
    name="code",
    description="Expert code editor with refactoring capabilities",
    system_prompt="You are Cursor, an advanced code editor...",
    tools=["read", "write", "bash"],
    workflow="Cursor editing workflow",
    subagents=["refactor", "debug"]
)

# Create builder
builder = CursorBuilder(agents_dir="agents")

# Build Cursor rules
options = BuildOptions(
    variant="verbose",
    include_tools=True,
    include_workflows=True
)
output = builder.build(agent, options)

# Write to .cursorrules file
with open(".cursorrules", "w") as f:
    f.write(output)
```

### Output Example

```markdown
# code Rules

You are an expert code editor with refactoring capabilities focused on improving code quality, maintainability, and performance.

## Core Constraints

- Type hints required on all public functions
- No `any` types without explicit justification
- Read code BEFORE writing code
- Match existing patterns exactly

## Available Tools

### read

Purpose: Read files and understand code structure
Usage: Call with file paths to examine code

### write

Purpose: Edit and create files with modifications
Usage: Call with content and file path

### bash

Purpose: Execute shell commands and scripts
Usage: Call with command and arguments

## Workflows

1. Read the existing code structure
2. Understand the patterns and conventions
3. Make targeted improvements
4. Test changes thoroughly

## Subagents Available

- **refactor**: Specializes in refactor tasks
- **debug**: Specializes in debug tasks
```

### Key Feature: Core Constraints

Cursor builder includes a "Core Constraints" section with development best practices:

```markdown
## Core Constraints

- Type hints required on all public functions
- No `any` types without explicit justification
- Read code BEFORE writing code
- Match existing patterns exactly
```

These constraints guide Cursor's behavior.

---

## Common API

All builders implement the `AbstractBuilder` interface.

### AbstractBuilder Interface

```python
class AbstractBuilder(ABC):
    @abstractmethod
    def build(self, agent: Agent, options: BuildOptions) -> str | dict[str, Any]: ...
    
    @abstractmethod
    def validate(self, agent: Agent) -> list[str]: ...
    
    def supports_feature(self, feature_name: str) -> bool: ...
    
    def get_output_format(self) -> str: ...
    
    def get_tool_name(self) -> str: ...
```

### Shared Methods

#### `validate(agent) -> list[str]`

Validates an Agent IR model. All builders check:
- Agent name is not empty
- Agent description is not empty
- System prompt is not empty

Returns list of error messages (empty if valid).

#### `supports_feature(feature_name) -> bool`

Checks if builder supports a feature. Supported features:
- "skills"
- "workflows"
- "rules"
- "subagents"
- "tools"

#### `get_output_format() -> str`

Returns human-readable description:
- KiloBuilder: "Kilo IDE Agent File (YAML frontmatter + Markdown)"
- ClineBuilder: "Cline AI Rules File (Markdown)"
- ClaudeBuilder: "Claude Messages API JSON (dict)"
- CopilotBuilder: "GitHub Copilot Instructions File (YAML frontmatter + Markdown)"
- CursorBuilder: "Cursor AI Rules File (Markdown)"

#### `get_tool_name() -> str`

Returns tool name:
- KiloBuilder: "kilo"
- ClineBuilder: "cline"
- ClaudeBuilder: "claude"
- CopilotBuilder: "copilot"
- CursorBuilder: "cursor"

### BuildOptions Class

```python
@dataclass
class BuildOptions:
    variant: str = "minimal"
    agent_name: str = ""
    include_subagents: bool = True
    include_skills: bool = True
    include_workflows: bool = True
    include_rules: bool = True
    include_tools: bool = True
```

**Validation**: `variant` must be "minimal" or "verbose"

---

## Error Handling

All builders raise `BuilderValidationError` for invalid inputs.

### BuilderValidationError

```python
from src.builders.errors import BuilderValidationError

try:
    builder.build(invalid_agent, options)
except BuilderValidationError as e:
    print(f"Validation errors: {e.errors}")
    print(f"Message: {e.message}")
```

### Common Error Cases

**Invalid Agent Name**:
```
BuilderValidationError: Invalid agent '': Agent name is required and must not be empty
```

**Missing System Prompt**:
```
BuilderValidationError: Invalid agent 'code': System prompt is required and must not be empty
```

**Invalid Variant**:
```
ValueError: Invalid variant: invalid. Must be 'minimal' or 'verbose'
```

**Non-Serializable Output (Claude)**:
```
BuilderValidationError: Invalid output from Claude builder: Output is not JSON serializable
```

---

## Examples

### Complete Workflow: Building for All Tools

```python
from pathlib import Path
from src.builders.factory import BuilderFactory
from src.builders.base import BuildOptions
from src.ir.registry import AgentRegistry

# Load agent
registry = AgentRegistry(base_path="agents")
agent = registry.load("code")

# Create options
options = BuildOptions(variant="verbose")

# Build for all tools
factory = BuilderFactory()
tools = ["kilo", "cline", "claude", "copilot", "cursor"]

outputs = {}
for tool_name in tools:
    builder = factory.get_builder(tool_name)
    output = builder.build(agent, options)
    outputs[tool_name] = output

# Write outputs to appropriate locations
# Kilo -> .kilo/agents/code.md
# Cline -> .clinerules
# Claude -> code.json (JSON)
# Copilot -> .github/instructions/code.md
# Cursor -> .cursorrules
```

### Minimal vs Verbose

```python
# Minimal variant (lightweight)
minimal_options = BuildOptions(
    variant="minimal",
    include_tools=True,
    include_skills=False,  # Skip skills
    include_workflows=False  # Skip workflows
)
minimal_output = builder.build(agent, minimal_options)

# Verbose variant (comprehensive)
verbose_options = BuildOptions(
    variant="verbose",
    include_tools=True,
    include_skills=True,
    include_workflows=True,
    include_subagents=True
)
verbose_output = builder.build(agent, verbose_options)
```

### Error Handling Pattern

```python
from src.builders.errors import BuilderValidationError

try:
    # Validate first (optional but recommended)
    errors = builder.validate(agent)
    if errors:
        print(f"Validation errors: {errors}")
        return
    
    # Build
    output = builder.build(agent, options)
    
except BuilderValidationError as e:
    print(f"Builder error: {e.message}")
    print(f"Details: {e.errors}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Component Selection

Each builder uses `ComponentSelector` to choose components based on variant:

```python
# Internally, builders do this:
selector = ComponentSelector(agents_dir="agents")

# Minimal variant selects lightweight versions
bundle = selector.select(agent, variant=Variant.MINIMAL)

# Verbose variant selects comprehensive versions
bundle = selector.select(agent, variant=Variant.VERBOSE)

# Bundle contains:
# - prompt: System prompt
# - skills: Skills content
# - workflow: Workflow content
# - rules: Rules content
```

---

## Integration with CLI

All builders are accessible via the `prompt-build` CLI tool:

```bash
# Build Kilo agent
prompt-build --tool kilo --agent code --variant verbose

# Build all formats
for tool in kilo cline claude copilot cursor; do
  prompt-build --tool $tool --agent code --variant verbose
done
```

See the CLI documentation for more details.

---

## Performance

All builders are optimized for fast generation:
- **Single agent, single tool**: < 0.05 seconds
- **Single agent, all 5 tools**: < 0.05 seconds
- **Memory usage**: < 10 MB per agent

See `PERFORMANCE_REPORT.md` for detailed benchmarks.

---

## Related Documentation

- **IR Models**: `docs/IR_MODEL_REFERENCE.md` - Agent model structure
- **Component System**: `docs/COMPONENT_SYSTEM.md` - Skills, workflows, rules
- **CLI Tool**: `docs/PROMPT_BUILD_CLI.md` - Command-line interface
- **Builder Factory**: `src/builders/factory.py` - Builder instantiation
- **Performance**: `docs/PERFORMANCE_REPORT.md` - Performance metrics
