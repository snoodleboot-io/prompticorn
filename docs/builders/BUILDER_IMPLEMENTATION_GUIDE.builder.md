# Builder Implementation Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start: Create Your First Builder](#quick-start-create-your-first-builder)
3. [Understanding the Builder Interface](#understanding-the-builder-interface)
4. [Component System](#component-system)
5. [Output Format Patterns](#output-format-patterns)
6. [Real Example: ClineBuilder Walkthrough](#real-example-clinebuilder-walkthrough)
7. [Testing Your Builder](#testing-your-builder)
8. [Extending Builders with Protocol Mixins](#extending-builders-with-protocol-mixins)
9. [Best Practices](#best-practices)
10. [FAQ](#faq)

---

## Introduction

### What Are Builders?

Builders are classes that translate Agent Intermediate Representation (IR) models into tool-specific output formats. The builder pattern enables clean separation between:

- **Agent IR Model** - A normalized, tool-agnostic representation of agent configuration
- **Tool-Specific Output** - The exact format each tool expects (Markdown, JSON, YAML, etc.)

### Why the Builder Pattern?

Before builders, you might write monolithic code that handled all format conversions in one place. With builders, each tool gets its own specialized class that:

1. **Transforms** Agent IR into the tool's native format
2. **Validates** that the agent has all required information
3. **Handles** tool-specific features and quirks
4. **Composes** complex output with proper structure

### How Does It Work?

```
Agent IR Model (normalized)
         ↓
    Builder Factory
         ↓
    [Builder Instance]
         ↓
Tool-Specific Output (YAML, JSON, Markdown, etc.)
```

### Real Examples

The system includes builders for five tools:

| Tool | Output Format | Builder Class |
|------|---------------|---------------|
| **Kilo** | YAML frontmatter + Markdown | `KiloBuilder` |
| **Cline** | Pure Markdown | `ClineBuilder` |
| **Claude** | Markdown files (dict[str, str]) | `ClaudeBuilder` |
| **Copilot** | YAML frontmatter + Markdown | `CopilotBuilder` |
| **Cursor** | JSON configuration | `CursorBuilder` |

---

## Quick Start: Create Your First Builder

### Step 1: Extend Builder

Create a new file in `prompticorn/builders/`:

```python
# prompticorn/builders/my_tool_builder.py

from prompticorn.builders.base import Builder, BuildOptions
from prompticorn.ir.models import Agent

class MyToolBuilder(Builder):
    """Builder for MyTool agent configurations."""

    def build(self, agent: Agent, options: BuildOptions) -> str | dict:
        """Build MyTool-specific output from an Agent IR model."""
        # Implementation here
        pass

    def validate(self, agent: Agent) -> list[str]:
        """Validate that the agent has required fields for MyTool."""
        # Implementation here
        pass

    def get_tool_name(self) -> str:
        """Return the tool name (lowercase)."""
        return "mytool"

    def get_output_format(self) -> str:
        """Return human-readable format description."""
        return "MyTool Configuration Format"
```

### Step 2: Implement `build()`

This is the main method. It should:

1. Validate the agent
2. Load components (skills, workflows, etc.)
3. Format each section appropriately
4. Compose the output in the tool's expected format

```python
def build(self, agent: Agent, options: BuildOptions) -> str:
    """Build MyTool configuration."""
    # 1. Validate
    errors = self.validate(agent)
    if errors:
        raise BuilderValidationError(errors=errors, message=f"Invalid agent: {errors}")

    # 2. Load components (using ComponentSelector)
    from prompticorn.builders.component_selector import ComponentSelector, Variant
    selector = ComponentSelector()
    variant = Variant.MINIMAL if options.variant == "minimal" else Variant.VERBOSE
    bundle = selector.select(agent, variant=variant)

    # 3. Format sections
    sections = []
    sections.append(self._format_header(agent))
    
    if options.include_tools and agent.tools:
        sections.append(self._format_tools(agent.tools))
    
    if options.include_skills and bundle.skills:
        sections.append(self._format_skills(bundle.skills))

    # 4. Compose output
    return "\n".join(sections)
```

### Step 3: Implement `validate()`

Check that the agent has everything MyTool needs:

```python
def validate(self, agent: Agent) -> list[str]:
    """Validate agent for MyTool."""
    errors = []

    if not agent.name:
        errors.append("Agent name is required")

    if not agent.description:
        errors.append("Agent description is required")

    if not agent.system_prompt:
        errors.append("System prompt is required")

    # Add tool-specific validations here
    return errors
```

### Step 4: Register with BuilderFactory

In `prompticorn/builders/__init__.py`:

```python
from prompticorn.builders.factory import BuilderFactory
from prompticorn.builders.my_tool_builder import MyToolBuilder

# Register the builder
BuilderFactory.register('mytool', MyToolBuilder)
```

Now you can use it:

```python
from prompticorn.builders.factory import BuilderFactory

builder = BuilderFactory.get_builder('mytool')
output = builder.build(agent, BuildOptions())
```

### Step 5: Write Tests

Create `tests/unit/builders/test_my_tool_builder.py`:

```python
import pytest
from prompticorn.builders.my_tool_builder import MyToolBuilder
from prompticorn.builders.base import BuildOptions
from prompticorn.ir.models import Agent

class TestMyToolBuilder:
    """Tests for MyToolBuilder."""

    def test_init(self):
        """Test builder initialization."""
        builder = MyToolBuilder()
        assert builder is not None

    def test_get_tool_name(self):
        """Test tool name."""
        builder = MyToolBuilder()
        assert builder.get_tool_name() == "mytool"

    def test_validate_valid_agent(self):
        """Test validation passes for valid agent."""
        agent = Agent(
            name="test",
            description="Test agent",
            system_prompt="Test prompt"
        )
        builder = MyToolBuilder()
        errors = builder.validate(agent)
        assert errors == []

    def test_validate_missing_name(self):
        """Test validation fails when name is missing."""
        agent = Agent(
            name="",
            description="Test agent",
            system_prompt="Test prompt"
        )
        builder = MyToolBuilder()
        errors = builder.validate(agent)
        assert len(errors) > 0
        assert any("name" in e.lower() for e in errors)

    def test_build_returns_string(self):
        """Test build returns expected output type."""
        agent = Agent(
            name="test",
            description="Test agent",
            system_prompt="Test prompt"
        )
        builder = MyToolBuilder()
        options = BuildOptions()
        
        # This test will fail until you implement build()
        result = builder.build(agent, options)
        assert isinstance(result, str)
```

---

## Understanding the Builder Interface

### Overview

All builders inherit from `Builder`, which defines three key methods:

```python
class Builder:
    """Base class for all tool-specific builders."""

    def build(self, agent: Agent, options: BuildOptions) -> str | dict[str, Any]:
        """Build tool-specific output from Agent IR model."""

    def validate(self, agent: Agent) -> list[str]:
        """Validate that agent meets tool's requirements."""

    def get_output_format(self) -> str:
        """Human-readable description of output format."""

    def get_tool_name(self) -> str:
        """Tool name (e.g., 'kilo', 'cline', 'claude')."""

    def supports_feature(self, feature_name: str) -> bool:
        """Check if builder supports a feature (skills, workflows, etc.)."""
```

### Key Concepts

#### BuildOptions: Configuration Control

`BuildOptions` lets callers control what gets included in the output:

```python
@dataclass
class BuildOptions:
    variant: str = "minimal"              # "minimal" or "verbose"
    agent_name: str = ""                  # For error context
    include_subagents: bool = True        # Include subagents?
    include_skills: bool = True           # Include skills?
    include_workflows: bool = True        # Include workflows?
    include_rules: bool = True            # Include rules?
    include_tools: bool = True            # Include tools?
```

#### Return Types: String or Dict

- **String**: For text-based formats (YAML, Markdown, plain text)
- **Dict**: For structured formats (JSON, which is serializable)

```python
# Text-based (KiloBuilder returns string)
def build(self, agent: Agent, options: BuildOptions) -> str:
    return "---\nname: agent\n---\n# System Prompt\n..."

# Structured (ClaudeBuilder returns dict[str, str])
def build(self, agent: Agent, options: BuildOptions) -> dict[str, str]:
    return {
        ".claude/agents/code-agent.md": "# Code Agent\n...",
        ".claude/subagents/feature.md": "# Feature\n...",
        "CLAUDE.md": "# Claude Configuration\n..."
    }
```

#### Validation Contract

`validate()` must return a **list of error messages** (not raise exceptions):

```python
def validate(self, agent: Agent) -> list[str]:
    errors = []
    if not agent.name:
        errors.append("Agent name is required")
    if not agent.system_prompt:
        errors.append("System prompt is required")
    return errors  # Empty list = valid, non-empty = invalid
```

---

## Component System

### Overview

The component system separates:
- **Agent IR** - What you want to communicate
- **Components** - How you communicate it (minimal vs. verbose, formatted sections)

### ComponentSelector: Loading Variants

`ComponentSelector` loads components for a given agent and variant:

```python
from prompticorn.builders.component_selector import ComponentSelector, Variant, ComponentBundle

selector = ComponentSelector(agents_dir="agents")

# Load minimal variant (with fallback to verbose)
bundle = selector.select(agent, variant=Variant.MINIMAL)

# bundle contains:
# - variant: which variant was selected
# - prompt: system prompt content
# - skills: skills content (if exists)
# - workflow: workflow content (if exists)
# - fallback_used: whether we fell back to verbose
```

### ComponentComposer: Assembling Output

`ComponentComposer` takes a bundle and assembles it into formatted output:

```python
from prompticorn.builders.component_composer import ComponentComposer

# Compose into plain markdown
markdown = ComponentComposer.compose_markdown(
    bundle=bundle,
    agent=agent,
    include_sections=["prompt", "tools", "skills"]
)

# Compose into YAML + markdown
yaml_markdown = ComponentComposer.compose_yaml_markdown(
    bundle=bundle,
    agent=agent,
    frontmatter={"name": agent.name, "description": agent.description}
)
```

### Full Pattern Example

```python
class MyToolBuilder(Builder):
    def build(self, agent: Agent, options: BuildOptions) -> str:
        # Validate
        errors = self.validate(agent)
        if errors:
            raise BuilderValidationError(errors=errors)

        # Load components with variant selection
        selector = ComponentSelector()
        variant = Variant.MINIMAL if options.variant == "minimal" else Variant.VERBOSE
        bundle = selector.select(agent, variant=variant)

        # Build custom frontmatter
        frontmatter = {
            "name": agent.name,
            "description": agent.description,
        }

        # Compose YAML + markdown
        return ComponentComposer.compose_yaml_markdown(
            bundle=bundle,
            agent=agent,
            frontmatter=frontmatter
        )
```

---

## Output Format Patterns

### Pattern 1: Text-Based Formats (Kilo, Cline, Cursor)

Text-based formats output plain text strings (Markdown, YAML, plain text):

```python
class TextBasedBuilder(Builder):
    def build(self, agent: Agent, options: BuildOptions) -> str:
        """Return a string."""
        sections = []
        sections.append("# System Prompt")
        sections.append(agent.system_prompt)
        sections.append("")
        
        if options.include_tools:
            sections.append("# Tools")
            sections.append(self._format_tools(agent.tools))
        
        return "\n".join(sections)
```

**Advantages:**
- Simple to read and debug
- Easy to version control (diffs are readable)
- Works with any text editor

**Use for:**
- IDE-like tools (Kilo, Cline, Cursor)
- Configuration files
- Human-readable formats

### Pattern 2: Structured Formats (Claude, file path → content)

Structured formats output dictionaries mapping file paths to Markdown content:

```python
class StructuredBuilder(Builder):
    def build(self, agent: Agent, options: BuildOptions) -> dict[str, str]:
        """Return a dict mapping file paths to Markdown content."""
        return {
            ".claude/agents/code-agent.md": "# Code Agent\n...",
            "CLAUDE.md": "# Claude Configuration\n..."
        }
```

**Advantages:**
- Structured for programmatic use
- Easy to validate with JSON schema
- Natural for APIs

**Use for:**
- API endpoints
- Tool integrations
- Serializable data structures

### Pattern 3: Hybrid Formats (Copilot, YAML+Markdown)

Hybrid formats combine YAML metadata with Markdown content:

```python
class HybridBuilder(Builder):
    def build(self, agent: Agent, options: BuildOptions) -> str:
        """Return YAML frontmatter + markdown."""
        frontmatter = {
            "name": agent.name,
            "description": agent.description,
            "applyTo": [{"model": "code"}]
        }
        
        markdown = "\n".join([
            "# System Prompt",
            agent.system_prompt,
            "# Tools",
            self._format_tools(agent.tools)
        ])
        
        return self._compose_yaml_markdown(frontmatter, markdown)
```

**Advantages:**
- Machine-parseable metadata (YAML)
- Human-readable content (Markdown)
- Flexible structure

**Use for:**
- Tools that support front matter (GitHub, Jekyll)
- Configuration + documentation
- Metadata-driven formats

### Choosing Your Format

| Decision | Format | Builder |
|----------|--------|---------|
| IDE or text editor integration? | Text (Markdown) | Kilo, Cline, Cursor |
| API endpoint or JSON output? | Structured (JSON dict) | Claude |
| Configuration with metadata? | Hybrid (YAML+MD) | Copilot |
| Custom format? | Whatever you need | Custom |

---

## Real Example: ClineBuilder Walkthrough

Let's walk through `ClineBuilder` to see all the patterns in action:

### Overview

ClineBuilder generates `.clinerules` files (pure Markdown) for Cline IDE. It's simpler than KiloBuilder because it has no YAML frontmatter.

### File Structure

```
src/builders/
├── cline_builder.py         # Main builder class
├── base.py                  # Builder base class
├── component_selector.py    # Component loading
└── component_composer.py    # Component assembly

tests/unit/builders/
├── test_cline_builder.py    # Unit tests (52 tests)
└── test_integration/
    └── test_cline_builder.py # Integration tests (31 tests)
```

### Step 1: Class Definition and Initialization

```python
class ClineBuilder(Builder):
    """Builder for Cline IDE agent rules.

    Generates `.clinerules` files (pure Markdown format) with
    system prompt, tools, skills, workflows, and subagents sections.
    """

    def __init__(self, agents_dir: Path | str = "agents") -> None:
        """Initialize ClineBuilder.

        Args:
            agents_dir: Base directory for agent components
        """
        self.agents_dir = agents_dir
        self.selector = ComponentSelector(agents_dir=agents_dir)
```

**Key Points:**
- Store `agents_dir` for component loading
- Create a `ComponentSelector` instance for lazy loading

### Step 2: Implement Validation

```python
def validate(self, agent: Agent) -> list[str]:
    """Validate agent for Cline format.

    Cline requires: name, description, system_prompt
    """
    errors = []

    if not agent.name:
        errors.append("Agent name is required")

    if not agent.description:
        errors.append("Agent description is required")

    if not agent.system_prompt:
        errors.append("System prompt is required")

    return errors
```

**Key Points:**
- Return list of errors (not throw)
- Be specific: "Agent name is required" not "Invalid agent"
- Check all required fields

### Step 3: Implement Build Method

```python
def build(self, agent: Agent, options: BuildOptions) -> str:
    """Build .clinerules markdown file."""
    # 1. Validate first
    errors = self.validate(agent)
    if errors:
        raise BuilderValidationError(
            errors=errors,
            message=f"Invalid agent '{agent.name}': {'; '.join(errors)}"
        )

    # 2. Select variant (minimal or verbose)
    variant = Variant.MINIMAL if options.variant == "minimal" else Variant.VERBOSE

    # 3. Load components
    bundle = self.selector.select(agent, variant=variant)

    # 4. Build sections
    sections = []

    # System Prompt (always first)
    sections.append("# System Prompt\n")
    sections.append(bundle.prompt)
    sections.append("")

    # Tools (if requested and present)
    if options.include_tools and agent.tools:
        sections.append(self._format_tools(agent.tools))
        sections.append("")

    # Skills (if requested and present)
    if options.include_skills and bundle.skills:
        sections.append(self._build_skill_activation_instructions(bundle.skills))
        sections.append("")

    # Workflows (if requested and present)
    if options.include_workflows and bundle.workflow:
        sections.append(self._format_workflows(bundle.workflow))
        sections.append("")

    # Subagents (if requested and present)
    if options.include_subagents and agent.subagents:
        sections.append(self._format_subagents(agent.subagents))
        sections.append("")

    # 5. Compose final output
    return "\n".join(sections).strip()
```

**Key Points:**
- Always validate first
- Select variant early (before loading)
- Load components once
- Build each section independently
- Respect `options` flags for inclusion
- Strip final whitespace

### Step 4: Implement Format Methods

```python
def _format_tools(self, tools: list[str]) -> str:
    """Format tools as markdown list."""
    lines = ["# Tools\n"]
    for tool in tools:
        lines.append(f"- {tool}")
    return "\n".join(lines)

def _build_skill_activation_instructions(self, skills_content: str) -> str:
    """Build skill activation section.

    Cline-specific: Include "use_skill {name}" invocation pattern.
    """
    lines = ["# Skills\n"]
    lines.append("Use skills with: `use_skill {skill_name}`\n")
    lines.append(skills_content.strip())
    return "\n".join(lines)

def _format_workflows(self, workflow_content: str) -> str:
    """Format workflows section."""
    lines = ["# Workflows\n"]
    lines.append(workflow_content.strip())
    return "\n".join(lines)

def _format_subagents(self, subagents: list[str]) -> str:
    """Format subagents as markdown list."""
    lines = ["# Subagents\n"]
    for subagent in subagents:
        lines.append(f"- {subagent}")
    return "\n".join(lines)
```

**Key Points:**
- Each format method is focused and testable
- Include headers in section formatters
- Strip content to avoid extra whitespace
- Document tool-specific patterns (like `use_skill`)

### Step 5: Implement Tool Metadata

```python
def get_tool_name(self) -> str:
    """Get the tool name."""
    return "cline"

def get_output_format(self) -> str:
    """Get format description."""
    return "Cline IDE Rules File (Markdown)"
```

**Key Points:**
- `get_tool_name()` should match registration key
- `get_output_format()` should be human-readable

### Step 6: Test Structure

#### Unit Tests (test_cline_builder.py)

```python
class TestClineBuilderInitialization:
    """Tests for initialization."""
    
    def test_init_with_default_dir(self):
        builder = ClineBuilder()
        assert builder.agents_dir == "agents"

class TestClineBuilderValidation:
    """Tests for validation."""
    
    def test_validate_valid_agent(self):
        agent = Agent(
            name="test",
            description="Test",
            system_prompt="Test prompt"
        )
        builder = ClineBuilder()
        assert builder.validate(agent) == []
    
    def test_validate_missing_name(self):
        agent = Agent(name="", description="Test", system_prompt="Test")
        builder = ClineBuilder()
        errors = builder.validate(agent)
        assert len(errors) > 0

class TestClineBuilderFormatting:
    """Tests for formatting methods."""
    
    def test_format_tools(self):
        builder = ClineBuilder()
        result = builder._format_tools(["read", "write"])
        assert "# Tools" in result
        assert "- read" in result
        assert "- write" in result
```

#### Integration Tests (test_integration/)

```python
class TestClineBuilderFileIO:
    """Tests with real filesystem I/O."""
    
    def test_write_to_file(self, temp_agents_dir):
        builder = ClineBuilder(agents_dir=temp_agents_dir)
        agent = Agent(...)
        output = builder.build(agent, BuildOptions())
        
        # Write and verify
        output_file = temp_agents_dir / "test.clinerules"
        output_file.write_text(output)
        
        assert output_file.exists()
        assert len(output_file.read_text()) > 0

class TestClineBuilderMarkdownValidation:
    """Tests for markdown format validity."""
    
    def test_markdown_syntax_valid(self):
        builder = ClineBuilder()
        agent = Agent(...)
        output = builder.build(agent, BuildOptions())
        
        # Validate markdown structure
        assert output.count("# ") > 0  # Has headers
        assert not output.startswith("\n")  # No leading whitespace
```

**Key Points:**
- Unit tests: Fast, isolated, mock components
- Integration tests: Slow, real filesystem, validate format
- Test each format method independently
- Test variant selection
- Test optional component handling

---

## Testing Your Builder

### Unit Test Structure

Unit tests are fast and isolated. Mock the ComponentSelector:

```python
import pytest
from unittest.mock import Mock
from prompticorn.builders.my_tool_builder import MyToolBuilder
from prompticorn.builders.base import BuildOptions
from prompticorn.builders.component_selector import ComponentBundle, Variant
from prompticorn.ir.models import Agent

class TestMyToolBuilder:
    """Unit tests for MyToolBuilder."""

    @pytest.fixture
    def builder(self):
        """Create builder instance."""
        return MyToolBuilder()

    @pytest.fixture
    def sample_agent(self):
        """Create sample agent."""
        return Agent(
            name="test_agent",
            description="Test agent for unit tests",
            system_prompt="Test system prompt",
            tools=["tool1", "tool2"],
            skills=["skill1"],
            workflows=["workflow1"],
            subagents=["subagent1"]
        )

    # Test initialization
    def test_builder_initializes(self, builder):
        """Test builder can be instantiated."""
        assert builder is not None

    # Test validation
    def test_validate_passes_for_valid_agent(self, builder, sample_agent):
        """Test validation succeeds for valid agent."""
        errors = builder.validate(sample_agent)
        assert errors == []

    def test_validate_fails_for_missing_name(self, builder):
        """Test validation catches missing name."""
        agent = Agent(name="", description="Test", system_prompt="Test")
        errors = builder.validate(agent)
        assert len(errors) > 0
        assert any("name" in e.lower() for e in errors)

    # Test format methods
    def test_format_tools_single(self, builder):
        """Test formatting single tool."""
        result = builder._format_tools(["tool1"])
        assert "tool1" in result

    def test_format_tools_multiple(self, builder):
        """Test formatting multiple tools."""
        result = builder._format_tools(["tool1", "tool2", "tool3"])
        for tool in ["tool1", "tool2", "tool3"]:
            assert tool in result

    # Test tool metadata
    def test_get_tool_name(self, builder):
        """Test tool name."""
        assert builder.get_tool_name() == "mytool"

    def test_get_output_format(self, builder):
        """Test output format description."""
        fmt = builder.get_output_format()
        assert isinstance(fmt, str)
        assert len(fmt) > 0
```

### Integration Test Structure

Integration tests use real file I/O:

```python
import pytest
import tempfile
from pathlib import Path
from prompticorn.builders.my_tool_builder import MyToolBuilder
from prompticorn.builders.base import BuildOptions
from prompticorn.ir.models import Agent

class TestMyToolBuilderIntegration:
    """Integration tests with real filesystem I/O."""

    @pytest.fixture
    def temp_agents_dir(self):
        """Create temporary agents directory with structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            agents_path = Path(temp_dir) / "agents"
            agents_path.mkdir()

            # Create test agent structure
            agent_dir = agents_path / "test_agent" / "minimal"
            agent_dir.mkdir(parents=True)

            # Write component files
            (agent_dir / "prompt.md").write_text("Test prompt content")
            (agent_dir / "skills.md").write_text("Test skills content")

            yield agents_path

    def test_build_full_agent(self, temp_agents_dir):
        """Test building complete agent."""
        builder = MyToolBuilder(agents_dir=temp_agents_dir)
        agent = Agent(
            name="test_agent",
            description="Test",
            system_prompt="Test",
            tools=["tool1"],
            skills=["skill1"]
        )
        
        output = builder.build(agent, BuildOptions())
        assert isinstance(output, str)
        assert len(output) > 0

    def test_build_writes_to_file(self, temp_agents_dir):
        """Test writing built output to file."""
        with tempfile.TemporaryDirectory() as output_dir:
            builder = MyToolBuilder(agents_dir=temp_agents_dir)
            agent = Agent(
                name="test_agent",
                description="Test",
                system_prompt="Test"
            )
            
            output = builder.build(agent, BuildOptions())
            output_file = Path(output_dir) / "agent.md"
            output_file.write_text(output)
            
            assert output_file.exists()
            assert output_file.stat().st_size > 0
            assert output_file.read_text() == output

    def test_variant_selection(self, temp_agents_dir):
        """Test minimal/verbose variant selection."""
        builder = MyToolBuilder(agents_dir=temp_agents_dir)
        agent = Agent(
            name="test_agent",
            description="Test",
            system_prompt="Test"
        )
        
        # Test minimal variant
        minimal_output = builder.build(agent, BuildOptions(variant="minimal"))
        
        # Test verbose variant
        verbose_output = builder.build(agent, BuildOptions(variant="verbose"))
        
        assert isinstance(minimal_output, str)
        assert isinstance(verbose_output, str)
        # Verbose might be same if no minimal variant exists (fallback)
        # or different if both variants exist
```

### Mutation Testing

Verify test quality using mutation testing:

```bash
# Install mutation testing tool
pip install mutmut

# Run mutation tests on your builder
mutmut run --path src/builders/my_tool_builder.py --tests tests/unit/builders/test_my_tool_builder.py

# View results
mutmut results
mutmut html  # Generate HTML report
```

High mutation score (80%+) means your tests catch bugs.

---

## Extending Builders with Protocol Mixins

### What Are Protocol Mixins?

Protocol mixins use Python's `Protocol` class to declare optional features without tight coupling:

```python
from typing import Protocol

class SupportsSkills(Protocol):
    """Any class that implements build_skills conforms to this protocol."""
    
    def build_skills(self, skills: list[Skill]) -> str | dict[str, Any]:
        """Build skill-specific output."""
        ...
```

A builder that implements `build_skills` automatically satisfies `SupportsSkills`:

```python
class MyBuilder(Builder):
    def build_skills(self, skills: list[Skill]) -> str:
        """This method makes MyBuilder satisfy SupportsSkills."""
        return "\n".join(skill.name for skill in skills)

# Type checker understands this automatically
builder: SupportsSkills = MyBuilder()
```

### Available Protocols

| Protocol | Method | Purpose |
|----------|--------|---------|
| `SupportsSkills` | `build_skills(skills)` | Format skills component |
| `SupportsWorkflows` | `build_workflows(workflows)` | Format workflows component |
| `SupportsRules` | `build_rules(rules)` | Format rules component |
| `SupportsSubagents` | `build_subagents(subagents)` | Format subagents component |
| `SupportsTools` | `build_tools(tool_names)` | Format tools component |

### Implementing Protocol Methods

Example: Adding `SupportsSkills` to your builder

```python
from typing import Any
from prompticorn.ir.models import Skill
from prompticorn.builders.interfaces import SupportsSkills

class MyToolBuilder(Builder):
    """Builder with skill support."""

    # Implement the protocol method
    def build_skills(self, skills: list[Skill]) -> str:
        """Build skills section.
        
        Once this method exists, MyToolBuilder automatically
        conforms to SupportsSkills protocol.
        """
        lines = ["# Skills"]
        for skill in skills:
            lines.append(f"## {skill.name}")
            lines.append(skill.description or "No description")
            lines.append("")
        return "\n".join(lines)

# Now type checkers understand:
def use_skills_builder(builder: SupportsSkills) -> str:
    skills = [Skill(name="test", description="Test skill")]
    return builder.build_skills(skills)

# This works because MyToolBuilder implements build_skills
builder = MyToolBuilder()
output = use_skills_builder(builder)
```

### Custom Features

Beyond protocols, you can add custom builder methods for tool-specific features:

```python
class MyToolBuilder(Builder):
    """Builder with custom features."""

    def build(self, agent: Agent, options: BuildOptions) -> str:
        """Main build method."""
        # ...standard implementation...
        return output

    # Standard protocol implementations
    def build_skills(self, skills: list[Skill]) -> str:
        return "# Skills\n" + "\n".join(s.name for s in skills)

    # Custom tool-specific features
    def build_with_auth(self, agent: Agent, api_key: str) -> str:
        """Custom method: build with authentication."""
        output = self.build(agent, BuildOptions())
        return f"# API Key: {api_key}\n\n{output}"

    def get_supported_languages(self) -> list[str]:
        """Custom method: list supported programming languages."""
        return ["python", "typescript", "go"]
```

---

## Best Practices

### 1. Follow Core Conventions

Your builder must follow `core-conventions-python.md`:

- **Type hints** on all public methods
- **Docstrings** on all classes and public methods
- **Error handling** with specific exception types
- **No circular imports** or `import *`

```python
# ✓ Good
from typing import Any
from prompticorn.ir.models import Agent
from prompticorn.builders.base import Builder, BuildOptions
from prompticorn.builders.errors import BuilderValidationError

class MyBuilder(Builder):
    """Builder for MyTool."""

    def build(self, agent: Agent, options: BuildOptions) -> str:
        """Build MyTool output.
        
        Args:
            agent: Agent IR model
            options: Build options
            
        Returns:
            Formatted output string
            
        Raises:
            BuilderValidationError: If validation fails
        """
        # Implementation
        pass

# ✗ Bad
from prompticorn.builders.base import *

class MyBuilder(Builder):
    def build(self, agent, options):  # No type hints
        # No docstring
        return "output"
```

### 2. Comprehensive Validation

Check all requirements before building:

```python
# ✓ Good
def validate(self, agent: Agent) -> list[str]:
    """Validate agent for this builder."""
    errors = []

    if not agent.name:
        errors.append("Agent name is required")

    if not agent.description:
        errors.append("Agent description is required")

    if not agent.system_prompt:
        errors.append("System prompt is required")

    # Tool-specific validations
    if self.requires_tools and not agent.tools:
        errors.append("This builder requires at least one tool")

    return errors

# ✗ Bad
def validate(self, agent: Agent) -> list[str]:
    """Validate agent."""
    if not agent.name:
        raise ValueError("Missing name")  # Raises instead of returning
    return []

# ✗ Bad
def build(self, agent: Agent, options: BuildOptions) -> str:
    # No validation - just assumes everything exists
    return f"Name: {agent.name}"
```

### 3. Respect BuildOptions

Always check `options` flags before including components:

```python
# ✓ Good
def build(self, agent: Agent, options: BuildOptions) -> str:
    sections = []
    
    # Always include system prompt
    sections.append(f"# System Prompt\n{agent.system_prompt}")
    
    # Respect include_tools flag
    if options.include_tools and agent.tools:
        sections.append(self._format_tools(agent.tools))
    
    # Respect include_skills flag
    if options.include_skills and agent.skills:
        sections.append(self._format_skills(agent.skills))
    
    return "\n".join(sections)

# ✗ Bad
def build(self, agent: Agent, options: BuildOptions) -> str:
    # Ignores options completely
    sections = [
        f"# Tools\n{self._format_tools(agent.tools)}",
        f"# Skills\n{self._format_skills(agent.skills)}",
    ]
    return "\n".join(sections)
```

### 4. Graceful Degradation

Handle missing optional components:

```python
# ✓ Good
def build(self, agent: Agent, options: BuildOptions) -> str:
    sections = []
    sections.append(bundle.prompt)
    
    # Skills are optional - only include if present
    if bundle.skills:
        sections.append(self._format_skills(bundle.skills))
    
    # Workflows are optional - only include if present
    if bundle.workflow:
        sections.append(self._format_workflows(bundle.workflow))
    
    return "\n".join(sections)

# ✗ Bad
def build(self, agent: Agent, options: BuildOptions) -> str:
    sections = [
        bundle.prompt,
        self._format_skills(bundle.skills or ""),  # Silent fallback
        self._format_workflows(bundle.workflow or ""),
    ]
    return "\n".join(sections)  # Might have empty sections
```

### 5. Clear Error Messages

Make debugging easy:

```python
# ✓ Good
if errors:
    raise BuilderValidationError(
        errors=errors,
        message=f"Cannot build agent '{agent.name}': "
                f"{len(errors)} validation error(s). "
                f"Details: {'; '.join(errors)}"
    )

# ✗ Bad
if errors:
    raise BuilderValidationError(errors=errors)
```

### 6. Unit Test Each Method

Test methods independently:

```python
# ✓ Good
def test_format_tools_single(self):
    builder = MyToolBuilder()
    result = builder._format_tools(["tool1"])
    assert "tool1" in result

def test_format_tools_empty_list(self):
    builder = MyToolBuilder()
    result = builder._format_tools([])
    assert result.strip() == ""  # Or appropriate empty format

def test_format_tools_special_characters(self):
    builder = MyToolBuilder()
    result = builder._format_tools(["tool-1", "tool_2"])
    assert "tool-1" in result
    assert "tool_2" in result

# ✗ Bad
def test_build_full_agent(self):
    # Tests 10 things at once, hard to debug when it fails
    builder = MyToolBuilder()
    agent = Agent(...)
    result = builder.build(agent, BuildOptions())
    # Asserts everything, unclear what failed
```

### 7. Document Tool-Specific Behavior

Explain what makes your builder unique:

```python
class MyToolBuilder(Builder):
    """Builder for MyTool agent configurations.
    
    MyTool-specific behaviors:
    - Requires agents_dir to contain agent/{name}/variant/ structure
    - Supports only 'minimal' and 'verbose' variants
    - Falls back to 'verbose' if 'minimal' not available
    - Outputs YAML frontmatter + Markdown sections
    - Section order: system prompt, tools, skills, workflows, subagents
    
    Example:
        builder = MyToolBuilder(agents_dir="agents")
        agent = Agent(name="code", ...)
        output = builder.build(agent, BuildOptions())
        print(output)  # YAML frontmatter + markdown
    """
```

---

## FAQ

### Q: How do I add a new builder?

**A:** Follow the Quick Start section:
1. Create a class extending `Builder`
2. Implement `build()`, `validate()`, `get_tool_name()`, `get_output_format()`
3. Register with `BuilderFactory.register('toolname', MyBuilder)`
4. Write unit and integration tests
5. Add documentation

### Q: What if my tool has a unique output format?

**A:** You have full flexibility in the `build()` return type:
- Return `str` for text formats (JSON strings, YAML, Markdown)
- Return `dict` for structured formats (ready to serialize)
- Return any combination of formatting logic
- Document the format clearly

### Q: Can I share code between builders?

**A:** Yes, but follow these patterns:
- **Shared components**: Use `ComponentSelector` and `ComponentComposer`
- **Shared validation logic**: Create a base class or utility function
- **Avoid inheritance hell**: Keep `Builder` simple; compose instead

```python
# ✓ Good: Shared validation helper
def validate_common_fields(agent: Agent) -> list[str]:
    """Shared validation for all builders."""
    errors = []
    if not agent.name:
        errors.append("Name required")
    if not agent.system_prompt:
        errors.append("System prompt required")
    return errors

class Builder1(Builder):
    def validate(self, agent: Agent) -> list[str]:
        return validate_common_fields(agent) + self._validate_specific(agent)

# ✓ Good: Use composition
class MyBuilder(Builder):
    def __init__(self):
        self.selector = ComponentSelector()
        self.composer = ComponentComposer()
        
    def build(self, agent: Agent, options: BuildOptions) -> str:
        bundle = self.selector.select(agent)
        return self.composer.compose_markdown(bundle, agent)
```

### Q: How do I test with different agent structures?

**A:** Use fixtures to create realistic test data:

```python
@pytest.fixture
def simple_agent(self):
    """Minimal valid agent."""
    return Agent(
        name="test",
        description="Test",
        system_prompt="Test"
    )

@pytest.fixture
def complex_agent(self):
    """Agent with all optional fields."""
    return Agent(
        name="complex",
        description="Complex agent",
        system_prompt="Prompt",
        tools=["t1", "t2"],
        skills=["s1"],
        workflows=["w1"],
        subagents=["sub1"]
    )

def test_simple_agent(self, simple_agent):
    """Test with minimal agent."""
    builder = MyToolBuilder()
    output = builder.build(simple_agent, BuildOptions())
    assert len(output) > 0

def test_complex_agent(self, complex_agent):
    """Test with full agent."""
    builder = MyToolBuilder()
    output = builder.build(complex_agent, BuildOptions())
    assert len(output) > len(self.test_simple_agent(agent))
```

### Q: What about error handling in build()?

**A:** Always validate first, then use specific exceptions:

```python
from prompticorn.builders.errors import BuilderValidationError, BuilderException

def build(self, agent: Agent, options: BuildOptions) -> str:
    # 1. Validate first
    errors = self.validate(agent)
    if errors:
        raise BuilderValidationError(
            errors=errors,
            message=f"Validation failed: {'; '.join(errors)}"
        )
    
    # 2. Handle component loading errors
    try:
        bundle = self.selector.select(agent)
    except VariantNotFoundError as e:
        raise BuilderException(
            message=f"Could not load components: {e}",
            original_error=e
        )
    
    # 3. Proceed with safe implementation
    return self._compose_output(bundle, agent, options)
```

### Q: How do I handle variant selection?

**A:** Use `ComponentSelector` with fallback:

```python
from prompticorn.builders.component_selector import ComponentSelector, Variant

def build(self, agent: Agent, options: BuildOptions) -> str:
    # Select variant
    variant = Variant.MINIMAL if options.variant == "minimal" else Variant.VERBOSE
    
    # Load with automatic fallback to verbose if minimal missing
    bundle = self.selector.select(agent, variant=variant)
    
    # bundle.fallback_used tells you if fallback was used
    if bundle.fallback_used:
        logger.warning(f"Using verbose variant for {agent.name} (minimal not found)")
    
    # Use the loaded components
    return self._build_output(bundle, agent, options)
```

### Q: Can I add custom configuration to my builder?

**A:** Yes, add `__init__` parameters:

```python
class MyBuilder(Builder):
    def __init__(
        self,
        agents_dir: Path | str = "agents",
        max_tools: int = 10,
        indent: int = 2,
        strict_mode: bool = False
    ) -> None:
        """Initialize with custom configuration.
        
        Args:
            agents_dir: Base agents directory
            max_tools: Maximum tools to include (0 for unlimited)
            indent: Indentation level for nested content
            strict_mode: Enable strict validation
        """
        self.agents_dir = agents_dir
        self.max_tools = max_tools
        self.indent = indent
        self.strict_mode = strict_mode
        self.selector = ComponentSelector(agents_dir=agents_dir)
    
    def validate(self, agent: Agent) -> list[str]:
        errors = []
        # ...base validation...
        
        if self.strict_mode and self.max_tools > 0:
            if len(agent.tools) > self.max_tools:
                errors.append(f"Too many tools: {len(agent.tools)} > {self.max_tools}")
        
        return errors
```

---

## Summary

Creating a new builder means:

1. **Understand** the tool's format requirements
2. **Validate** agents comprehensively
3. **Load** components (with variant selection)
4. **Format** each section appropriately
5. **Compose** the final output
6. **Test** thoroughly (unit + integration)
7. **Document** tool-specific behaviors

Use the pattern established by existing builders (Kilo, Cline, Claude, Copilot, Cursor) as templates. Follow core-conventions-python.md for code quality. Write tests first, then implementation.

For questions or issues, refer to the existing builders in `prompticorn/builders/` or the test suite in `tests/unit/builders/` and `tests/integration/`.
