# Builder Documentation Index

Comprehensive guides for building Agent IR configurations for all 5 production builders.

## Overview

Builders transform Agent IR (Intermediate Representation) models into tool-specific configurations. This directory contains detailed documentation for each builder with examples, patterns, and best practices.

## The 5 Production Builders

### 1. 🔷 [KiloBuilder](./KILO_BUILDER_GUIDE.md)
**For:** Kilo IDE agent configurations  
**Output Format:** YAML frontmatter + Markdown (`.md`)  
**Target:** `.kilo/agents/{agent_name}.md`  
**Use When:** Building agents for Kilo IDE development environment

**Key Features:**
- YAML frontmatter with metadata
- Markdown sections for content
- Support for subagents in nested directories
- Variant support (minimal/verbose)
- Component selection and bundling

**Quick Example:**
```python
from promptosaurus.builders.kilo_builder import KiloBuilder
from promptosaurus.ir.models import Agent

builder = KiloBuilder()
agent = Agent(name="code", description="Code expert", system_prompt="...")
output = builder.build(agent, BuildOptions(variant="verbose"))
```

[📖 Full KiloBuilder Guide](./KILO_BUILDER_GUIDE.md)

---

### 2. 🚀 [ClineBuilder](./CLINE_BUILDER_GUIDE.md)
**For:** Cline AI configuration files  
**Output Format:** Pure Markdown (no YAML)  
**Target:** `.clinerules` file  
**Use When:** Configuring Cline AI assistant behavior

**Key Features:**
- Prose-based instructions
- `use_skill` invocation pattern
- Subagent delegation support
- Natural language focused
- Pure markdown (easy to read)

**Quick Example:**
```python
from promptosaurus.builders.cline_builder import ClineBuilder

builder = ClineBuilder()
agent = Agent(name="code", description="...", system_prompt="...")
rules = builder.build(agent, BuildOptions(variant="verbose"))
# Save to .clinerules
```

[📖 Full ClineBuilder Guide](./CLINE_BUILDER_GUIDE.md)

---

### 3. 🤖 [ClaudeBuilder](./CLAUDE_BUILDER_GUIDE.md)
**For:** Claude agent configuration files  
**Output Format:** Markdown files (dict[str, str])  
**Target:** `.claude/` directory with Markdown files  
**Use When:** Building Claude agent configuration files

**Key Features:**
- File path → Markdown content mapping
- `.claude/` directory structure
- Agents, subagents, and workflows support
- Programmatic integration
- Skills and workflows support

**Quick Example:**
```python
from promptosaurus.builders.claude_builder import ClaudeBuilder
from pathlib import Path

builder = ClaudeBuilder()
agent = Agent(name="code", description="...", system_prompt="...")
config = builder.build(agent, BuildOptions(variant="verbose"))
for file_path, content in config.items():
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    Path(file_path).write_text(content)
```

[📖 Full ClaudeBuilder Guide](./CLAUDE_BUILDER_GUIDE.md)

---

### 4. 🐙 [CopilotBuilder](./COPILOT_BUILDER_GUIDE.md)
**For:** GitHub Copilot instructions  
**Output Format:** YAML frontmatter + Markdown  
**Target:** `.github/instructions/{mode}.md`  
**Use When:** Configuring GitHub Copilot behavior

**Key Features:**
- YAML applyTo metadata
- Multi-mode support (code, refactor, etc.)
- Markdown instructions
- Skill delegation
- Model-specific configuration

**Quick Example:**
```python
from promptosaurus.builders.copilot_builder import CopilotBuilder

builder = CopilotBuilder(agents_dir=".github/instructions")
agent = Agent(name="code", description="...", system_prompt="...")
instructions = builder.build(agent, BuildOptions(variant="verbose"))
```

[📖 Full CopilotBuilder Guide](./COPILOT_BUILDER_GUIDE.md)

---

### 5. ➡️ [CursorBuilder](./CURSOR_BUILDER_GUIDE.md)
**For:** Cursor IDE rules files  
**Output Format:** Pure Markdown  
**Target:** `.cursorrules` file  
**Use When:** Configuring Cursor IDE behavior

**Key Features:**
- Markdown rules format
- Core constraints section
- Tool documentation
- Workflow definitions
- Subagent descriptions
- Cursor IDE optimized

**Quick Example:**
```python
from promptosaurus.builders.cursor_builder import CursorBuilder

builder = CursorBuilder()
agent = Agent(name="dev", description="...", system_prompt="...")
rules = builder.build(agent, BuildOptions(variant="verbose"))
# Save to .cursorrules
```

[📖 Full CursorBuilder Guide](./CURSOR_BUILDER_GUIDE.md)

---

## Quick Comparison

| Feature | Kilo | Cline | Claude | Copilot | Cursor |
|---------|------|-------|--------|---------|--------|
| **Output Format** | YAML + MD | Markdown | Markdown files (dict[str, str]) | YAML + MD | Markdown |
| **Has Frontmatter** | ✅ Yes | ❌ No | N/A | ✅ Yes | ❌ No |
| **JSON Serializable** | ❌ No | ❌ No | ❌ No | ❌ No | ❌ No |
| **Subagents** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Skills** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Workflows** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Constraints** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Prose Format** | ❌ Structured | ✅ Prose | ❌ Prose | ✅ Prose | ✅ Prose |
| **API Compatible** | 🔧 Kilo | 🔧 Cline | 🚀 Claude | 🐙 GitHub | ➡️ Cursor |

---

## Builder Selection Guide

### Use KiloBuilder if:
- You're developing with Kilo IDE
- You need YAML frontmatter configuration
- You want subagents in nested directories
- You need fine-grained component control

### Use ClineBuilder if:
- You're using Cline AI assistant
- You prefer prose-based instructions
- You need `use_skill` invocation syntax
- You want simple markdown format

### Use ClaudeBuilder if:
- You're integrating with Claude API
- You need JSON configuration
- You're building programmatic agents
- You want tool schemas

### Use CopilotBuilder if:
- You're configuring GitHub Copilot
- You need multi-mode support (code, refactor, etc.)
- You want applyTo metadata
- You're in GitHub ecosystem

### Use CursorBuilder if:
- You're using Cursor IDE
- You need `.cursorrules` file
- You want constraint definitions
- You prefer pure markdown

---

## Common Patterns

### Pattern 1: Building Multiple Agents

```python
agents = [
    Agent(name="code", description="Code expert", ...),
    Agent(name="test", description="Test expert", ...),
    Agent(name="review", description="Reviewer", ...),
]

for agent in agents:
    config = builder.build(agent, BuildOptions(variant="verbose"))
    # Save config
```

### Pattern 2: Conditional Components

```python
# Build with only tools and prompts
options = BuildOptions(
    include_tools=True,
    include_skills=False,
    include_workflows=False,
)

output = builder.build(agent, options)
```

### Pattern 3: Validation Before Building

```python
errors = builder.validate(agent)
if errors:
    print("Validation failed:")
    for error in errors:
        print(f"  - {error}")
else:
    config = builder.build(agent, options)
```

### Pattern 4: Dynamic Configuration

```python
def build_from_dict(config: dict) -> str:
    agent = Agent(
        name=config["name"],
        description=config["description"],
        system_prompt=config["system_prompt"],
        tools=config.get("tools", []),
        skills=config.get("skills", []),
    )
    
    options = BuildOptions(
        variant=config.get("variant", "minimal"),
        include_tools=config.get("include_tools", True),
    )
    
    return builder.build(agent, options)
```

---

## BuildOptions Reference

All builders support BuildOptions with these fields:

```python
@dataclass
class BuildOptions:
    variant: str = "minimal"          # minimal or verbose
    agent_name: str = ""              # Name of the agent
    include_subagents: bool = True    # Include subagents
    include_skills: bool = True       # Include skills
    include_workflows: bool = True    # Include workflows
    include_rules: bool = True        # Include rules/constraints
    include_tools: bool = True        # Include tools
```

### Variant Behavior

**minimal:**
- Lightweight output
- Shorter content
- Fewer sections
- Faster processing

**verbose:**
- Full detail
- Complete content
- All available sections
- Comprehensive configuration

---

## Common Tasks

### Task: Create a New Builder

1. Read [KiloBuilder Guide](./KILO_BUILDER_GUIDE.md) for complete structure
2. Extend `Builder` from `promptosaurus/builders/base.py`
3. Implement `build()` and `validate()` methods
4. Register in builder factory
5. Create documentation following guide format

### Task: Build Configurations for Multiple Tools

```python
# Build same agent for all tools
agent = Agent(name="code", ...)

builders = {
    "kilo": KiloBuilder(),
    "claude": ClaudeBuilder(),
    "cline": ClineBuilder(),
    "copilot": CopilotBuilder(),
    "cursor": CursorBuilder(),
}

for tool_name, builder in builders.items():
    config = builder.build(agent, BuildOptions(variant="verbose"))
    # Process config (save/use)
```

### Task: Validate Agents Before Building

```python
builder = KiloBuilder()

errors = builder.validate(agent)
if errors:
    raise ValueError(f"Agent validation failed: {errors}")

output = builder.build(agent, options)
```

---

## Architecture

### Class Hierarchy

```
Builder (base.py)
├── KiloBuilder
├── ClineBuilder
├── ClaudeBuilder
├── CopilotBuilder
└── CursorBuilder
```

### Data Flow

```
Agent IR Model
    ↓
builder.validate(agent)  → Check requirements
    ↓
builder.build(agent, options)  → Generate output
    ↓
Tool-Specific Format
(YAML+MD, JSON, Markdown, etc.)
    ↓
Save to File / Use with API
```

---

## API Reference

### Builder Interface

```python
class Builder:
    def build(self, agent: Agent, options: BuildOptions) -> str | dict:
        """Build tool-specific output."""
        
    def validate(self, agent: Agent) -> list[str]:
        """Validate agent model."""
        
    def get_output_format(self) -> str:
        """Get format description."""
        
    def get_tool_name(self) -> str:
        """Get tool name."""
        
    def supports_feature(self, feature_name: str) -> bool:
        """Check feature support."""
```

### Agent IR Model

```python
@dataclass
class Agent:
    name: str
    description: str
    system_prompt: str
    tools: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    workflows: list[str] = field(default_factory=list)
    subagents: list[str] = field(default_factory=list)
```

---

## Error Handling

All builders raise `BuilderValidationError` on validation failure:

```python
from promptosaurus.builders.errors import BuilderValidationError

try:
    config = builder.build(agent, options)
except BuilderValidationError as e:
    print(f"Build failed: {e.message}")
    for error in e.errors:
        print(f"  - {error}")
```

---

## Best Practices

### ✅ DO

- ✅ Validate before building
- ✅ Use appropriate variant (minimal/verbose)
- ✅ Include meaningful system prompts
- ✅ Organize tools and skills logically
- ✅ Test with real agent data
- ✅ Handle errors explicitly
- ✅ Document custom configurations

### ❌ DON'T

- ❌ Skip validation
- ❌ Use empty required fields
- ❌ Assume builder features without checking
- ❌ Mix different tool-specific formats
- ❌ Ignore validation errors
- ❌ Build without understanding tool requirements

---

## Source Code References

- **Base Classes:** `promptosaurus/builders/base.py`
- **Kilo Implementation:** `promptosaurus/builders/kilo_builder.py`
- **Cline Implementation:** `promptosaurus/builders/cline_builder.py`
- **Claude Implementation:** `promptosaurus/builders/claude_builder.py`
- **Copilot Implementation:** `promptosaurus/builders/copilot_builder.py`
- **Cursor Implementation:** `promptosaurus/builders/cursor_builder.py`
- **Errors:** `promptosaurus/builders/errors.py`
- **Examples:** `promptosaurus/builders/examples_usage.py`
- **IR Models:** `promptosaurus/ir/models.py`

---

## Support

For detailed information on any builder:
- Read the comprehensive guide for that builder
- Check the docstrings in source code
- Review examples in `promptosaurus/builders/examples_usage.py`
- Look at test files in `tests/unit/builders/`

For issues or questions:
- Check troubleshooting section in the builder's guide
- Review common patterns section
- Validate your agent with `builder.validate(agent)`

---

## Cross-References

- **KiloBuilder:** [Full Guide](./KILO_BUILDER_GUIDE.md)
- **ClineBuilder:** [Full Guide](./CLINE_BUILDER_GUIDE.md)
- **ClaudeBuilder:** [Full Guide](./CLAUDE_BUILDER_GUIDE.md)
- **CopilotBuilder:** [Full Guide](./COPILOT_BUILDER_GUIDE.md)
- **CursorBuilder:** [Full Guide](./CURSOR_BUILDER_GUIDE.md)

---

**Last Updated:** 2026-04-09  
**Documentation Version:** 1.0  
**Builder System Version:** 1.0

