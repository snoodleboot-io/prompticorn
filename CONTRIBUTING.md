# Contributing to prompticorn

Thank you for your interest in contributing to prompticorn! This guide will help you get started.

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

- **Python 3.10+** (the project targets 3.10–3.14)
- **uv** for package management (recommended) or pip
- **Git** for version control
- **pyright** for type checking

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/prompticorn.git
   cd prompticorn
   ```

3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/snoodleboot-io/prompticorn.git
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

# Install the package in development mode
pip install -e .

# Install the dev tools (declared under [dependency-groups] in pyproject.toml)
pip install pytest pytest-cov ruff pyright pre-commit build mutmut
```

> **Note:** dev tooling lives in the PEP 735 `[dependency-groups]` table, which
> `uv sync --dev` installs automatically. Plain `pip` does not yet resolve that
> table, so install the dev tools explicitly (above) or, on a recent pip, with
> `pip install --group dev`.

### Verify Installation

```bash
# Check CLI works
uv run prompticorn --help

# Run tests
uv run pytest

# Type checking
uv run pyright

# Linting
uv run ruff check .
```

If all commands succeed, you're ready to contribute!

> **Tip:** Prefix tool invocations with `uv run` so they execute inside the
> project's managed environment. If you activated the virtualenv manually
> (`source .venv/bin/activate`), you can drop the `uv run` prefix.

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

Tests run with [pytest](https://docs.pytest.org/). Configuration lives in the
`[tool.pytest.ini_options]` table of `pyproject.toml` (test discovery, strict
markers, and the `slow`/`integration`/`security`/`unit` markers).

```bash
# All tests
uv run pytest

# Unit tests only
uv run pytest tests/unit

# Integration tests
uv run pytest tests/integration

# Skip the slow end-to-end builder tests
uv run pytest -m "not slow"

# Stop on first failure
uv run pytest -x
```

### 4. Coverage

Coverage is collected with [pytest-cov](https://pytest-cov.readthedocs.io/). The
project sits at roughly **85%** line coverage; new code should not regress it.

```bash
# Terminal summary
uv run pytest --cov=prompticorn --cov-report=term-missing

# HTML report
uv run pytest --cov=prompticorn --cov-report=html

# View coverage report
open htmlcov/index.html      # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html     # Windows
```

### 5. Mutation Testing

For changes to core logic, run [mutmut](https://mutmut.readthedocs.io/) to check
that the test suite actually catches injected faults. Mutation testing is
configured in the `[tool.mutmut]` table of `pyproject.toml` (it mutates
`prompticorn/`, runs against `tests/`, and uses a fast runner that skips the
`slow` tests with coverage disabled).

```bash
# Run mutation testing (slow over the whole tree)
uv run mutmut run

# Inspect surviving mutants
uv run mutmut results
```

Mutation runs over the full package are slow — when iterating on one module,
narrow `paths_to_mutate` in `[tool.mutmut]` to that path before running.

### 6. Type Checking

Type checking uses [pyright](https://github.com/microsoft/pyright). Its
configuration is in the `[tool.pyright]` table of `pyproject.toml`
(`typeCheckingMode = "standard"`, checking the `prompticorn` package and
excluding `tests`).

```bash
# Run pyright
uv run pyright

# Fix all reported type issues before opening a PR
```

### 7. Linting and Formatting

Both linting and formatting use [ruff](https://docs.astral.sh/ruff/), configured
in the `[tool.ruff]` tables of `pyproject.toml` (line length 100, target
`py310`; lint rules E/W/F/I/B/C4/UP; double-quote formatting).

```bash
# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

### 8. Commit Changes

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

### 9. Push and Create PR

```bash
# Push to your fork
git push origin feat/your-feature-name

# Create pull request on GitHub
```

---

## Project Structure

### Directory Layout

```
prompticorn/
├── prompticorn/             # Main package
│   ├── __about__.py         # Single source of the (dynamic) version
│   ├── __init__.py
│   ├── cli.py               # CLI entry point (init, list, validate, switch, swap, update)
│   ├── config_handler.py    # Read/write .prompticorn/.prompticorn.yaml
│   ├── registry.py          # Component registry (gitignore patterns, etc.)
│   ├── source_layouts.py    # Per-language source-tree layout resolution
│   │
│   ├── agents/              # Bundled agent definitions (25 agents + core/)
│   │   ├── core/            # Shared conventions (conventions-<lang>.md, system, session)
│   │   ├── code/
│   │   ├── test/
│   │   └── ...
│   │
│   ├── skills/             # ~95 reusable skill definitions
│   ├── workflows/          # ~100 workflow definitions
│   │
│   ├── agent_registry/      # Live agent discovery and registry
│   │   ├── discovery.py     # RegistryDiscovery: scans agents/ tree
│   │   ├── registry.py      # Registry: build from discovery
│   │   └── errors.py
│   │
│   ├── builders/            # Tool-specific builders (Kilo, Cline, Claude, Cursor, Copilot)
│   │   ├── base.py
│   │   ├── factory.py
│   │   ├── kilo_builder.py
│   │   ├── cline_builder.py
│   │   ├── claude_builder.py
│   │   ├── cursor_builder.py
│   │   ├── copilot_builder.py
│   │   ├── convention_generator.py  # Populates conventions from spec choices
│   │   └── template_handlers/
│   │
│   ├── ir/                  # Intermediate Representation
│   │   ├── models/          # agent, skill, workflow, project, rules, tool
│   │   ├── parsers/
│   │   └── loaders/
│   │
│   ├── configurations/      # YAML data (languages, mappings, source_layouts.yaml)
│   ├── personas/            # Persona definitions (personas.yaml + registry.py)
│   │
│   ├── questions/           # Interactive questions for init
│   │   ├── base/
│   │   ├── project/         # Project-level questions (db, ORM, layout, etc.)
│   │   ├── python/
│   │   └── ...              # one package per supported language
│   │
│   ├── ui/                  # Terminal UI (input, commands, render, state, pipeline)
│   ├── prompts/             # Shared prompt assets
│   │   └── macros/          # Jinja2 macros (checklist, coverage_targets, ...)
│   └── templates/           # Jinja2 templates (claude/)
│
├── tests/                   # Test suite
│   ├── unit/
│   ├── integration/
│   ├── security/
│   ├── slow/
│   └── conftest.py
│
├── docs/                    # Documentation
│   ├── user-guide/
│   ├── reference/
│   ├── builders/
│   └── architecture/
│
├── .github/                 # CI/CD (calculate_version.py, ci-cd.yml)
├── pyproject.toml           # Project metadata, tool config (ruff/pyright/pytest/mutmut)
└── README.md                # Project overview
```

### Key Files

| File | Purpose |
|------|---------|
| `__about__.py` | Single source of the package version (`0.0.0.dev0` locally; injected by CI) |
| `cli.py` | CLI commands (init, list, validate, switch, swap, update) |
| `config_handler.py` | Read/write `.prompticorn/.prompticorn.yaml` |
| `source_layouts.py` | Resolve per-language source-tree layout (flat/src) |
| `ir/models/agent.py` | Agent IR model (immutable Pydantic) |
| `agent_registry/discovery.py` | Auto-discover agents from the `agents/` tree |
| `builders/factory.py` | Builder factory pattern |
| `builders/convention_generator.py` | Populate conventions from the user's spec choices |
| `personas/registry.py` | Persona filtering logic |
| `configurations/source_layouts.yaml` | Per-language source-tree layout data |
| `.github/scripts/calculate_version.py` | CI version derivation (see [Release Process](#release-process-maintainers)) |

---

## Adding New Features

### Adding a New Builder

Implement support for a new AI coding assistant.

#### Step 1: Create Builder Class

Create `prompticorn/builders/mytool_builder.py`:

```python
"""Builder for MyTool AI assistant."""

from typing import Any
from prompticorn.builders.base import Builder, BuildOptions
from prompticorn.ir.models.agent import Agent

class MyToolBuilder(Builder):
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

Register your builder with the `BuilderFactory` (see
`prompticorn/builders/factory.py`) alongside the existing tools:

```python
BuilderFactory.register("kilo", KiloBuilder)
BuilderFactory.register("cline", ClineBuilder)
BuilderFactory.register("claude", ClaudeBuilder)
BuilderFactory.register("cursor", CursorBuilder)
BuilderFactory.register("copilot", CopilotBuilder)
BuilderFactory.register("mytool", MyToolBuilder)  # Add this
```

#### Step 3: Add to CLI

In `prompticorn/cli.py`, add to tool selection:

```python
ai_tool = select_option_with_explain(
    question="Which AI assistant would you like to configure?",
    options=["Kilo CLI", "Kilo IDE", "Claude", "Cline", "Cursor", "Copilot", "MyTool"],  # Add "MyTool"
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
from prompticorn.builders.mytool_builder import MyToolBuilder
from prompticorn.builders.base import BuildOptions
from prompticorn.ir.models.agent import Agent

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
uv run pytest

# Type checking
uv run pyright

# Try it manually
uv run prompticorn init
# Select "MyTool"
# Verify output files generated
```

---

### Adding a New Language

Add support for a new programming language.

#### Step 1: Create Question Modules

Create `prompticorn/questions/mylang/`:

```
questions/mylang/
├── __init__.py
├── mylang_runtime_question.py
└── mylang_package_manager_question.py
```

**Example: `mylang_runtime_question.py`**

```python
"""MyLang runtime version question."""

from prompticorn.questions.base.question import Question

class MyLangRuntimeQuestion(Question):
    """Ask for MyLang runtime version."""
    
    question_text = "Which MyLang runtime version?"
    explanation = "Select the MyLang version for your project."
    options = ["1.0", "1.1", "1.2", "2.0"]
    default = "2.0"
    config_key = "runtime"
```

#### Step 2: Register Language

Languages are discovered dynamically from
`prompticorn/configurations/languages.yaml`. Add your language to the
`supported_languages` list:

```yaml
supported_languages:
  - python
  - typescript
  - javascript
  - mylang  # Add this
```

`LanguageRegistry` (in `prompticorn/questions/language.py`) reads this file, so
no code change is required to register the language itself.

#### Step 3: Create Conventions File

Add the language convention to `prompticorn/agents/core/conventions-mylang.md`.
This file is the template the convention generator populates with the user's
spec choices (runtime, package manager, linter, formatter, coverage targets,
and the resolved source-tree layout) during `init`.

#### Step 4: Add Template Handlers

If needed, create language-specific template handlers in `prompticorn/builders/template_handlers/`.

#### Step 5: Add Tests

Create `tests/unit/questions/test_mylang_questions.py`.

---

### Adding a New Persona

Define a new role for persona-based filtering.

#### Step 1: Edit `personas.yaml`

Edit `prompticorn/personas/personas.yaml`:

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
uv run prompticorn init

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
mkdir -p prompticorn/agents/my-agent/minimal
mkdir -p prompticorn/agents/my-agent/verbose
```

#### Step 2: Create Minimal Prompt

Create `prompticorn/agents/my-agent/minimal/prompt.md`:

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

Create `prompticorn/agents/my-agent/verbose/prompt.md`:

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

Create `prompticorn/agents/my-agent/minimal/skills.md` (optional):

```markdown
# Skills

- skill1
- skill2
```

Create `prompticorn/agents/my-agent/minimal/workflow.md` (optional):

```markdown
# Workflow

## Steps

1. Step 1
2. Step 2
3. Step 3
```

#### Step 5: Test Discovery

```bash
# Validate the agent registry structure
uv run prompticorn validate

# List discovered agents, subagents, and prompt variants
uv run prompticorn list

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
├── slow/              # Slow end-to-end builder tests (marked `slow`)
└── conftest.py        # Pytest fixtures
```

### Writing Unit Tests

**Naming:** `test_{function_name}_{scenario}.py`

**Structure (AAA Pattern):**

```python
def test_agent_loader_loads_valid_agent():
    """Test that AgentLoader loads a valid agent correctly."""
    # Arrange
    agent_dir = Path("prompticorn/agents/code/minimal")
    loader = ComponentLoader(agent_dir)
    
    # Act
    bundle = loader.load()
    
    # Assert
    assert bundle.prompt is not None
    assert "code" in bundle.prompt
```

### Coverage Expectations

- **Overall:** the suite sits around **85%**; don't regress it.
- **Core modules** (`ir/`, `builders/`, `agent_registry/`): aim high — these
  carry the build logic and are the easiest to test thoroughly.
- **UI modules** are harder to exercise interactively; cover what you reasonably
  can.

For changes to core logic, also run mutation testing (`uv run mutmut run`) to
confirm the tests catch injected faults — see
[Mutation Testing](#5-mutation-testing).

### Running Specific Tests

```bash
# Single file
uv run pytest tests/unit/test_config.py

# Single test
uv run pytest tests/unit/test_config.py::test_config_loads

# By marker
uv run pytest -m slow            # Slow tests only
uv run pytest -m "not slow"      # Everything except slow tests

# With verbose output
uv run pytest -v

# Stop on first failure
uv run pytest -x
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

Follow the bundled Python convention at
`prompticorn/agents/core/conventions-python.md`.

**Key rules:**
- Type hints on all public functions
- Use Pydantic for data models
- No `setattr`/`getattr` unless framework code
- All modules have `__init__.py`
- Use `ruff` for linting and formatting
- Use `pyright` for type checking (configured as `standard` mode in
  `[tool.pyright]`)

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
- [ ] All tests pass locally (`uv run pytest`)
- [ ] Type checking passes (`uv run pyright`)
- [ ] Linting passes (`uv run ruff check .`)
- [ ] Code formatted (`uv run ruff format .`)
- [ ] Coverage not regressed (`uv run pytest --cov=prompticorn`)
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

GitHub Actions (`.github/workflows/ci-cd.yml`) runs:
- `pytest` - All tests
- `pyright` - Type checking
- `ruff check` - Linting
- Coverage report

All must pass before merge. The same workflow derives the package version and
publishes to TestPyPI (on PRs to `main`) and PyPI (on merge to `main`) — see
[Release Process](#release-process-maintainers).

---

## Getting Help

### Where to Ask Questions

- **GitHub Discussions** - General questions, ideas
- **GitHub Issues** - Bug reports, feature requests
- **Pull Request Comments** - Code-specific questions

### Reporting Bugs

Include:
- Python version
- prompticorn version (`uv run prompticorn --version`, or the installed PyPI version)
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

**There is no manual version bump.** The version is *dynamic* and derived by
CI/CD — do not edit a version string by hand.

### How versioning works

- `pyproject.toml` declares `dynamic = ["version"]` and sources the version from
  `prompticorn/__about__.py` via Hatch (`[tool.hatch.version]`).
- `prompticorn/__about__.py` holds only a dev placeholder (`0.0.0.dev0`). That is
  the version you get for local/editable installs — it is never hand-edited to a
  real release number.
- At build time, CI/CD computes the real version
  (`.github/scripts/calculate_version.py`, invoked from
  `.github/workflows/ci-cd.yml`) using the scheme **MAJOR.MINOR.PATCH**:
  - **MAJOR** — from the CI environment (`MAJOR_VERSION`).
  - **MINOR** — derived from PyPI release history (latest published MINOR for the
    current MAJOR, plus one).
  - **PATCH** — derived from the change set (the PR number for PR builds; a
    release `0` on merge to `main`).

### What that means for contributors

- Don't bump any version field in `pyproject.toml` or `__about__.py`.
- Don't create `vX.Y.Z` release tags by hand — the workflow handles publishing.
- Locally, `prompticorn --version` reporting `0.0.0.dev0` is expected.

### Releasing

1. Update `CHANGELOG.md`.
2. Open a PR to `main`. CI publishes a preview build to **TestPyPI**.
3. Merge to `main`. CI computes the release version and publishes to **PyPI**.

---

Thank you for contributing to prompticorn!
