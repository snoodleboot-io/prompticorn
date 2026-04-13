# Contributing to Promptosaurus

Thank you for your interest in contributing to Promptosaurus! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Project Structure](#project-structure)
- [Adding New Features](#adding-new-features)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [Getting Help](#getting-help)

---

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:
- Be respectful and considerate
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

---

## Getting Started

### Prerequisites

- **Python 3.10+** (3.12 recommended)
- **uv** for package management (recommended) or pip
- **Git** for version control
- **pyright** for type checking

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/promptosaurus.git
   cd promptosaurus
   ```

3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/snoodleboot-io/promptosaurus.git
   ```

### Install Development Environment

#### Option 1: Using uv (Recommended)

```bash
# Install uv if you haven't
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync --dev
```

#### Option 2: Using pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Verify Installation

```bash
# Check CLI works
promptosaurus --help

# Run tests
pytest

# Type checking
pyright

# Linting
ruff check .
```

If all commands succeed, you're ready to contribute!

---

## Development Workflow

### 1. Create a Feature Branch

```bash
# Update your fork
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feat/your-feature-name
```

### 2. Make Changes

- Write code following our [Code Style](#code-style)
- Add tests for new functionality
- Update documentation as needed
- Run tests and linting locally

### 3. Run Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit

# Integration tests
pytest tests/integration

# With coverage
pytest --cov=promptosaurus --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### 4. Type Checking

```bash
# Run pyright (strict mode)
pyright

# No errors allowed - fix all type issues
```

### 5. Linting and Formatting

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

### 6. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add new builder for XYZ"
```

**Commit message format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `refactor:` - Code refactoring
- `test:` - Adding/updating tests
- `chore:` - Maintenance tasks

### 7. Push and Create PR

```bash
# Push to your fork
git push origin feat/your-feature-name

# Create pull request on GitHub
```

---

## Project Structure

### Directory Layout

```
promptosaurus/
├── promptosaurus/          # Main package
│   ├── __init__.py
│   ├── cli.py             # CLI entry point
│   ├── config_handler.py  # Configuration management
│   ├── registry.py        # Legacy registry
│   │
│   ├── ir/                # Intermediate Representation
│   │   ├── models/        # Agent, Skill, Workflow models
│   │   ├── parsers/       # YAML, Markdown parsers
│   │   └── loaders/       # Component loaders
│   │
│   ├── agent_registry/    # Agent discovery and registry
│   │   ├── registry.py
│   │   └── discovery.py
│   │
│   ├── builders/          # Tool-specific builders
│   │   ├── base.py        # AbstractBuilder
│   │   ├── factory.py     # BuilderFactory
│   │   ├── kilo_builder.py
│   │   ├── cline_builder.py
│   │   ├── claude_builder.py
│   │   ├── cursor_builder.py
│   │   ├── copilot_builder.py
│   │   └── template_handlers/  # Template substitution
│   │
│   ├── personas/          # Persona-based filtering
│   │   └── registry.py
│   │
│   ├── ui/                # Terminal UI
│   │   ├── input/         # Input providers
│   │   ├── commands/      # UI commands
│   │   ├── render/        # Renderers
│   │   └── state/         # State management
│   │
│   ├── questions/         # Interactive questions
│   │   ├── base/
│   │   ├── python/
│   │   └── typescript/
│   │
│   └── agents/            # Bundled agent definitions
│       ├── code/
│       ├── test/
│       └── ...
│
├── tests/                 # Test suite
│   ├── unit/
│   ├── integration/
│   ├── security/
│   └── conftest.py
│
├── docs/                  # Documentation
│   ├── user-guide/
│   ├── reference/
│   ├── builders/
│   └── architecture/
│
├── pyproject.toml         # Project metadata
└── README.md              # Project overview
```

### Key Files

| File | Purpose |
|------|---------|
| `cli.py` | CLI commands (init, list, validate, etc.) |
| `config_handler.py` | Read/write `.promptosaurus.yaml` |
| `prompt_builder.py` | Main builder wrapper (Phase 2A) |
| `ir/models/agent.py` | Agent IR model (immutable Pydantic) |
| `agent_registry/discovery.py` | Auto-discover agents from filesystem |
| `builders/factory.py` | Builder factory pattern |
| `personas/registry.py` | Persona filtering logic |

---

## Adding New Features

### Adding a New Builder

Implement support for a new AI coding assistant.

#### Step 1: Create Builder Class

Create `promptosaurus/builders/mytool_builder.py`:

```python
"""Builder for MyTool AI assistant."""

from typing import Any
from promptosaurus.builders.base import AbstractBuilder, BuildOptions
from promptosaurus.ir.models.agent import Agent

class MyToolBuilder(AbstractBuilder):
    """Builder for MyTool configurations."""
    
    def get_tool_name(self) -> str:
        return "mytool"
    
    def get_output_format(self) -> str:
        return "markdown"  # or "json", "yaml"
    
    def build(self, agent: Agent, options: BuildOptions) -> str:
        """Build MyTool configuration from agent IR.
        
        Args:
            agent: Agent IR model
            options: Build options
            
        Returns:
            Formatted configuration string
        """
        output = []
        
        # Build system prompt
        output.append(f"# {agent.name}\n")
        output.append(agent.system_prompt)
        
        # Build skills section (if supported)
        if options.include_skills and agent.skills:
            output.append("\n## Skills\n")
            for skill in agent.skills:
                output.append(f"- {skill.name}: {skill.description}\n")
        
        # Build workflows section (if supported)
        if options.include_workflows and agent.workflows:
            output.append("\n## Workflows\n")
            for workflow in agent.workflows:
                output.append(f"- {workflow.name}\n")
        
        return "".join(output)
    
    def validate(self, agent: Agent) -> list[str]:
        """Validate agent compatibility with MyTool.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not agent.name:
            errors.append("Agent must have a name")
        
        if not agent.system_prompt:
            errors.append("Agent must have a system prompt")
        
        return errors
    
    def supports_feature(self, feature_name: str) -> bool:
        """Check if builder supports a feature."""
        supported = {"skills", "workflows"}
        return feature_name in supported
```

#### Step 2: Register Builder

In `promptosaurus/builders/factory.py`, add to `_register_default_builders()`:

```python
def _register_default_builders():
    factory.register("kilo", KiloBuilder)
    factory.register("cline", ClineBuilder)
    factory.register("claude", ClaudeBuilder)
    factory.register("cursor", CursorBuilder)
    factory.register("copilot", CopilotBuilder)
    factory.register("mytool", MyToolBuilder)  # Add this
```

#### Step 3: Add to CLI

In `promptosaurus/cli.py`, add to tool selection:

```python
ai_tool = select_option_with_explain(
    question="Which AI assistant would you like to configure?",
    options=["Kilo CLI", "Kilo IDE", "Cline", "Cursor", "Copilot", "MyTool"],  # Add "MyTool"
    explanations={
        # ... existing ...
        "MyTool": "MyTool - .mytool/config.md",
    },
    # ...
)
```

#### Step 4: Add Tests

Create `tests/unit/builders/test_mytool_builder.py`:

```python
"""Tests for MyToolBuilder."""

import pytest
from promptosaurus.builders.mytool_builder import MyToolBuilder
from promptosaurus.builders.base import BuildOptions
from promptosaurus.ir.models.agent import Agent

def test_mytool_builder_basic():
    """Test basic MyTool builder functionality."""
    agent = Agent(
        name="code",
        description="Code implementation",
        system_prompt="You are a code assistant.",
    )
    
    builder = MyToolBuilder()
    options = BuildOptions(variant="minimal")
    
    result = builder.build(agent, options)
    
    assert "# code" in result
    assert "You are a code assistant." in result

def test_mytool_builder_validation():
    """Test MyTool builder validation."""
    agent = Agent(
        name="",  # Invalid: empty name
        description="Test",
        system_prompt="Test",
    )
    
    builder = MyToolBuilder()
    errors = builder.validate(agent)
    
    assert len(errors) > 0
    assert "must have a name" in errors[0]
```

#### Step 5: Update Documentation

Add builder documentation to `docs/builders/MYTOOL_BUILDER_GUIDE.builder.md`.

#### Step 6: Test End-to-End

```bash
# Run all tests
pytest

# Type checking
pyright

# Try it manually
promptosaurus init
# Select "MyTool"
# Verify output files generated
```

---

### Adding a New Language

Add support for a new programming language.

#### Step 1: Create Question Modules

Create `promptosaurus/questions/mylang/`:

```
questions/mylang/
├── __init__.py
├── mylang_runtime_question.py
└── mylang_package_manager_question.py
```

**Example: `mylang_runtime_question.py`**

```python
"""MyLang runtime version question."""

from promptosaurus.questions.base.question import Question

class MyLangRuntimeQuestion(Question):
    """Ask for MyLang runtime version."""
    
    question_text = "Which MyLang runtime version?"
    explanation = "Select the MyLang version for your project."
    options = ["1.0", "1.1", "1.2", "2.0"]
    default = "2.0"
    config_key = "runtime"
```

#### Step 2: Register Language

In `promptosaurus/questions/language.py`:

```python
LANGUAGE_KEYS = {
    "python": "Python",
    "typescript": "TypeScript",
    "javascript": "JavaScript",
    "mylang": "MyLang",  # Add this
}
```

#### Step 3: Create Conventions File

Create `promptosaurus/configurations/core/core-conventions-mylang.md`:

```markdown
# Core Conventions MyLang

Language:        mylang
Runtime:         2.0
Package Manager: mylang-pkg
Linter:          mylang-lint
Formatter:       mylang-fmt
```

#### Step 4: Add Template Handlers

If needed, create language-specific template handlers in `promptosaurus/builders/template_handlers/`.

#### Step 5: Add Tests

Create `tests/unit/questions/test_mylang_questions.py`.

---

### Adding a New Persona

Define a new role for persona-based filtering.

#### Step 1: Edit `personas.yaml`

Edit `promptosaurus/personas/personas.yaml`:

```yaml
personas:
  # ... existing personas ...
  
  my_new_persona:
    display_name: "My New Role"
    description: "Description of what this role does"
    primary_agents:
      - "code"
      - "test"
    secondary_agents:
      - "review"
    workflows:
      - "feature"
      - "bugfix"
    skills:
      - "debugging-methodology"
      - "code-review-practices"
```

#### Step 2: Test Persona

```bash
# Re-run init
promptosaurus init

# Select "My New Role" persona
# Verify correct agents generated
```

#### Step 3: Document Persona

Add documentation to `docs/PERSONAS.md`.

---

### Adding a New Agent

Create a new agent for a specific task.

#### Step 1: Create Directory Structure

```bash
mkdir -p promptosaurus/agents/my-agent/minimal
mkdir -p promptosaurus/agents/my-agent/verbose
```

#### Step 2: Create Minimal Prompt

Create `promptosaurus/agents/my-agent/minimal/prompt.md`:

```markdown
---
name: my-agent
description: Brief description of agent purpose
mode: my-agent
---

# System Prompt

You are a specialized assistant for [specific task].

## Responsibilities

- Responsibility 1
- Responsibility 2

## Guidelines

- Guideline 1
- Guideline 2
```

#### Step 3: Create Verbose Prompt

Create `promptosaurus/agents/my-agent/verbose/prompt.md`:

```markdown
---
name: my-agent
description: Detailed description of agent purpose
mode: my-agent
---

# System Prompt

You are a specialized assistant for [specific task].

[More detailed explanation with examples]

## Responsibilities

- Responsibility 1: [Detailed explanation]
- Responsibility 2: [Detailed explanation]

## Guidelines

- Guideline 1: [With examples]
- Guideline 2: [With examples]

## Examples

### Example 1

[Show concrete example]

### Example 2

[Show another example]
```

#### Step 4: Add Optional Skills/Workflows

Create `promptosaurus/agents/my-agent/minimal/skills.md` (optional):

```markdown
# Skills

- skill1
- skill2
```

Create `promptosaurus/agents/my-agent/minimal/workflow.md` (optional):

```markdown
# Workflow

## Steps

1. Step 1
2. Step 2
3. Step 3
```

#### Step 5: Test Discovery

```bash
# Validate agent discovered
promptosaurus list

# Should show "my-agent" in output
```

---

## Testing Guidelines

### Test Structure

```
tests/
├── unit/              # Unit tests (fast, isolated)
├── integration/       # Integration tests (slower, realistic)
├── security/          # Security tests
└── conftest.py        # Pytest fixtures
```

### Writing Unit Tests

**Naming:** `test_{function_name}_{scenario}.py`

**Structure (AAA Pattern):**

```python
def test_agent_loader_loads_valid_agent():
    """Test that AgentLoader loads a valid agent correctly."""
    # Arrange
    agent_dir = Path("promptosaurus/agents/code/minimal")
    loader = ComponentLoader(agent_dir)
    
    # Act
    bundle = loader.load()
    
    # Assert
    assert bundle.prompt is not None
    assert "code" in bundle.prompt
```

### Coverage Expectations

- **Overall:** 90%+
- **Core modules:** 95%+ (ir/, builders/, registry/)
- **UI modules:** 80%+ (harder to test interactively)

### Running Specific Tests

```bash
# Single file
pytest tests/unit/test_config.py

# Single test
pytest tests/unit/test_config.py::test_config_loads

# By marker
pytest -m slow  # Slow tests only

# With verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Test Fixtures

Use fixtures for common setup:

```python
@pytest.fixture
def sample_agent():
    """Create a sample agent for testing."""
    return Agent(
        name="test-agent",
        description="Test agent",
        system_prompt="You are a test assistant.",
    )

def test_something(sample_agent):
    """Use the fixture."""
    assert sample_agent.name == "test-agent"
```

---

## Documentation Guidelines

### Docstring Format (Google Style)

```python
def my_function(param1: str, param2: int) -> bool:
    """Brief one-line description.
    
    Longer description explaining what this function does,
    when to use it, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param2 is negative
        KeyError: When param1 not found
        
    Examples:
        >>> my_function("test", 5)
        True
    """
    if param2 < 0:
        raise ValueError("param2 must be non-negative")
    return len(param1) > param2
```

### When to Update Documentation

Update docs when you:
- Add a new feature
- Change existing behavior
- Add/remove CLI commands
- Change configuration schema
- Add/remove builders

### Documentation Files

| File | Update When |
|------|-------------|
| `README.md` | Major features, installation changes |
| `docs/ARCHITECTURE.md` | Design changes, new components |
| `docs/user-guide/GETTING_STARTED.md` | CLI changes, workflow changes |
| `docs/ADVANCED_CONFIGURATION.md` | Config schema changes |
| `docs/builders/*.md` | Builder API changes |

---

## Code Style

### Python Conventions

Follow `.kilo/rules/conventions-python.md` exactly.

**Key rules:**
- Type hints on all public functions
- Use Pydantic for data models
- No `setattr`/`getattr` unless framework code
- All modules have `__init__.py`
- Use `ruff` for linting and formatting
- Use `pyright` in strict mode

### Type Hints Required

```python
# Good
def process_data(items: list[str], limit: int) -> dict[str, int]:
    ...

# Bad
def process_data(items, limit):
    ...
```

### Immutability for Models

```python
# Good (frozen Pydantic model)
class Agent(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    description: str

# Bad (mutable)
class Agent(BaseModel):
    name: str
    description: str
```

### Error Handling

```python
# Good (specific exception, context)
raise ValueError(f"Invalid language: {language}. Must be one of {VALID_LANGUAGES}")

# Bad (generic exception)
raise Exception("Error")
```

---

## Pull Request Process

### Before Submitting

Checklist:
- [ ] All tests pass locally (`pytest`)
- [ ] Type checking passes (`pyright`)
- [ ] Linting passes (`ruff check .`)
- [ ] Code formatted (`ruff format .`)
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] Branch name follows convention

### PR Template

```markdown
## Description

[What does this PR do?]

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

[How was this tested?]

## Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Type hints added
- [ ] Linting passes
- [ ] All tests pass
```

### Review Process

1. **Automated checks** - CI runs tests, linting, type checking
2. **Code review** - Maintainer reviews code quality, design
3. **Feedback** - Address review comments
4. **Approval** - Maintainer approves PR
5. **Merge** - Squash and merge to main

### CI/CD Checks

GitHub Actions runs:
- `pytest` - All tests
- `pyright` - Type checking
- `ruff check` - Linting
- Coverage report

All must pass before merge.

---

## Getting Help

### Where to Ask Questions

- **GitHub Discussions** - General questions, ideas
- **GitHub Issues** - Bug reports, feature requests
- **Pull Request Comments** - Code-specific questions

### Reporting Bugs

Include:
- Python version
- Promptosaurus version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/stack traces

### Requesting Features

Include:
- Use case description
- Why this feature is needed
- Proposed implementation (if you have one)
- Alternatives considered

---

## Release Process (Maintainers)

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release tag: `git tag v0.2.0`
4. Push tag: `git push --tags`
5. GitHub Actions builds and publishes to PyPI

---

Thank you for contributing to Promptosaurus! 🦖
