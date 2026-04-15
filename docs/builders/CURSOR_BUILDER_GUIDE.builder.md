# CursorBuilder Comprehensive Guide

A detailed guide for building Cursor IDE rules files from Agent IR models.

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

**CursorBuilder** is the builder for [Cursor IDE](https://cursor.sh), a next-generation IDE powered by AI that's designed for AI-first development. It transforms Agent IR models into `.cursorrules` configuration files that control Cursor's behavior within your workspace.

### What CursorBuilder Does

- **Input:** Agent IR models (Python dataclasses with agent definitions)
- **Output:** Markdown files with prose format (no YAML frontmatter)
- **Target:** `.cursorrules` files for Cursor IDE integration
- **Supports:** System prompts, constraints, tools, workflows, and subagents

### Output Format

CursorBuilder generates pure markdown with clear sections:

```markdown
# {Agent Name} Rules

You are an expert [description]. [System prompt as prose].

Your responsibilities:
- [responsibility 1]
- [responsibility 2]

## Core Constraints

- Type hints required on all public functions
- Read code BEFORE writing code
- Match existing patterns exactly

## Available Tools

### bash
Purpose: Execute shell commands
Usage: Call with appropriate parameters

### python
Purpose: Execute Python code
Usage: Call with appropriate parameters

## Workflows

When implementing features:
1. Understand requirements
2. Design solution
3. Implement code
4. Write tests
5. Review

## Subagents Available

- **architect**: Specializes in architecture tasks
- **tester**: Specializes in tester tasks
```

### Key Features

✅ Pure markdown format (no YAML)
✅ Prose-based instructions
✅ Core constraints section
✅ Tool documentation
✅ Workflow definitions
✅ Subagent descriptions
✅ Cursor IDE optimized

---

## Quick Start

### Most Basic Example

```python
from promptosaurus.builders.cursor_builder import CursorBuilder
from promptosaurus.builders.base import BuildOptions
from promptosaurus.ir.models import Agent

# Create a builder
builder = CursorBuilder()

# Create an agent
agent = Agent(
    name="developer",
    description="A software developer",
    system_prompt="You are a skilled software developer who writes clean code.",
    tools=["bash", "python"],
)

# Build the rules
options = BuildOptions(variant="minimal", agent_name="developer")
output = builder.build(agent, options)

print(output)
```

### Expected Output

```markdown
# developer Rules

You are a skilled software developer who writes clean code.

## Core Constraints

- Type hints required on all public functions
- No `any` types without explicit justification
- Read code BEFORE writing code
- Match existing patterns exactly

## Available Tools

### bash
Purpose: [Description of bash]
Usage: Call with appropriate parameters

### python
Purpose: [Description of python]
Usage: Call with appropriate parameters
```

---

## Installation & Setup

### Prerequisites

- Python 3.11+
- Cursor IDE installed and configured
- Agent IR models properly defined

### Import

```python
from promptosaurus.builders.cursor_builder import CursorBuilder
from promptosaurus.builders.base import BuildOptions, BuilderValidationError
from promptosaurus.ir.models import Agent
```

### Initialize

```python
# Option 1: Default initialization
builder = CursorBuilder()

# Option 2: With custom agents directory
builder = CursorBuilder(agents_dir="cursor_configs")

# Option 3: Using Path object
from pathlib import Path
builder = CursorBuilder(agents_dir=Path(".cursor"))
```

### Verify Installation

```python
# Check tool information
print(builder.get_tool_name())          # Returns: "cursor"
print(builder.get_output_format())      # Returns: "Cursor AI Rules File (Markdown)"

# Verify feature support
print(builder.supports_feature("skills"))      # True
print(builder.supports_feature("workflows"))   # True
print(builder.supports_feature("rules"))       # True
```

---

## Basic Usage

### 1. Create Agent Model

```python
from promptosaurus.ir.models import Agent

agent = Agent(
    name="feature_builder",
    description="Builds new features with best practices",
    system_prompt="""You are an expert feature developer.

Your responsibilities:
- Understand requirements thoroughly
- Design clean, maintainable solutions
- Write production-ready code
- Consider edge cases
- Follow established patterns
- Write comprehensive tests""",
    tools=["bash", "python", "git"],
    skills=["feature_design", "implementation", "testing"],
)
```

### 2. Validate Agent

```python
# Always validate first
errors = builder.validate(agent)

if errors:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("✓ Agent validation passed")
```

### 3. Create Build Options

```python
from promptosaurus.builders.base import BuildOptions

# Configure for Cursor
options = BuildOptions(
    variant="verbose",
    agent_name="feature_builder",
    include_rules=True,          # Include constraints
    include_tools=True,
    include_workflows=True,
)
```

### 4. Build Rules File

```python
try:
    rules = builder.build(agent, options)
    print(rules)
except BuilderValidationError as e:
    print(f"Build failed: {e.message}")
```

### 5. Save to .cursorrules

```python
from pathlib import Path

# Generate output
rules = builder.build(agent, options)

# Save to .cursorrules
cursorrules_path = Path(".cursorrules")
cursorrules_path.write_text(rules)

print(f"✓ Saved Cursor rules to {cursorrules_path}")
```

---

## Advanced Usage Patterns

### Pattern 1: Project-Specific Constraints

Cursor supports detailed constraint sections for type safety and code quality.

```python
# Agent with detailed constraints
agent = Agent(
    name="type_safe_developer",
    description="Writes type-safe Python code",
    system_prompt="You write production-grade type-safe Python.",
    tools=["python", "bash"],
)

options = BuildOptions(
    variant="verbose",
    include_rules=True,  # Enable constraints section
)

rules = builder.build(agent, options)

# Output includes:
# ## Core Constraints
# - Type hints required on all public functions
# - No `any` types without explicit justification
# - Read code BEFORE writing code
# - Match existing patterns exactly
```

### Pattern 2: Workflow-Driven Development

```python
# Agent with detailed workflow
agent = Agent(
    name="workflow_expert",
    description="Follows disciplined development workflow",
    system_prompt="""You follow a rigorous development workflow.

Every task proceeds through:
1. Requirement Analysis
2. Design Review
3. Implementation
4. Testing
5. Code Review
6. Documentation""",
    tools=["python", "pytest", "git"],
    workflows=["requirement_analysis", "implementation", "testing"],
)

options = BuildOptions(
    variant="verbose",
    include_workflows=True,  # Enable workflows section
)

rules = builder.build(agent, options)
# Workflows appear in dedicated section
```

### Pattern 3: Subagent-Based Architecture

```python
# Agent that delegates to specialists
orchestrator = Agent(
    name="tech_lead",
    description="Technical lead coordinating specialists",
    system_prompt="""You are a tech lead managing specialists.

For different tasks, delegate to:
- Architecture specialist
- Performance specialist
- Security specialist
- Testing specialist""",
    tools=["coordination"],
    subagents=["architect", "performance_specialist", "security_specialist", "test_specialist"],
)

options = BuildOptions(
    variant="verbose",
    include_subagents=True,
)

rules = builder.build(orchestrator, options)

# Output includes subagent list with descriptions
```

### Pattern 4: Language-Specific Rules

```python
def build_language_rules(language: str) -> str:
    """Build language-specific Cursor rules."""
    
    language_specs = {
        "python": {
            "constraints": [
                "Type hints required on all public functions",
                "Use f-strings for string formatting",
                "Follow PEP 8 style guide",
                "Use type annotations for complex types",
            ],
            "tools": ["python", "bash", "pytest"],
        },
        "typescript": {
            "constraints": [
                "Strict mode enabled",
                "No `any` types",
                "ESLint configuration enforced",
                "Use const/let, never var",
            ],
            "tools": ["node", "typescript", "jest"],
        },
        "rust": {
            "constraints": [
                "Memory safety first",
                "No unsafe blocks without justification",
                "Error handling with Result",
                "Follow Rust idioms",
            ],
            "tools": ["rust", "cargo", "bash"],
        },
    }
    
    spec = language_specs.get(language)
    if not spec:
        raise ValueError(f"Unknown language: {language}")
    
    agent = Agent(
        name=f"{language}_expert",
        description=f"{language.capitalize()} development expert",
        system_prompt=f"You are an expert {language} developer.",
        tools=spec["tools"],
    )
    
    options = BuildOptions(
        variant="verbose",
        include_rules=True,
        include_tools=True,
    )
    
    return builder.build(agent, options)

# Usage
for lang in ["python", "typescript", "rust"]:
    rules = build_language_rules(lang)
    # Save or use rules
```

### Pattern 5: Domain-Specific Rules

```python
def build_domain_rules(domain: str) -> str:
    """Build domain-specific Cursor rules."""
    
    domain_specs = {
        "web_backend": {
            "description": "Web backend development",
            "constraints": [
                "API contracts defined in OpenAPI",
                "Database migrations required",
                "Authentication required",
                "Input validation mandatory",
            ],
            "tools": ["python", "bash", "sql"],
        },
        "web_frontend": {
            "description": "Web frontend development",
            "constraints": [
                "Component tests required",
                "Accessibility standards (WCAG) must be met",
                "Performance budget observed",
                "SEO best practices followed",
            ],
            "tools": ["typescript", "node", "jest"],
        },
        "ml_engineering": {
            "description": "Machine learning development",
            "constraints": [
                "Data validation documented",
                "Model versioning required",
                "Training reproducible",
                "Metrics tracked",
            ],
            "tools": ["python", "bash", "jupyter"],
        },
    }
    
    spec = domain_specs.get(domain)
    if not spec:
        raise ValueError(f"Unknown domain: {domain}")
    
    agent = Agent(
        name=domain,
        description=spec["description"],
        system_prompt=f"You develop in the {domain} domain.",
        tools=spec["tools"],
    )
    
    options = BuildOptions(variant="verbose", include_rules=True)
    return builder.build(agent, options)
```

---

## Configuration Options

### BuildOptions for Cursor

```python
@dataclass
class BuildOptions:
    variant: str = "minimal"          # minimal or verbose
    agent_name: str = ""              # Agent name
    include_subagents: bool = True    # Include subagents
    include_skills: bool = True       # Include skills
    include_workflows: bool = True    # Include workflows
    include_rules: bool = True        # Include constraints/rules
    include_tools: bool = True        # Include tools
```

### Core Constraints (Auto-Generated)

The constraints section is automatically generated with defaults:

```markdown
## Core Constraints

- Type hints required on all public functions
- No `any` types without explicit justification
- Read code BEFORE writing code
- Match existing patterns exactly
```

### Variant Comparison

| Aspect | minimal | verbose |
|--------|---------|---------|
| Constraints | Default | Detailed |
| Tools | Listed only | Full descriptions |
| Workflows | Skipped | Included |
| Subagents | Skipped | Included |
| File size | Small | Large |

---

## Common Patterns & Best Practices

### ✅ DO: Write Detailed Responsibilities

```python
# GOOD - Clear responsibilities
agent = Agent(
    name="developer",
    system_prompt="""You are a developer.

Your responsibilities:
1. Write clean, maintainable code
2. Follow project conventions
3. Consider edge cases
4. Document your code
5. Write tests
6. Improve performance""",
)
```

```python
# BAD - Vague responsibilities
agent = Agent(
    name="developer",
    system_prompt="You are a developer.",
)
```

### ✅ DO: Include Read-Code-First Instruction

```python
# GOOD - Cursor-specific best practice
agent = Agent(
    system_prompt="""Your workflow:
1. Read existing code in the file
2. Understand patterns
3. Follow established conventions
4. Write matching code
5. Test thoroughly""",
)
```

### ✅ DO: List Concrete Constraints

```python
# GOOD - Specific, actionable constraints
agent = Agent(
    system_prompt="""Constraints:
- Type hints on all public functions
- No single-letter variables (except i, j in loops)
- Functions under 50 lines
- Docstrings for public APIs
- 80% test coverage minimum""",
)
```

### ✅ DO: Use Cursor-Specific Conventions

```python
# GOOD - Cursor conventions
agent = Agent(
    name="cursor_expert",
    system_prompt="""You work with Cursor IDE.

Available tools in Cursor:
- Bash for command execution
- Python for code manipulation
- Built-in file editing

Use these effectively.""",
    tools=["bash", "python"],
)
```

### ✅ DO: Include Tool Descriptions

```python
# Tools with context
agent = Agent(
    tools=["python", "bash", "git"],
    system_prompt="""Tools available:

- python: Run Python code for analysis/manipulation
- bash: Execute shell commands
- git: Version control operations""",
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
agent = Agent(name="descriptive_name", ...)
```

### Issue: "System prompt is required"

**Problem:**
```python
agent = Agent(system_prompt="", ...)
```

**Solution:**
```python
agent = Agent(
    system_prompt="""You are an expert in your domain.

Your responsibilities:
- [responsibility 1]
- [responsibility 2]

Constraints:
- [constraint 1]
- [constraint 2]""",
)
```

### Issue: Cursor doesn't recognize .cursorrules

**Problem:**
- File not named `.cursorrules` (no `.md` extension)
- File not in project root
- Cursor needs to be restarted

**Solution:**
```python
# Save as .cursorrules (no extension)
cursorrules_path = Path(".cursorrules")
cursorrules_path.write_text(rules)

# Restart Cursor IDE
```

### Issue: Constraints not appearing

**Problem:**
```python
options = BuildOptions(include_rules=False)  # Disabled!
```

**Solution:**
```python
options = BuildOptions(include_rules=True)  # Enable
```

---

## API Reference

### CursorBuilder Class

#### Constructor

```python
def __init__(self, agents_dir: Path | str = "agents") -> None:
    """Initialize CursorBuilder.
    
    Args:
        agents_dir: Base directory for agent configurations
    """
```

#### Core Methods

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `build` | `build(agent: Agent, options: BuildOptions) -> str` | String | Builds markdown rules file |
| `validate` | `validate(agent: Agent) -> list[str]` | List | Returns validation errors |
| `get_output_format` | `get_output_format() -> str` | String | Returns format description |
| `get_tool_name` | `get_tool_name() -> str` | String | Returns "cursor" |
| `supports_feature` | `supports_feature(feature: str) -> bool` | Bool | Checks feature support |

#### Main Build Method

```python
def build(self, agent: Agent, options: BuildOptions) -> str:
    """Build a Cursor AI configuration file.
    
    Args:
        agent: The Agent IR model to build from
        options: Build configuration options
    
    Returns:
        String containing markdown content for .cursorrules file
    
    Raises:
        BuilderValidationError: If the agent model is invalid
    """
```

#### Validation

```python
def validate(self, agent: Agent) -> list[str]:
    """Validate an Agent IR model for Cursor.
    
    Checks:
    - Agent name is non-empty
    - Agent description is non-empty
    - System prompt is non-empty
    
    Args:
        agent: The Agent IR model to validate
    
    Returns:
        List of validation error messages (empty if valid)
    """
```

---

## Full Working Examples

### Example 1: Simple Developer Rules

```python
from promptosaurus.builders.cursor_builder import CursorBuilder
from promptosaurus.builders.base import BuildOptions
from promptosaurus.ir.models import Agent
from pathlib import Path

def create_developer_rules():
    """Create .cursorrules for general development."""
    
    builder = CursorBuilder()
    
    agent = Agent(
        name="developer",
        description="General software developer",
        system_prompt="""You are a skilled software developer.

Your responsibilities:
- Write clean, readable code
- Follow project conventions
- Consider edge cases
- Maintain performance
- Write comprehensive tests
- Document your work

Always read existing code before making changes.""",
        tools=["bash", "python", "git"],
    )
    
    options = BuildOptions(
        variant="verbose",
        include_rules=True,
        include_tools=True,
    )
    
    rules = builder.build(agent, options)
    
    # Save to .cursorrules
    Path(".cursorrules").write_text(rules)
    print("✓ Created .cursorrules")
    
    return rules

if __name__ == "__main__":
    rules = create_developer_rules()
    print(rules)
```

### Example 2: Type-Safe Python Development

```python
from promptosaurus.builders.cursor_builder import CursorBuilder
from promptosaurus.builders.base import BuildOptions
from promptosaurus.ir.models import Agent
from pathlib import Path

def create_python_rules():
    """Create .cursorrules for Python development."""
    
    builder = CursorBuilder()
    
    agent = Agent(
        name="python_developer",
        description="Type-safe Python development expert",
        system_prompt="""You are a Python development expert.

Your approach:
1. Write type-hinted code
2. Use pydantic for validation
3. Follow PEP 8
4. Use async/await properly
5. Handle errors explicitly
6. Test thoroughly

Constraints:
- Type hints required on all public functions
- No `any` types without justification
- Use f-strings for formatting
- Prefer dataclasses/pydantic over dicts
- Always import from future annotations""",
        tools=["python", "bash", "pytest"],
        skills=["type_safety", "async_programming", "testing"],
    )
    
    options = BuildOptions(
        variant="verbose",
        include_rules=True,
        include_tools=True,
        include_skills=True,
    )
    
    rules = builder.build(agent, options)
    Path(".cursorrules").write_text(rules)
    
    return rules

if __name__ == "__main__":
    rules = create_python_rules()
```

### Example 3: Full-Stack Web Development

```python
from promptosaurus.builders.cursor_builder import CursorBuilder
from promptosaurus.builders.base import BuildOptions
from promptosaurus.ir.models import Agent
from pathlib import Path

def create_fullstack_rules():
    """Create .cursorrules for full-stack development."""
    
    builder = CursorBuilder()
    
    agent = Agent(
        name="fullstack_engineer",
        description="Full-stack web development expert",
        system_prompt="""You are a full-stack web engineer.

Front-end (TypeScript/React):
- Components must be testable
- Use TypeScript strict mode
- Follow accessibility standards
- Optimize for performance

Back-end (Python/FastAPI):
- Type hints everywhere
- Validate all inputs
- Document APIs with OpenAPI
- Write migrations for schema changes

Responsibilities:
- Build features end-to-end
- Ensure seamless integration
- Write tests for both layers
- Optimize database queries
- Monitor performance""",
        tools=["typescript", "python", "bash", "sql"],
        skills=["frontend", "backend", "database", "devops"],
        subagents=["frontend_specialist", "backend_specialist"],
    )
    
    options = BuildOptions(
        variant="verbose",
        include_rules=True,
        include_tools=True,
        include_skills=True,
        include_subagents=True,
    )
    
    rules = builder.build(agent, options)
    Path(".cursorrules").write_text(rules)
    
    return rules

if __name__ == "__main__":
    rules = create_fullstack_rules()
```

### Example 4: Specialized Domain Rules

```python
from promptosaurus.builders.cursor_builder import CursorBuilder
from promptosaurus.builders.base import BuildOptions
from promptosaurus.ir.models import Agent
from pathlib import Path
import json

def create_domain_specific_rules(domain_config_path: str):
    """Create domain-specific Cursor rules."""
    
    # Load domain configuration
    with open(domain_config_path) as f:
        config = json.load(f)
    
    builder = CursorBuilder()
    
    agent = Agent(
        name=config["name"],
        description=config["description"],
        system_prompt=config["system_prompt"],
        tools=config.get("tools", []),
        skills=config.get("skills", []),
        subagents=config.get("subagents", []),
    )
    
    options = BuildOptions(
        variant=config.get("variant", "verbose"),
        include_rules=config.get("include_rules", True),
        include_tools=config.get("include_tools", True),
        include_skills=config.get("include_skills", True),
        include_subagents=config.get("include_subagents", False),
    )
    
    rules = builder.build(agent, options)
    Path(".cursorrules").write_text(rules)
    
    print(f"✓ Created rules for {config['name']}")
    return rules

if __name__ == "__main__":
    # Example config.json
    config = {
        "name": "mlops_engineer",
        "description": "MLOps engineer",
        "system_prompt": "You are an MLOps engineer.",
        "tools": ["python", "bash", "docker"],
        "skills": ["ml_deployment", "monitoring", "scaling"],
        "variant": "verbose"
    }
    
    with open("domain.json", "w") as f:
        json.dump(config, f)
    
    rules = create_domain_specific_rules("domain.json")
```

---

## Related Builders

For building other tools, see:
- [KiloBuilder Guide](./KILO_BUILDER_GUIDE.md) - For Kilo IDE
- [ClineBuilder Guide](./CLINE_BUILDER_GUIDE.md) - For Cline AI
- [ClaudeBuilder Guide](./CLAUDE_BUILDER_GUIDE.md) - For Claude API
- [CopilotBuilder Guide](./COPILOT_BUILDER_GUIDE.md) - For GitHub Copilot

---

## Support & Resources

- **Source Code:** `promptosaurus/builders/cursor_builder.py`
- **Base Class:** `promptosaurus/builders/base.py` (Builder)
- **IR Models:** `promptosaurus/ir/models.py` (Agent dataclass)
- **Examples:** `promptosaurus/builders/examples_usage.py`
- **Cursor Docs:** [cursor.sh](https://cursor.sh)
- **Cursor Rules Guide:** [cursor.sh/docs/.cursorrules](https://cursor.sh/docs/.cursorrules)

