# Getting Started with Promptosaurus

## Quick 5-Minute Guide

This guide will help you get up and running with Promptosaurus in just 5 minutes.

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager
- One of the supported AI coding assistants:
  - Kilo Code (CLI or IDE)
  - Cline
  - Cursor
  - GitHub Copilot

### Installation

Install from pip:

```bash
pip install promptosaurus
```

Or with uv (recommended):

```bash
uv pip install promptosaurus
```

Verify installation:

```bash
promptosaurus --help
```

You should see:
```
Usage: promptosaurus [OPTIONS] COMMAND [ARGS]...

  Prompt library CLI — manage and validate your prompt configurations.

Options:
  --help  Show this message and exit.

Commands:
  init      Interactively initialize prompt configuration for your project.
  list      List all registered modes and their prompt files.
  switch    Switch to a different AI assistant tool.
  swap      Swap active personas and regenerate configurations.
  update    Update configuration options interactively.
  validate  Check that all registered prompt files exist and no files are...
```

---

## Basic Usage

### Step 1: Initialize Configuration

Run the interactive setup wizard:

```bash
promptosaurus init
```

This will ask you a series of questions:

#### Question 1: Which AI assistant?

```
Which AI assistant would you like to configure?

Options:
  - Kilo CLI    (.opencode/rules/ with collapsed mode files)
  - Kilo IDE    (.kilo/agents/ individual agent files)
  - Cline       (.clinerules file - concatenated rules)
  - Cursor      (.cursor/rules/ directory + .cursorrules)
  - Copilot     (.github/copilot-instructions.md)

Select: Kilo IDE
```

#### Question 2: Repository type?

```
What type of repository is this?

Options:
  - single-language           (One language for the entire project)
  - multi-language-monorepo   (Multiple languages in different folders)

Select: single-language
```

#### Question 3: Prompt variant?

```
Which prompt variant would you like to use?

Options:
  - Minimal   (Lightweight prompts for faster tokens and lower costs)
  - Verbose   (Detailed prompts with more examples and explanations)

Select: Minimal
```

#### Question 4: Which personas?

```
Which personas will be working on this codebase?

Options:
  - Software Engineer
  - QA/Tester
  - DevOps Engineer
  - Security Engineer
  - Architect
  - Data Engineer
  - Data Scientist
  - Technical Writer
  - Product Manager

Select: Software Engineer, QA/Tester
```

*You can select multiple personas using Space, then Enter to confirm.*

#### Question 5: Language configuration

If you selected **single-language**, you'll be asked:

```
What is your primary programming language?

Options:
  - Python
  - TypeScript
  - JavaScript
  - Go
  - Java
  - Rust

Select: Python
```

Then language-specific questions like:

```
What Python runtime version?
  - 3.10
  - 3.11
  - 3.12
  - 3.13
  - 3.14

What package manager?
  - pip
  - poetry
  - uv

What testing framework?
  - pytest
  - unittest

... etc
```

If you selected **multi-language-monorepo**, you'll configure each folder separately.

#### Result

After answering all questions:

```
=========================================================
  Configuration saved!
=========================================================

  Config file: /home/you/project/.promptosaurus.yaml

------------------------------------------------------------
  Generating AI assistant configurations (minimal)...
------------------------------------------------------------
  ✓ Created .kilo/agents/code.md
  ✓ Created .kilo/agents/test.md
  ✓ Created .kilo/agents/review.md
  ✓ Created .kilo/agents/refactor.md
  ✓ Created .kilo/agents/document.md
  ... (only agents for selected personas)

=========================================================
  Setup complete!
=========================================================
```

---

### Step 2: Verify Configuration

List all registered agents:

```bash
promptosaurus list
```

Output:
```
Registered modes and their files:

code:
  - .kilo/agents/code.md

test:
  - .kilo/agents/test.md

review:
  - .kilo/agents/review.md

... etc
```

Validate configuration:

```bash
promptosaurus validate
```

Output:
```
▶ Validating prompt registry...

  ✓ All good — no missing or orphaned files.
```

---

### Step 3: Use with Your AI Tool

The generated configuration files are ready to use with your selected AI tool.

#### For Kilo Code IDE

Files generated in `.kilo/agents/`:
- `code.md` - Code implementation agent
- `test.md` - Testing agent
- `review.md` - Code review agent
- `refactor.md` - Refactoring agent
- `document.md` - Documentation agent
- ... (only agents for your selected personas)

Kilo Code automatically discovers these files.

#### For Kilo Code CLI

Files generated in `.opencode/rules/`:
- Collapsed format with all modes in fewer files

#### For Cline

Single file generated: `.clinerules`

Contains all agent configurations concatenated.

#### For Cursor

Files generated in `.cursor/rules/`:
- Per-mode `.mdc` files
- Legacy `.cursorrules` file

#### For GitHub Copilot

File generated: `.github/copilot-instructions.md`

---

## Common Commands

### Switch to a Different AI Tool

If you want to generate configs for a different tool:

```bash
promptosaurus switch
```

This will ask which tool you want to configure and regenerate the configs.

### Swap Active Personas

If you want to change which roles/personas are active:

```bash
promptosaurus swap
```

Select different personas, and configs will be regenerated with only those persona's agents.

### Update Configuration Options

Update language, runtime, package manager, etc. without re-running `init`:

```bash
promptosaurus update
```

Interactive menu to change specific options:
- Language
- Runtime version
- Package manager
- Testing framework
- ... etc

---

## Example Workflows

### Workflow 1: Python Project with Testing

```bash
# Initialize
promptosaurus init

# Select:
#   - AI Tool: Kilo IDE
#   - Repo Type: single-language
#   - Variant: Minimal
#   - Personas: Software Engineer, QA/Tester
#   - Language: Python
#   - Runtime: 3.12
#   - Package Manager: uv
#   - Testing Framework: pytest

# Result: Generated .kilo/agents/ with:
#   - code.md, test.md, review.md, refactor.md, document.md
#   (Plus universal: ask.md, debug.md, explain.md)

# Validate
promptosaurus validate
```

### Workflow 2: Multi-Language Monorepo

```bash
# Initialize
promptosaurus init

# Select:
#   - AI Tool: Cline
#   - Repo Type: multi-language-monorepo
#   - Variant: Verbose
#   - Personas: Software Engineer, DevOps Engineer

# Then configure folders:
#   Folder 1: backend/api (Python 3.12, uv, pytest)
#   Folder 2: frontend (TypeScript 5.4, npm, vitest)

# Result: Generated .clinerules with:
#   - All agent configs for both personas
#   - Language-specific configurations for Python and TypeScript

# Validate
promptosaurus validate
```

### Workflow 3: Switching Tools

```bash
# Started with Kilo, now want Cursor
promptosaurus switch

# Select: Cursor
# Result: Generates .cursor/rules/ from existing .promptosaurus.yaml

# Both .kilo/ and .cursor/ now exist
# You can use either tool
```

---

## Configuration File

The `.promptosaurus.yaml` file stores your project configuration.

### Single-Language Example

```yaml
version: "1.0"
repository:
  type: "single-language"
spec:
  language: "python"
  runtime: "3.12"
  package_manager: "uv"
  testing_framework: "pytest"
  test_runner: "pytest"
  linter: ["ruff"]
  formatter: ["black"]
  coverage_tool: "pytest-cov"
variant: "minimal"
active_personas:
  - "software_engineer"
  - "qa_tester"
```

### Multi-Language Monorepo Example

```yaml
version: "1.0"
repository:
  type: "multi-language-monorepo"
spec:
  - folder: "backend/api"
    type: "backend"
    subtype: "api"
    language: "python"
    runtime: "3.12"
    package_manager: "uv"
    testing_framework: "pytest"
  - folder: "frontend"
    type: "frontend"
    subtype: "ui"
    language: "typescript"
    runtime: "5.4"
    package_manager: "npm"
    testing_framework: "vitest"
variant: "minimal"
active_personas:
  - "software_engineer"
  - "devops_engineer"
```

---

## Persona-Based Filtering

Promptosaurus uses **personas** to filter which agents are generated, reducing cognitive load.

### Available Personas

| Persona | Primary Agents | Description |
|---------|---------------|-------------|
| Software Engineer | code, test, refactor, review | Core development work |
| QA/Tester | test, review | Testing and quality assurance |
| DevOps Engineer | code, devops, observability, incident | Operations and infrastructure |
| Security Engineer | security, compliance | Security reviews and compliance |
| Architect | architect, backend, frontend, data | System design and architecture |
| Data Engineer | data-pipeline, etl | Data engineering workflows |
| Data Scientist | mlai, experiment | ML/AI and experimentation |
| Technical Writer | document, explain | Documentation and education |
| Product Manager | plan, roadmap | Product planning |

### Universal Agents (Always Available)

These agents are always generated regardless of personas:
- **ask** - Q&A and decision logs
- **debug** - Debugging assistance
- **explain** - Code explanations
- **plan** - Planning and task breakdowns
- **orchestrator** - Workflow coordination

---

## Troubleshooting

### Command not found: promptosaurus

**Cause:** Not installed or not in PATH

**Solution:**
```bash
# Check if installed
pip show promptosaurus

# If not installed
pip install promptosaurus

# If installed but not in PATH, use:
python -m promptosaurus.cli --help
```

### Configuration file not found

**Cause:** Haven't run `promptosaurus init` yet

**Solution:**
```bash
promptosaurus init
```

### No agents generated

**Cause:** No personas selected or persona filtering too restrictive

**Solution:**
- Select at least one persona during `init`
- Universal agents (ask, debug, explain) are always generated
- Run `promptosaurus swap` to change persona selection

### YAML syntax error

**Cause:** Manually edited `.promptosaurus.yaml` with invalid syntax

**Solution:**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('.promptosaurus.yaml'))"

# Or delete and re-run init
rm .promptosaurus.yaml
promptosaurus init
```

---

## Next Steps

- **Advanced Configuration:** See [ADVANCED_CONFIGURATION.md](../ADVANCED_CONFIGURATION.md)
- **Troubleshooting:** See [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- **Personas:** See [PERSONAS.md](../PERSONAS.md)
- **Architecture:** See [ARCHITECTURE.md](../ARCHITECTURE.md)
- **API Reference:** See [API_REFERENCE.reference.md](../reference/API_REFERENCE.reference.md)

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `promptosaurus init` | Initialize configuration (interactive) |
| `promptosaurus list` | List all registered agents/modes |
| `promptosaurus validate` | Validate configuration integrity |
| `promptosaurus switch` | Switch to different AI tool |
| `promptosaurus swap` | Swap active personas |
| `promptosaurus update` | Update configuration options |

---

**Need help?** See [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) or file an issue on GitHub.
