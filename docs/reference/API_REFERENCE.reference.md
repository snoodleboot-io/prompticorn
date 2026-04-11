# API Reference

Complete API documentation for Promptosaurus builders, IR models, loaders, and registry.

**Table of Contents:**
- [Builders](#builders)
- [Core Infrastructure](#core-infrastructure)
- [IR Models](#ir-models)
- [Loaders](#loaders)
- [Registry](#registry)

---

## Builders

All builders inherit from `AbstractBuilder` and transform Agent IR models into tool-specific output formats.

### Overview

The builder system provides a unified interface for generating configurations for different AI tools:

| Builder | Output Format | Target Tool | File Extension |
|---------|---------------|-------------|-----------------|
| KiloBuilder | YAML + Markdown | Kilo IDE | `.md` |
| ClineBuilder | Markdown | Cline AI | `.clinerules` |
| ClaudeBuilder | JSON Dict | Claude API | `.json` |
| CopilotBuilder | YAML + Markdown | GitHub Copilot | `.md` |
| CursorBuilder | Markdown | Cursor AI | `.cursorrules` |

### KiloBuilder

Generates `.kilo/agents/{name}.md` files with YAML frontmatter and markdown sections.

#### Signature

```python
class KiloBuilder(AbstractBuilder):
    def __init__(self, agents_dir: Path | str = "agents") -> None
    def build(self, agent: Agent, options: BuildOptions) -> str
    def validate(self, agent: Agent) -> list[str]
    def get_output_format(self) -> str
    def get_tool_name(self) -> str
    def build_subagents(self, agent: Agent, options: BuildOptions) -> dict[str, str]
```

#### Class Description

Builder for Kilo IDE agent configurations. Generates YAML frontmatter with metadata and markdown sections for system prompts, tools, skills, workflows, and subagents.

#### Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `agents_dir: Path \| str = "agents"` | - | Initialize builder with optional agents directory |
| `build` | `agent: Agent`, `options: BuildOptions` | `str` | Build complete Kilo agent file with YAML + markdown |
| `validate` | `agent: Agent` | `list[str]` | Validate agent model; returns error list (empty if valid) |
| `get_output_format` | - | `str` | Returns "Kilo IDE Agent File (YAML frontmatter + Markdown)" |
| `get_tool_name` | - | `str` | Returns "kilo" |
| `build_subagents` | `agent: Agent`, `options: BuildOptions` | `dict[str, str]` | Build subagent files; returns dict mapping subagent names to content |

#### Output Format

```markdown
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

#### Raises

- `BuilderValidationError`: If agent model is invalid

#### Example

```python
from src.builders.kilo_builder import KiloBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent

builder = KiloBuilder(agents_dir="agents")
agent = Agent(
    name="code",
    description="Expert software engineer",
    system_prompt="You are an expert code engineer..."
)
options = BuildOptions(variant="minimal", include_skills=True)
output = builder.build(agent, options)
print(output)  # YAML + markdown content
```

---

### ClineBuilder

Generates `.clinerules` files with markdown formatting.

#### Signature

```python
class ClineBuilder(AbstractBuilder):
    def __init__(self, agents_dir: Path | str = "agents") -> None
    def build(self, agent: Agent, options: BuildOptions) -> str
    def validate(self, agent: Agent) -> list[str]
    def get_output_format(self) -> str
    def get_tool_name(self) -> str
```

#### Class Description

Builder for Cline AI configuration files. Generates `.clinerules` files (single markdown file) with system prompt rendered as prose, followed by tools, skills, workflows, and subagents sections.

#### Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `agents_dir: Path \| str = "agents"` | - | Initialize builder |
| `build` | `agent: Agent`, `options: BuildOptions` | `str` | Build Cline markdown rules file |
| `validate` | `agent: Agent` | `list[str]` | Validate agent model |
| `get_output_format` | - | `str` | Returns "Cline AI Rules File (Markdown)" |
| `get_tool_name` | - | `str` | Returns "cline" |

#### Output Format

```markdown
# {Agent Name} Rules

You are an expert [description].

## Tools

- **tool1**: [Description]
- **tool2**: [Description]

## Skills

The following skills are available. Use them by calling use_skill::

### Skill: skill-name
Invoke by: `use_skill skill_name`

## Workflows

[Workflow instructions]

## Subagents

You may delegate to these specialists:

### Subagent: subagent-name
Specializes in subagent-name tasks.
Invoke by: `use_skill subagent_name` or request 'subagent-name subagent'
```

#### Raises

- `BuilderValidationError`: If agent model is invalid

#### Example

```python
from src.builders.cline_builder import ClineBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent

builder = ClineBuilder()
agent = Agent(
    name="code",
    description="Code specialist",
    system_prompt="You excel at writing production-quality code..."
)
options = BuildOptions(variant="minimal")
output = builder.build(agent, options)
# output is markdown string suitable for .clinerules file
```

---

### ClaudeBuilder

Generates JSON output compatible with Claude's Messages API.

#### Signature

```python
class ClaudeBuilder(AbstractBuilder):
    def __init__(self, agents_dir: Path | str = "agents") -> None
    def build(self, agent: Agent, options: BuildOptions) -> dict[str, Any]
    def validate(self, agent: Agent) -> list[str]
    def get_output_format(self) -> str
    def get_tool_name(self) -> str
```

#### Class Description

Builder for Claude Messages API JSON output. Generates JSON dictionary with system prompt, tools, and instructions suitable for use with Claude's API.

#### Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `agents_dir: Path \| str = "agents"` | - | Initialize builder |
| `build` | `agent: Agent`, `options: BuildOptions` | `dict[str, Any]` | Build JSON-serializable dict for Claude API |
| `validate` | `agent: Agent` | `list[str]` | Validate agent model |
| `get_output_format` | - | `str` | Returns "Claude Messages API JSON (dict)" |
| `get_tool_name` | - | `str` | Returns "claude" |

#### Output Format

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
        }
    ],
    "instructions": "Skills:\n- skill1\n\nWorkflows:\n[workflow content]\n\nSubagents:\n- subagent1"
}
```

#### Raises

- `BuilderValidationError`: If agent model is invalid or output is not JSON serializable

#### Example

```python
from src.builders.claude_builder import ClaudeBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent
import json

builder = ClaudeBuilder()
agent = Agent(
    name="code",
    description="Code specialist",
    system_prompt="You are an expert at coding...",
    tools=["read", "write"]
)
options = BuildOptions(include_tools=True)
output = builder.build(agent, options)
json_str = json.dumps(output)  # JSON serializable
```

---

### CopilotBuilder

Generates GitHub Copilot instructions files with YAML frontmatter.

#### Signature

```python
class CopilotBuilder(AbstractBuilder):
    def __init__(self, agents_dir: Path | str = "agents") -> None
    def build(self, agent: Agent, options: BuildOptions) -> str
    def validate(self, agent: Agent) -> list[str]
    def get_output_format(self) -> str
    def get_tool_name(self) -> str
```

#### Class Description

Builder for GitHub Copilot instructions files. Generates `.github/instructions/{mode}.md` files with YAML frontmatter containing applyTo metadata and markdown sections.

#### Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `agents_dir: Path \| str = "agents"` | - | Initialize builder |
| `build` | `agent: Agent`, `options: BuildOptions` | `str` | Build Copilot instructions file |
| `validate` | `agent: Agent` | `list[str]` | Validate agent model |
| `get_output_format` | - | `str` | Returns "GitHub Copilot Instructions File (YAML frontmatter + Markdown)" |
| `get_tool_name` | - | `str` | Returns "copilot" |

#### Output Format

```markdown
---
applyTo:
  - model: "code"
  - parentAgents: []
---

# Copilot Code Agent Instructions

You are an expert code specialist.

## Tools

- read
- write

## Skills

[Skills content]

## Workflows

[Workflows content]

## Subagents

You may delegate to specialized agents:

### Subagent: test
Specializes in test tasks.
```

#### Raises

- `BuilderValidationError`: If agent model is invalid

#### Example

```python
from src.builders.copilot_builder import CopilotBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent

builder = CopilotBuilder()
agent = Agent(
    name="code",
    description="Code specialist",
    system_prompt="You specialize in writing code...",
    tools=["read", "write"]
)
options = BuildOptions(include_tools=True, include_workflows=True)
output = builder.build(agent, options)
```

---

### CursorBuilder

Generates Cursor AI rules files with markdown formatting.

#### Signature

```python
class CursorBuilder(AbstractBuilder):
    def __init__(self, agents_dir: Path | str = "agents") -> None
    def build(self, agent: Agent, options: BuildOptions) -> str
    def validate(self, agent: Agent) -> list[str]
    def get_output_format(self) -> str
    def get_tool_name(self) -> str
```

#### Class Description

Builder for Cursor AI configuration files. Generates `.cursorrules` files (single markdown file) with system prompt, constraints, tools, workflows, and subagents sections.

#### Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `agents_dir: Path \| str = "agents"` | - | Initialize builder |
| `build` | `agent: Agent`, `options: BuildOptions` | `str` | Build Cursor rules file |
| `validate` | `agent: Agent` | `list[str]` | Validate agent model |
| `get_output_format` | - | `str` | Returns "Cursor AI Rules File (Markdown)" |
| `get_tool_name` | - | `str` | Returns "cursor" |

#### Output Format

```markdown
# {Agent Name} Rules

You are an expert [description].

Your responsibilities:
- [responsibility 1]
- [responsibility 2]

## Core Constraints

- Type hints required on all public functions
- No `any` types without explicit justification
- Read code BEFORE writing code
- Match existing patterns exactly

## Available Tools

### read
Purpose: [Description]
Usage: Call with appropriate parameters

### bash
Purpose: [Description]
Usage: Call with appropriate parameters

## Workflows

[Workflow instructions]

## Subagents Available

- **test**: Specializes in test tasks
- **architect**: Specializes in architect tasks
```

#### Raises

- `BuilderValidationError`: If agent model is invalid

#### Example

```python
from src.builders.cursor_builder import CursorBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent

builder = CursorBuilder()
agent = Agent(
    name="code",
    description="Expert code developer",
    system_prompt="You are an expert at writing code...",
    tools=["read", "bash"]
)
options = BuildOptions(include_tools=True, include_rules=True)
output = builder.build(agent, options)
```

---

## Core Infrastructure

### BuildOptions

Configuration class for builder options.

#### Signature

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

#### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `variant` | `str` | `"minimal"` | Build variant: "minimal" (lightweight) or "verbose" (detailed) |
| `agent_name` | `str` | `""` | Name of agent being built (for context in error messages) |
| `include_subagents` | `bool` | `True` | Whether to include subagents in output |
| `include_skills` | `bool` | `True` | Whether to include skills in output |
| `include_workflows` | `bool` | `True` | Whether to include workflows in output |
| `include_rules` | `bool` | `True` | Whether to include rules in output |
| `include_tools` | `bool` | `True` | Whether to include tools in output |

#### Raises

- `ValueError`: If variant is not "minimal" or "verbose"

#### Example

```python
from src.builders.base import BuildOptions

options = BuildOptions(
    variant="minimal",
    include_tools=True,
    include_skills=False,
    include_workflows=True
)

# Variant validation happens in __post_init__
invalid = BuildOptions(variant="full")  # Raises ValueError
```

---

### AbstractBuilder

Abstract base class for all tool-specific builders.

#### Signature

```python
class AbstractBuilder(ABC):
    @abstractmethod
    def build(self, agent: Agent, options: BuildOptions) -> str | dict[str, Any]
    
    @abstractmethod
    def validate(self, agent: Agent) -> list[str]
    
    def supports_feature(self, feature_name: str) -> bool
    
    def get_output_format(self) -> str
    
    def get_tool_name(self) -> str
```

#### Abstract Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `build` | `agent: Agent`, `options: BuildOptions` | `str \| dict[str, Any]` | **Must override.** Transform Agent IR to tool-specific output |
| `validate` | `agent: Agent` | `list[str]` | **Must override.** Validate agent; return error messages (empty if valid) |

#### Concrete Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `supports_feature` | `feature_name: str` | `bool` | Check if feature is supported. Supported: "skills", "workflows", "rules", "subagents", "tools" |
| `get_output_format` | - | `str` | Human-readable output format description (override in subclasses) |
| `get_tool_name` | - | `str` | Tool name (derived from class name; override if needed) |

#### Example

```python
from src.builders.base import AbstractBuilder, BuildOptions
from src.ir.models import Agent

class CustomBuilder(AbstractBuilder):
    def build(self, agent: Agent, options: BuildOptions) -> str:
        # Implementation
        return f"Custom: {agent.name}"
    
    def validate(self, agent: Agent) -> list[str]:
        errors = []
        if not agent.name:
            errors.append("Agent name is required")
        return errors

builder = CustomBuilder()
if builder.supports_feature("skills"):
    print("Skills supported")
```

---

### BuilderFactory

Factory for creating and managing builder instances.

#### Signature

```python
class BuilderFactory:
    @classmethod
    def register(cls, tool_name: str, builder_class: type[AbstractBuilder]) -> None
    
    @classmethod
    def get_builder(cls, tool_name: str) -> AbstractBuilder
    
    @classmethod
    def list_builders(cls) -> list[str]
    
    @classmethod
    def has_builder(cls, tool_name: str) -> bool
    
    @classmethod
    def clear(cls) -> None
    
    @classmethod
    def get_builder_info(cls, tool_name: str) -> dict[str, Any]
```

#### Class Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register` | `tool_name: str`, `builder_class: type[AbstractBuilder]` | `None` | Register a builder class for a tool |
| `get_builder` | `tool_name: str` | `AbstractBuilder` | Get builder instance for tool (creates new instance) |
| `list_builders` | - | `list[str]` | List all registered tool names (sorted) |
| `has_builder` | `tool_name: str` | `bool` | Check if builder registered for tool |
| `clear` | - | `None` | Clear all registered builders (for testing) |
| `get_builder_info` | `tool_name: str` | `dict[str, Any]` | Get metadata: tool_name, class_name, output_format |

#### Raises

- `BuilderNotFoundError`: If builder not registered for tool
- `TypeError`: If builder_class is not subclass of AbstractBuilder
- `ValueError`: If tool_name is empty

#### Example

```python
from src.builders.factory import BuilderFactory
from src.builders.kilo_builder import KiloBuilder

# Register
BuilderFactory.register("kilo", KiloBuilder)

# Get builder instance
builder = BuilderFactory.get_builder("kilo")

# List available
tools = BuilderFactory.list_builders()  # ["kilo", "claude", "cline", ...]

# Check if available
if BuilderFactory.has_builder("claude"):
    builder = BuilderFactory.get_builder("claude")

# Get info
info = BuilderFactory.get_builder_info("kilo")
# {"tool_name": "kilo", "class_name": "KiloBuilder", "output_format": "..."}
```

---

### ComponentSelector

Selects and loads component variants (minimal/verbose) for agents.

#### Signature

```python
class Variant(str, Enum):
    MINIMAL = "minimal"
    VERBOSE = "verbose"

class ComponentBundle(NamedTuple):
    variant: Variant
    prompt: str
    skills: Optional[str] = None
    workflow: Optional[str] = None
    fallback_used: bool = False

class ComponentSelector:
    def __init__(self, agents_dir: Path | str = "agents") -> None
    def select(self, agent: Agent, variant: Variant = Variant.MINIMAL) -> ComponentBundle
    def get_variant_path(self, agent_name: str, variant: Variant) -> Path
    def variant_exists(self, agent_name: str, variant: Variant) -> bool
    def list_available_variants(self, agent_name: str) -> List[Variant]
```

#### Variant Enum

| Value | Description |
|-------|-------------|
| `MINIMAL` | Lightweight, essential content only |
| `VERBOSE` | Detailed, comprehensive content |

#### ComponentBundle

| Attribute | Type | Description |
|-----------|------|-------------|
| `variant` | `Variant` | Selected variant (MINIMAL or VERBOSE) |
| `prompt` | `str` | System prompt content (required) |
| `skills` | `Optional[str]` | Skills content if available |
| `workflow` | `Optional[str]` | Workflow content if available |
| `fallback_used` | `bool` | True if verbose used as fallback for missing minimal |

#### Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `agents_dir: Path \| str = "agents"` | - | Initialize selector |
| `select` | `agent: Agent`, `variant: Variant = MINIMAL` | `ComponentBundle` | Select and load components; falls back to verbose if minimal unavailable |
| `get_variant_path` | `agent_name: str`, `variant: Variant` | `Path` | Get path to variant directory |
| `variant_exists` | `agent_name: str`, `variant: Variant` | `bool` | Check if variant exists with prompt.md |
| `list_available_variants` | `agent_name: str` | `List[Variant]` | List available variants for agent |

#### Raises

- `ComponentNotFoundError`: If required prompt.md is missing
- `VariantNotFoundError`: If both minimal and verbose unavailable

#### Example

```python
from src.builders.component_selector import ComponentSelector, Variant
from src.ir.models import Agent

selector = ComponentSelector(agents_dir="agents")
agent = Agent(
    name="code",
    description="Code specialist",
    system_prompt="You code well..."
)

# Select minimal variant (or falls back to verbose)
bundle = selector.select(agent, variant=Variant.MINIMAL)
print(bundle.prompt)  # System prompt content
print(bundle.variant)  # Variant.MINIMAL or Variant.VERBOSE

# Check what's available
available = selector.list_available_variants("code")
# [Variant.MINIMAL, Variant.VERBOSE]
```

---

### ComponentComposer

Composes loaded components into formatted output.

#### Signature

```python
class ComponentComposer:
    @staticmethod
    def compose_markdown(
        bundle: ComponentBundle,
        agent: Agent,
        include_sections: Optional[List[str]] = None,
    ) -> str
    
    @staticmethod
    def compose_yaml_markdown(
        bundle: ComponentBundle,
        agent: Agent,
        frontmatter: Optional[Dict[str, Any]] = None,
    ) -> str
    
    @staticmethod
    def compose_json(
        bundle: ComponentBundle,
        agent: Agent,
    ) -> Dict[str, Any]
```

#### Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `compose_markdown` | `bundle: ComponentBundle`, `agent: Agent`, `include_sections: Optional[List[str]] = None` | `str` | Compose into markdown format |
| `compose_yaml_markdown` | `bundle: ComponentBundle`, `agent: Agent`, `frontmatter: Optional[Dict[str, Any]] = None` | `str` | Compose into YAML frontmatter + markdown |
| `compose_json` | `bundle: ComponentBundle`, `agent: Agent` | `Dict[str, Any]` | Compose into JSON-serializable dict |

#### Parameters

`include_sections` valid values: "prompt", "tools", "skills", "workflows", "subagents"

#### Example

```python
from src.builders.component_composer import ComponentComposer
from src.builders.component_selector import ComponentSelector, Variant
from src.ir.models import Agent

selector = ComponentSelector()
agent = Agent(
    name="code",
    description="Code specialist",
    system_prompt="You are a code expert...",
    tools=["read", "write"],
    skills=["analyze", "refactor"]
)

bundle = selector.select(agent, variant=Variant.MINIMAL)

# Markdown only
markdown = ComponentComposer.compose_markdown(
    bundle, 
    agent,
    include_sections=["prompt", "tools", "skills"]
)

# YAML + Markdown
yaml_md = ComponentComposer.compose_yaml_markdown(
    bundle,
    agent,
    frontmatter={"name": agent.name, "model": "claude-3"}
)

# JSON
json_out = ComponentComposer.compose_json(bundle, agent)
```

---

## IR Models

Intermediate Representation (IR) models define the data structures for agents, skills, workflows, tools, rules, and projects.

### Agent

Represents a tool-agnostic agent configuration.

#### Signature

```python
class Agent(BaseModel):
    name: str = Field(..., min_length=1, description="Unique identifier")
    description: str = Field(..., min_length=1, description="One-sentence description")
    system_prompt: str = Field(..., min_length=1, description="System prompt defining behavior")
    tools: List[str] = Field(default_factory=list, description="List of tool names")
    skills: List[str] = Field(default_factory=list, description="List of skill names")
    workflows: List[str] = Field(default_factory=list, description="List of workflow names")
    subagents: List[str] = Field(default_factory=list, description="List of subagent names")
```

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | `str` | Yes | Unique identifier (e.g., 'code', 'architect') |
| `description` | `str` | Yes | One-sentence description of purpose |
| `system_prompt` | `str` | Yes | System prompt defining agent behavior |
| `tools` | `List[str]` | No | Tool names agent can use |
| `skills` | `List[str]` | No | Skill names agent can perform |
| `workflows` | `List[str]` | No | Workflow names agent can execute |
| `subagents` | `List[str]` | No | Subagent names for hierarchical composition |

#### Notes

- Frozen model (immutable after creation)
- All fields validated by Pydantic
- Required fields have min_length=1

#### Example

```python
from src.ir.models import Agent

agent = Agent(
    name="code",
    description="Expert software engineer",
    system_prompt="You are an expert at writing production-quality code...",
    tools=["read", "bash", "write"],
    skills=["refactoring", "testing"],
    workflows=["code_review"],
    subagents=["test", "refactor"]
)

print(agent.name)  # "code"
print(len(agent.tools))  # 3

# agent.name = "code2"  # Error: frozen model
```

---

### Skill

Represents a reusable capability for agents.

#### Signature

```python
class Skill(BaseModel):
    name: str = Field(..., min_length=1, description="Unique identifier")
    description: str = Field(..., min_length=1, description="One-sentence description")
    instructions: str = Field(..., min_length=1, description="Detailed instructions")
    tools_needed: List[str] = Field(default_factory=list, description="Required tool names")
```

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | `str` | Yes | Unique identifier (e.g., 'code_analysis') |
| `description` | `str` | Yes | One-sentence description |
| `instructions` | `str` | Yes | Detailed instructions for execution |
| `tools_needed` | `List[str]` | No | Tools required by this skill |

#### Example

```python
from src.ir.models import Skill

skill = Skill(
    name="code_analysis",
    description="Analyze code structure and quality",
    instructions="Read the code, identify patterns, suggest improvements...",
    tools_needed=["read", "bash"]
)

print(skill.name)  # "code_analysis"
print(skill.tools_needed)  # ["read", "bash"]
```

---

### Workflow

Represents a sequence of steps an agent can execute.

#### Signature

```python
class Workflow(BaseModel):
    name: str = Field(..., min_length=1, description="Unique identifier")
    description: str = Field(..., min_length=1, description="One-sentence description")
    steps: List[str] = Field(..., description="Step descriptions (non-empty)")
```

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | `str` | Yes | Unique identifier |
| `description` | `str` | Yes | One-sentence description |
| `steps` | `List[str]` | Yes | Step descriptions (must have ≥1 step) |

#### Validation

- `steps` must be non-empty list
- Each step must be a string
- Raises `ValueError` if steps validation fails

#### Example

```python
from src.ir.models import Workflow

workflow = Workflow(
    name="code_review",
    description="Review code for quality and best practices",
    steps=[
        "Read the code file",
        "Analyze for issues",
        "Suggest improvements",
        "Document findings"
    ]
)

print(len(workflow.steps))  # 4

# Empty steps raises error
invalid = Workflow(
    name="bad",
    description="Bad workflow",
    steps=[]
)  # ValueError: Workflow must have at least one step
```

---

### Tool

Represents a tool agents can invoke.

#### Signature

```python
class Tool(BaseModel):
    name: str = Field(..., min_length=1, description="Unique identifier")
    description: str = Field(..., min_length=1, description="One-sentence description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="JSON schema")
```

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | `str` | Yes | Unique identifier (e.g., 'read', 'bash') |
| `description` | `str` | Yes | One-sentence description |
| `parameters` | `Dict[str, Any]` | No | JSON schema describing parameters |

#### Example

```python
from src.ir.models import Tool

tool = Tool(
    name="read",
    description="Read files and directories",
    parameters={
        "type": "object",
        "properties": {
            "filePath": {"type": "string", "description": "Path to read"}
        },
        "required": ["filePath"]
    }
)

print(tool.name)  # "read"
```

---

### Rules

Represents constraints and guidelines for behavior.

#### Signature

```python
class Rules(BaseModel):
    constraints: List[str] = Field(
        default_factory=list,
        description="List of constraints to enforce"
    )
    guidelines: Dict[str, Any] = Field(
        default_factory=dict,
        description="Guidelines organized by category"
    )
```

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `constraints` | `List[str]` | No | Constraints to enforce |
| `guidelines` | `Dict[str, Any]` | No | Guidelines by category |

#### Example

```python
from src.ir.models import Rules

rules = Rules(
    constraints=[
        "Type hints required on all public functions",
        "No `any` types without justification"
    ],
    guidelines={
        "code_style": "Follow PEP 8",
        "testing": "Minimum 80% coverage"
    }
)

print(len(rules.constraints))  # 2
print(rules.guidelines["code_style"])  # "Follow PEP 8"
```

---

### Project

Represents project configuration.

#### Signature

```python
class Project(BaseModel):
    registry_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Registry configuration"
    )
    verbosity: Literal["minimal", "verbose"] = Field(
        default="minimal",
        description="Logging verbosity"
    )
    builder_configs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Builder-specific configurations"
    )
```

#### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `registry_settings` | `Dict[str, Any]` | `{}` | Registry configuration |
| `verbosity` | `Literal["minimal", "verbose"]` | `"minimal"` | Logging verbosity |
| `builder_configs` | `Dict[str, Any]` | `{}` | Builder-specific configs |

#### Example

```python
from src.ir.models import Project

project = Project(
    registry_settings={"cache_enabled": True},
    verbosity="verbose",
    builder_configs={
        "kilo": {"output_dir": ".kilo"},
        "claude": {"use_json": True}
    }
)

print(project.verbosity)  # "verbose"
```

---

## Loaders

Loaders parse files and create IR models.

### ComponentLoader

Loads complete component bundles from directories.

#### Signature

```python
class ComponentBundle(NamedTuple):
    prompt_content: Dict[str, Any]
    skills_content: Optional[Dict[str, Any]] = None
    workflow_content: Optional[Dict[str, Any]] = None

class ComponentLoader:
    def __init__(self) -> None
    def load(self, directory: str) -> ComponentBundle
    def load_as_dict(self, directory: str) -> Dict[str, Any]
```

#### Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | - | - | Initialize loader with YAML and Markdown parsers |
| `load` | `directory: str` | `ComponentBundle` | Load prompt.md (required), skills.md, workflow.md (optional) |
| `load_as_dict` | `directory: str` | `Dict[str, Any]` | Load as flat dict with keys: 'prompt', 'skills', 'workflow' |

#### File Structure

```
directory/
├── prompt.md          (required)
├── skills.md          (optional)
└── workflow.md        (optional)
```

#### Raises

- `MissingFileError`: If prompt.md not found
- `ParseError`: If parsing fails

#### Example

```python
from src.ir.loaders.component_loader import ComponentLoader

loader = ComponentLoader()

# Load as bundle
bundle = loader.load("src/prompts/code-agent/")
print(bundle.prompt_content)
print(bundle.skills_content)
print(bundle.workflow_content)

# Load as dict
components = loader.load_as_dict("src/prompts/code-agent/")
print(components["prompt"])
print(components.get("skills"))
```

---

### SkillLoader

Loads Skill IR models from markdown files.

#### Signature

```python
class SkillLoader:
    def __init__(self) -> None
    def load(self, file_path: str) -> Skill
```

#### File Format

```markdown
---
name: skill-name
description: One-line description
tools_needed: [tool1, tool2]
---

## Instructions

Detailed instructions here.
```

#### Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | - | - | Initialize with YAML and Markdown parsers |
| `load` | `file_path: str` | `Skill` | Parse markdown file and return Skill IR model |

#### Raises

- `MissingFileError`: If file not found
- `ParseError`: If file cannot be parsed
- `ValidationError`: If validation fails

#### Example

```python
from src.ir.loaders.skill_loader import SkillLoader

loader = SkillLoader()
skill = loader.load("src/skills/code_analysis.md")

print(skill.name)
print(skill.description)
print(skill.instructions)
print(skill.tools_needed)
```

---

### WorkflowLoader

Loads Workflow IR models from markdown files.

#### Signature

```python
class WorkflowLoader:
    def __init__(self) -> None
    def load(self, file_path: str) -> Workflow
```

#### File Format

```markdown
---
name: workflow-name
description: One-line description
steps:
  - Step 1
  - Step 2
  - Step 3
---

## Steps

Detailed step information.
```

#### Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | - | - | Initialize with YAML and Markdown parsers |
| `load` | `file_path: str` | `Workflow` | Parse markdown file and return Workflow IR model |

#### Raises

- `MissingFileError`: If file not found
- `ParseError`: If file cannot be parsed
- `ValidationError`: If validation fails (e.g., empty steps)

#### Example

```python
from src.ir.loaders.workflow_loader import WorkflowLoader

loader = WorkflowLoader()
workflow = loader.load("src/workflows/code_review.md")

print(workflow.name)
print(workflow.description)
print(len(workflow.steps))
for step in workflow.steps:
    print(f"  - {step}")
```

---

## Registry

Registry manages discovered agents and provides lookup functionality.

### Registry

Holds and retrieves agents with optional caching.

#### Signature

```python
class Registry:
    def __init__(self, agents: Dict[str, Agent], cache: bool = True) -> None
    
    @classmethod
    def from_discovery(cls, agents_dir: Path | str, cache: bool = True) -> "Registry"
    
    def get_agent(self, name: str, variant: str = "minimal") -> Agent
    def get_all_agents(self) -> Dict[str, Agent]
    def list_agents(self, include_subagents: bool = False) -> list[str]
    def list_subagents(self, agent_name: str) -> list[str]
    def has_agent(self, name: str) -> bool
    def has_subagent(self, agent_name: str, subagent_name: str) -> bool
```

#### Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `agents: Dict[str, Agent]`, `cache: bool = True` | - | Initialize with agents dict |
| `from_discovery` | `agents_dir: Path \| str`, `cache: bool = True` | `Registry` | Create registry from filesystem discovery |
| `get_agent` | `name: str`, `variant: str = "minimal"` | `Agent` | Get agent by name (subagents: "agent/subagent") |
| `get_all_agents` | - | `Dict[str, Agent]` | Get all agents (top-level + subagents) |
| `list_agents` | `include_subagents: bool = False` | `list[str]` | List agent names (sorted) |
| `list_subagents` | `agent_name: str` | `list[str]` | List subagents for agent (sorted) |
| `has_agent` | `name: str` | `bool` | Check if agent exists |
| `has_subagent` | `agent_name: str`, `subagent_name: str` | `bool` | Check if subagent exists |

#### Raises

- `AgentNotFoundError`: If agent not found
- `InvalidVariantError`: If variant unavailable

#### Example

```python
from src.registry.registry import Registry

# Create from filesystem discovery
registry = Registry.from_discovery("./agents")

# Get agent
agent = registry.get_agent("code", variant="minimal")
print(agent.name)  # "code"
print(agent.description)

# Get subagent
subagent = registry.get_agent("code/test")

# List all agents
agents = registry.list_agents()  # ["architect", "code", ...]

# Check existence
if registry.has_agent("code"):
    print("Code agent exists")

# List subagents
subs = registry.list_subagents("code")
for sub in subs:
    print(f"  - code/{sub}")

# Get all
all_agents = registry.get_all_agents()
```

---

## Type Index

Quick reference of all types and their modules:

### Builders
- `AbstractBuilder` - src.builders.base
- `BuildOptions` - src.builders.base
- `KiloBuilder` - src.builders.kilo_builder
- `ClineBuilder` - src.builders.cline_builder
- `ClaudeBuilder` - src.builders.claude_builder
- `CopilotBuilder` - src.builders.copilot_builder
- `CursorBuilder` - src.builders.cursor_builder
- `BuilderFactory` - src.builders.factory

### Components
- `ComponentSelector` - src.builders.component_selector
- `Variant` - src.builders.component_selector
- `ComponentBundle` (selector) - src.builders.component_selector
- `ComponentComposer` - src.builders.component_composer

### IR Models
- `Agent` - src.ir.models
- `Skill` - src.ir.models
- `Workflow` - src.ir.models
- `Tool` - src.ir.models
- `Rules` - src.ir.models
- `Project` - src.ir.models

### Loaders
- `ComponentLoader` - src.ir.loaders
- `ComponentBundle` (loader) - src.ir.loaders
- `SkillLoader` - src.ir.loaders
- `WorkflowLoader` - src.ir.loaders

### Registry
- `Registry` - src.registry.registry

---

## Common Patterns

### Building an Agent for a Specific Tool

```python
from src.builders.factory import BuilderFactory
from src.builders.base import BuildOptions
from src.ir.models import Agent

# Create agent
agent = Agent(
    name="code",
    description="Expert software engineer",
    system_prompt="You write production-quality code...",
    tools=["read", "write", "bash"],
    skills=["refactoring", "testing"]
)

# Build for Kilo
kilo_builder = BuilderFactory.get_builder("kilo")
kilo_output = kilo_builder.build(agent, BuildOptions(variant="minimal"))

# Build for Claude
claude_builder = BuilderFactory.get_builder("claude")
claude_output = claude_builder.build(agent, BuildOptions())

# Build for Cline
cline_builder = BuilderFactory.get_builder("cline")
cline_output = cline_builder.build(agent, BuildOptions())
```

### Loading Components and Building Output

```python
from src.builders.component_selector import ComponentSelector, Variant
from src.builders.component_composer import ComponentComposer
from src.ir.models import Agent

selector = ComponentSelector(agents_dir="agents")
agent = Agent(
    name="code",
    description="Code specialist",
    system_prompt="You specialize in code..."
)

# Select components
bundle = selector.select(agent, variant=Variant.MINIMAL)

# Compose output
markdown = ComponentComposer.compose_markdown(bundle, agent)
yaml_md = ComponentComposer.compose_yaml_markdown(bundle, agent)
json_out = ComponentComposer.compose_json(bundle, agent)
```

### Discovering and Retrieving Agents

```python
from src.registry.registry import Registry

# Discover agents from filesystem
registry = Registry.from_discovery("./agents")

# List available agents
agents = registry.list_agents()
print(f"Available agents: {', '.join(agents)}")

# Get specific agent
code_agent = registry.get_agent("code")

# List subagents
subagents = registry.list_subagents("code")
print(f"Code subagents: {', '.join(subagents)}")

# Get subagent
test_agent = registry.get_agent("code/test")
```

---

## Error Handling

All components use typed exceptions from `src.builders.errors` and `src.ir.exceptions`:

- `BuilderValidationError` - Raised when agent validation fails
- `BuilderNotFoundError` - Raised when builder not registered
- `ComponentNotFoundError` - Raised when component file missing
- `VariantNotFoundError` - Raised when variant unavailable
- `AgentNotFoundError` - Raised when agent not in registry
- `ParseError` - Raised when file parsing fails
- `ValidationError` - Raised when model validation fails

```python
from src.builders.errors import BuilderValidationError
from src.builders.kilo_builder import KiloBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent

builder = KiloBuilder()
try:
    agent = Agent(name="", description="", system_prompt="")  # Invalid
    builder.build(agent, BuildOptions())
except BuilderValidationError as e:
    print(f"Validation failed: {e.message}")
    print(f"Errors: {e.errors}")
```

---

**Last Updated:** 2026-04-09
**Version:** 1.0.0
**Status:** Production-Ready
