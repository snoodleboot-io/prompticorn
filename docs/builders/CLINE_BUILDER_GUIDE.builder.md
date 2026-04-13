# ClineBuilder Comprehensive Guide

A detailed guide for building Cline AI rules files from Agent IR models.

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

**ClineBuilder** is the builder for [Cline](https://github.com/cline/cline), an advanced AI assistant that works directly in your IDE and terminal. It transforms Agent IR models into `.clinerules` configuration files that control how Cline behaves within your workspace.

### What ClineBuilder Does

- **Input:** Agent IR models (Python dataclasses with agent definitions)
- **Output:** Markdown files in prose format (no YAML frontmatter)
- **Target:** `.clinerules` files for Cline IDE integration
- **Supports:** System prompts, tools, skills, workflows, and subagents

### Output Format

ClineBuilder generates prose markdown with clear sections:

```markdown
# {Agent Name} Rules

You are an expert [description]. Your system prompt as narrative prose.

## Tools

Available tools:

- **bash**: Execute shell commands
- **python**: Execute Python code

## Skills

The following skills are available. Use them by calling use_skill::

### Skill: code-generation
Invoke by: `use_skill code_generation`

### Skill: debugging
Invoke by: `use_skill debugging`

## Workflows

When implementing features:
1. Understand requirements
2. Design solution
3. Implement code

## Subagents

You may delegate to these specialists:

### Subagent: architect
Specializes in architecture tasks.
Invoke by: `use_skill architect` or request 'architect subagent'
```

### Key Features

✅ Pure markdown (no YAML)
✅ Prose-based instructions
✅ `use_skill` invocation patterns
✅ Subagent delegation syntax
✅ Workflow step-by-step instructions
✅ Natural language focused

---

## Quick Start

### Most Basic Example

```python
from src.builders.cline_builder import ClineBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent

# Create a builder
builder = ClineBuilder(agents_dir=".cline")

# Create an agent
agent = Agent(
    name="code_assistant",
    description="Helps with code development",
    system_prompt="""You are a helpful coding assistant.

Your role:
- Help write clean, maintainable code
- Suggest improvements
- Follow best practices
- Use available tools when needed""",
    tools=["bash", "python"],
)

# Build the configuration
options = BuildOptions(variant="minimal", agent_name="code_assistant")
output = builder.build(agent, options)

# output is markdown prose
print(output)
```

### Expected Output

```markdown
# code_assistant Rules

You are a helpful coding assistant.

Your role:
- Help write clean, maintainable code
- Suggest improvements
- Follow best practices
- Use available tools when needed

## Tools

Available tools:

- **bash**: [Tool description and usage]
- **python**: [Tool description and usage]
```

---

## Installation & Setup

### Prerequisites

- Python 3.11+
- Agent IR models with proper definitions
- Knowledge of Cline workspace integration

### Import

```python
from src.builders.cline_builder import ClineBuilder
from src.builders.base import BuildOptions, BuilderValidationError
from src.ir.models import Agent
```

### Initialize

```python
# Option 1: Default initialization
builder = ClineBuilder()

# Option 2: With custom agents directory
builder = ClineBuilder(agents_dir=".cline/rules")

# Option 3: Using Path object
from pathlib import Path
builder = ClineBuilder(agents_dir=Path("custom/cline"))
```

### Verify Setup

```python
# Check tool information
print(builder.get_tool_name())          # Returns: "cline"
print(builder.get_output_format())      # Returns: "Cline AI Rules File (Markdown)"

# Check feature support
print(builder.supports_feature("skills"))      # True
print(builder.supports_feature("workflows"))   # True
print(builder.supports_feature("subagents"))   # True
```

---

## Basic Usage

### 1. Create an Agent Model

```python
from src.ir.models import Agent

agent = Agent(
    name="code_reviewer",
    description="Reviews code for quality and best practices",
    system_prompt="""You are an expert code reviewer.

Your responsibilities:
- Identify bugs and potential issues
- Suggest architectural improvements
- Ensure code follows best practices
- Maintain consistent style
- Catch security vulnerabilities

Focus on maintainability and performance.""",
    tools=["bash", "grep"],
    skills=["code_review", "static_analysis"],
    subagents=["security_auditor"],
)
```

### 2. Validate the Agent

```python
# Always validate before building
errors = builder.validate(agent)

if errors:
    print("Validation failed:")
    for error in errors:
        print(f"  - {error}")
else:
    print("Agent validation passed!")
```

### 3. Configure Build Options

```python
from src.builders.base import BuildOptions

# Create options for Cline rules
options = BuildOptions(
    variant="verbose",  # Full detail
    agent_name="code_reviewer",
    include_tools=True,
    include_skills=True,
    include_workflows=True,
    include_subagents=True,
)
```

### 4. Build the Rules File

```python
try:
    rules_content = builder.build(agent, options)
    print(rules_content)
except BuilderValidationError as e:
    print(f"Build failed: {e.message}")
    for error in e.errors:
        print(f"  - {error}")
```

### 5. Save to .clinerules

```python
from pathlib import Path

# Generate output
rules_content = builder.build(agent, options)

# Save to .clinerules file
cline_rules_path = Path(".clinerules")
cline_rules_path.write_text(rules_content)

print(f"✓ Saved Cline rules to {cline_rules_path}")
```

---

## Advanced Usage Patterns

### Pattern 1: Delegating to Subagents

Cline supports delegating to specialized subagents using the `use_skill` syntax.

```python
# Agent with specialists
orchestrator = Agent(
    name="orchestrator",
    description="Coordinates specialized agents",
    system_prompt="""You are an orchestrator agent.

Delegate work to specialists when needed:
- Security issues → security_auditor
- Performance → performance_specialist
- Architecture → architect""",
    tools=["coordination"],
    subagents=["security_auditor", "performance_specialist", "architect"],
)

options = BuildOptions(
    variant="verbose",
    include_subagents=True,  # Enable subagent section
)

output = builder.build(orchestrator, options)

# Output will include delegation instructions:
# ### Subagent: security_auditor
# Specializes in security_auditor tasks.
# Invoke by: `use_skill security_auditor` or request 'security_auditor subagent'
```

### Pattern 2: Workflow-Based Instructions

```python
# Agent with specific workflows
feature_builder = Agent(
    name="feature_builder",
    description="Implements new features",
    system_prompt="""You build features following a structured process.""",
    tools=["bash", "python"],
    workflows=["feature_implementation", "testing"],  # Will be formatted as workflow content
)

# Workflows appear as step-by-step instructions
# in the Workflows section
```

### Pattern 3: Skill Invocation Syntax

```python
# Agent with specialized skills
code_agent = Agent(
    name="code_expert",
    description="Writes and optimizes code",
    system_prompt="You are a code expert.",
    skills=["code_generation", "optimization", "refactoring"],
)

options = BuildOptions(include_skills=True)
output = builder.build(code_agent, options)

# Output includes Cline-specific invocation:
# ### Skill: code-generation
# Invoke by: `use_skill code_generation`
#
# ### Skill: optimization
# Invoke by: `use_skill optimization`
#
# ### Skill: refactoring
# Invoke by: `use_skill refactoring`
```

### Pattern 4: Tools with Descriptions

```python
# Build agent with detailed tools
tools_agent = Agent(
    name="system_admin",
    description="Manages system administration tasks",
    system_prompt="You are a system administrator.",
    tools=["bash", "grep", "awk", "sed"],
)

# Tools appear with placeholder descriptions
# - **bash**: [Tool description and usage]
# - **grep**: [Tool description and usage]
# etc.
```

### Pattern 5: Minimal Configuration

```python
# For simple rules with minimal requirements
simple_rules = Agent(
    name="simple",
    description="A simple agent",
    system_prompt="You are a simple agent.",
)

# Minimal variant - no extra sections
minimal_options = BuildOptions(
    variant="minimal",
    include_tools=False,
    include_skills=False,
    include_workflows=False,
    include_subagents=False,
)

output = builder.build(simple_rules, minimal_options)
# Output is just the header and system prompt
```

---

## Configuration Options

### BuildOptions for Cline

```python
@dataclass
class BuildOptions:
    variant: str = "minimal"          # minimal or verbose
    agent_name: str = ""              # Agent name
    include_subagents: bool = True    # Include subagents
    include_skills: bool = True       # Include skills
    include_workflows: bool = True    # Include workflows
    include_rules: bool = True        # Include rules
    include_tools: bool = True        # Include tools
```

### When to Use Each Option

| Option | Default | Use Case |
|--------|---------|----------|
| `variant="minimal"` | N/A | Simple rules without complexity |
| `variant="verbose"` | N/A | Comprehensive Cline configuration |
| `include_tools=True` | True | If agent uses specific tools |
| `include_skills=True` | True | If agent has specialized skills |
| `include_workflows=True` | True | If agent has step-by-step processes |
| `include_subagents=True` | True | If agent delegates to others |

### Typical Configurations

**Development Rules (Verbose):**
```python
BuildOptions(
    variant="verbose",
    include_tools=True,
    include_skills=True,
    include_workflows=True,
    include_subagents=True,
)
```

**Simple Rules (Minimal):**
```python
BuildOptions(
    variant="minimal",
    include_tools=False,
    include_skills=False,
    include_workflows=False,
    include_subagents=False,
)
```

---

## Common Patterns & Best Practices

### ✅ DO: Write Natural Prose Prompts

```python
# GOOD - Natural language system prompt
agent = Agent(
    name="reviewer",
    system_prompt="""You are an experienced code reviewer.

When reviewing code, consider:
1. Readability - Is the code clear?
2. Efficiency - Can it be optimized?
3. Safety - Are there security concerns?
4. Maintainability - Will others understand it?

Always be constructive in feedback.""",
)
```

```python
# BAD - Robotic, structured format
agent = Agent(
    name="reviewer",
    system_prompt="""ROLE: Code Reviewer
TASK: Review Code
REQUIREMENTS: 1. Readability 2. Efficiency 3. Safety""",
)
```

### ✅ DO: Use Cline Invocation Syntax

```python
# Cline expects use_skill syntax
agent = Agent(
    name="delegator",
    system_prompt="""When you need specialized help, invoke skills:

- Complex architecture → use_skill architect
- Performance issues → use_skill performance_profiler
- Security concerns → use_skill security_auditor""",
)
```

### ✅ DO: Organize Skills and Tools

```python
# GOOD - Grouped by purpose
writing_agent = Agent(
    name="writer",
    skills=[
        "markdown_formatting",    # Documentation
        "code_example_generation", # Code examples
        "technical_writing",      # Clear explanation
    ],
    tools=["bash"],
)
```

### ✅ DO: Include Clear Subagent Descriptions

```python
# GOOD - Clear specialist definitions
orchestrator = Agent(
    name="main",
    subagents=[
        "security_specialist",
        "performance_specialist",
        "architecture_specialist",
    ],
    system_prompt="""Delegate to specialists:

- Security concerns → security_specialist
- Performance optimization → performance_specialist
- Design decisions → architecture_specialist""",
)
```

### ✅ DO: Make Workflows Step-by-Step

```python
# GOOD - Clear workflow steps
agent = Agent(
    name="builder",
    system_prompt="""Follow this workflow:

1. Understand requirements
2. Design solution
3. Implement code
4. Write tests
5. Review and refine
6. Deliver""",
)
```

---

## Troubleshooting

### Issue: "Agent name is required"

**Problem:**
```python
agent = Agent(
    name="",  # Empty!
    description="Test",
    system_prompt="Test",
)
```

**Solution:**
```python
agent = Agent(
    name="meaningful_name",  # Use descriptive name
    description="Test",
    system_prompt="Test",
)
```

### Issue: "System prompt is required"

**Problem:**
```python
agent = Agent(
    name="agent",
    description="Test",
    system_prompt="",  # Empty!
)
```

**Solution:**
```python
agent = Agent(
    name="agent",
    description="Test",
    system_prompt="""You are a helpful assistant.

Your responsibilities:
- Help users effectively
- Provide accurate information
- Follow best practices""",
)
```

### Issue: Subagents not appearing

**Problem:**
```python
agent = Agent(
    name="main",
    subagents=["specialist1", "specialist2"],
)

options = BuildOptions(include_subagents=False)  # Disabled!
output = builder.build(agent, options)
```

**Solution:**
```python
options = BuildOptions(include_subagents=True)  # Enable
output = builder.build(agent, options)
```

### Issue: Skills section appears but not formatted correctly

**Problem:**
```python
agent = Agent(
    name="agent",
    skills=["skill1", "skill2"],  # Just list
    system_prompt="...",
)
```

**Solution:**
```python
# Skills content is loaded from component selector
# Ensure your skills are defined in the component system
# Cline will automatically format them with use_skill syntax
```

---

## API Reference

### ClineBuilder Class

#### Constructor

```python
def __init__(self, agents_dir: Path | str = "agents") -> None:
    """Initialize ClineBuilder.
    
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
| `get_tool_name` | `get_tool_name() -> str` | String | Returns "cline" |
| `supports_feature` | `supports_feature(feature: str) -> bool` | Bool | Checks feature support |

#### Main Build Method

```python
def build(self, agent: Agent, options: BuildOptions) -> str:
    """Build a Cline AI configuration file.
    
    Args:
        agent: The Agent IR model to build from
        options: Build configuration options
    
    Returns:
        String containing markdown content for .clinerules file
    
    Raises:
        BuilderValidationError: If the agent model is invalid
    """
```

#### Validation

```python
def validate(self, agent: Agent) -> list[str]:
    """Validate an Agent IR model for Cline.
    
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

### Example 1: Simple Cline Rules

```python
from src.builders.cline_builder import ClineBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent

def create_simple_cline_rules():
    """Create a simple .clinerules file."""
    
    builder = ClineBuilder()
    
    agent = Agent(
        name="helper",
        description="A helpful coding assistant",
        system_prompt="""You are a helpful coding assistant.

Your job is to:
- Help write clean, maintainable code
- Answer technical questions
- Suggest improvements
- Follow best practices""",
        tools=["bash", "python"],
    )
    
    options = BuildOptions(
        variant="minimal",
        include_tools=True,
        include_skills=False,
    )
    
    rules = builder.build(agent, options)
    
    # Save to .clinerules
    from pathlib import Path
    Path(".clinerules").write_text(rules)
    
    return rules

if __name__ == "__main__":
    rules = create_simple_cline_rules()
    print(rules)
```

### Example 2: Comprehensive Development Rules

```python
from src.builders.cline_builder import ClineBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent

def create_development_rules():
    """Create comprehensive development rules for Cline."""
    
    builder = ClineBuilder()
    
    agent = Agent(
        name="developer",
        description="Expert software developer",
        system_prompt="""You are an expert software developer.

Your responsibilities:
1. Write clean, maintainable code
2. Follow project conventions
3. Use appropriate tools and libraries
4. Write comprehensive tests
5. Document your code
6. Consider performance and security

When facing challenges:
- Break problems into smaller tasks
- Consider edge cases
- Optimize iteratively
- Test thoroughly""",
        tools=["bash", "python", "grep"],
        skills=["code_generation", "debugging", "optimization"],
        subagents=["architect", "tester"],
    )
    
    options = BuildOptions(
        variant="verbose",
        include_tools=True,
        include_skills=True,
        include_workflows=True,
        include_subagents=True,
    )
    
    rules = builder.build(agent, options)
    
    from pathlib import Path
    Path(".clinerules").write_text(rules)
    
    return rules

if __name__ == "__main__":
    rules = create_development_rules()
    print(rules)
```

### Example 3: Delegating Multi-Specialist System

```python
from src.builders.cline_builder import ClineBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent

def create_specialist_delegator():
    """Create rules for delegating to specialists."""
    
    builder = ClineBuilder()
    
    agent = Agent(
        name="orchestrator",
        description="Coordinates between specialized agents",
        system_prompt="""You coordinate between specialized agents.

Route work to appropriate specialists:

For architecture decisions → use_skill architect
For test writing → use_skill tester
For code review → use_skill reviewer
For security → use_skill security_auditor
For performance → use_skill performance_expert

Your role:
1. Understand the task
2. Route to appropriate specialist
3. Coordinate results
4. Ensure quality""",
        tools=["coordination", "logging"],
        subagents=[
            "architect",
            "tester",
            "reviewer",
            "security_auditor",
            "performance_expert",
        ],
    )
    
    options = BuildOptions(
        variant="verbose",
        include_subagents=True,
        include_tools=True,
    )
    
    rules = builder.build(agent, options)
    
    from pathlib import Path
    Path(".clinerules").write_text(rules)
    
    return rules

if __name__ == "__main__":
    rules = create_specialist_delegator()
    print(rules)
```

### Example 4: Domain-Specific Rules Generator

```python
from src.builders.cline_builder import ClineBuilder
from src.builders.base import BuildOptions
from src.ir.models import Agent
from pathlib import Path

def create_domain_rules(domain: str) -> str:
    """Create domain-specific Cline rules."""
    
    builder = ClineBuilder()
    
    domain_configs = {
        "frontend": {
            "name": "frontend_expert",
            "description": "Expert in frontend development",
            "system_prompt": """You are an expert frontend developer.

Focus on:
- React/Vue/Angular best practices
- User experience
- Performance optimization
- Responsive design
- Accessibility""",
            "tools": ["bash", "node"],
            "skills": ["ui_development", "performance"],
        },
        "backend": {
            "name": "backend_expert",
            "description": "Expert in backend development",
            "system_prompt": """You are an expert backend developer.

Focus on:
- API design
- Database optimization
- Scalability
- Security
- Error handling""",
            "tools": ["bash", "python"],
            "skills": ["api_design", "database_optimization"],
        },
    }
    
    config = domain_configs.get(domain)
    if not config:
        raise ValueError(f"Unknown domain: {domain}")
    
    agent = Agent(
        name=config["name"],
        description=config["description"],
        system_prompt=config["system_prompt"],
        tools=config["tools"],
        skills=config["skills"],
    )
    
    options = BuildOptions(
        variant="verbose",
        include_tools=True,
        include_skills=True,
    )
    
    return builder.build(agent, options)

if __name__ == "__main__":
    # Create rules for different domains
    domains = ["frontend", "backend"]
    
    for domain in domains:
        rules = create_domain_rules(domain)
        path = Path(f".clinerules-{domain}")
        path.write_text(rules)
        print(f"✓ Created {path}")
```

---

## Related Builders

For building other tools, see:
- [KiloBuilder Guide](./KILO_BUILDER_GUIDE.md) - For Kilo IDE
- [ClaudeBuilder Guide](./CLAUDE_BUILDER_GUIDE.md) - For Claude API
- [CopilotBuilder Guide](./COPILOT_BUILDER_GUIDE.md) - For GitHub Copilot
- [CursorBuilder Guide](./CURSOR_BUILDER_GUIDE.md) - For Cursor IDE

---

## Support & Resources

- **Source Code:** `src/builders/cline_builder.py`
- **Base Class:** `src/builders/base.py` (AbstractBuilder)
- **IR Models:** `src/ir/models.py` (Agent dataclass)
- **Examples:** `src/builders/examples_usage.py`
- **Cline Docs:** [cline.ai](https://cline.ai)

