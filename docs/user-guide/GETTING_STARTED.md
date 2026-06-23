# Getting Started with prompticorn

## Quick 5-Minute Guide

This guide will help you get up and running with prompticorn in just 5 minutes.

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager
- One of the supported AI coding assistants:
  - Kilo Code (CLI or IDE)
  - Claude
  - Cline
  - Cursor
  - GitHub Copilot

### Installation

Install from pip:

```bash
pip install prompticorn
```

Or with uv (recommended):

```bash
uv pip install prompticorn
```

Verify installation:

```bash
prompticorn --help
```

You should see:
```
Usage: prompticorn [OPTIONS] COMMAND [ARGS]...

  prompticorn CLI — manage and validate your prompt configurations.

Options:
  --help  Show this message and exit.

Commands:
  init      Interactively initialize prompt configuration for your project.
  list      List all discovered agents, their subagents, and prompt variants.
  switch    Switch to a different AI assistant tool.
  swap      Swap active personas and regenerate configurations.
  update    Update configuration options interactively.
  validate  Validate agent registry structure and that all agents load...
```

---

## Basic Usage

### Step 1: Initialize Configuration

Run the interactive setup wizard:

```bash
prompticorn init
```

This will ask you a series of questions:

#### Question 1: Which AI assistant?

```
Which AI assistant would you like to configure?

Options:
  - Kilo CLI    (.opencode/rules/ with collapsed mode files)
  - Kilo IDE    (.kilo/agents/ individual agent files)
  - Claude      (.claude/ directory with Markdown agent files and CLAUDE.md)
  - Cline       (.clinerules file - concatenated rules)
  - Cursor      (.cursor/rules/ directory + .cursorrules)
  - Copilot     (.github/copilot-instructions.md)

Select: Kilo IDE
```

The default selection is **Kilo IDE**.

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
  - Backend Software Engineer
  - Frontend Software Engineer
  - Fullstack Software Engineer
  - Architect
  - QA / Tester
  - DevOps Engineer
  - Security Engineer
  - Product Manager
  - Data Engineer
  - Data Scientist
  - Technical Writer

Select: Fullstack Software Engineer, QA / Tester
```

*You can select multiple personas using Space, then Enter to confirm. Only
agents and workflows for the selected personas are generated.*

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

#### Question 6: Project settings

Finally, `init` asks a short set of language-agnostic project questions. These
populate the project-level fields of the generated core conventions. Every
question except the layout style offers a **Not specified** option that renders
as a clear placeholder if you skip it.

```
Which source-tree layout should the conventions document?
  - flat   (package/modules at the repo root — recommended default)
  - src    (sources nested under a src/ directory)

Which database does this project use?
  - Not specified / PostgreSQL / MySQL / SQLite / MongoDB / DynamoDB / Redis

Which ORM / query layer does this project use?
  - Not specified / SQLAlchemy / Prisma / Django ORM / GORM / TypeORM / Raw SQL

What error-handling pattern does this project follow?
  - Not specified / Exceptions / Result type / Error values / codes

Which commit message style does this project follow?
  - Not specified / Conventional Commits / Free-form

What soft PR size limit (lines changed) should agents target?
  - Not specified / 200 / 400 / 800

What is the primary deployment target?
  - Not specified / AWS Lambda / AWS ECS / Kubernetes / GKE / Vercel / Heroku / On-prem
```

The layout choice is saved as `project.layout_style` and the matching
per-language standard source tree is rendered into the core conventions.

#### Result

After answering all questions:

```
=========================================================
  Configuration saved!
=========================================================

  Config file: .prompticorn/.prompticorn.yaml

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

### Step 2: Inspect and Validate the Agent Registry

`list` and `validate` are discovery-based: they inspect the agents bundled with
prompticorn (the `agents/` registry), not your generated config or any flat
`prompts/` directory.

List all discovered agents, their subagents, and prompt variants:

```bash
prompticorn list
```

Output:
```
AGENT REGISTRY

architect  — System design, architecture planning, and technical decisions
  ✓  prompt.md
  subagents:
    architect-data-model
      ✓  minimal/prompt.md
      ✓  verbose/prompt.md

code  — Implement features and make direct code changes
  ✓  prompt.md
  subagents:
    code-implementation
      ✓  minimal/prompt.md
      ✓  verbose/prompt.md

... etc
```

Validate the registry structure (every agent has a base prompt and each subagent
has minimal/verbose variants that load cleanly):

```bash
prompticorn validate
```

Output:
```
▶ Validating agent registry...

  ✓ Registry valid: 25 agents, 82 subagents.
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

#### For Claude

Generates a `.claude/` directory with Markdown agent files plus a top-level
`CLAUDE.md`.

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
prompticorn switch
```

This will ask which tool you want to configure and regenerate the configs.

### Swap Active Personas

If you want to change which roles/personas are active:

```bash
prompticorn swap
```

Select different personas, and configs will be regenerated with only those persona's agents.

### Update Configuration Options

Update language, runtime, package manager, etc. without re-running `init`:

```bash
prompticorn update
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
prompticorn init

# Select:
#   - AI Tool: Kilo IDE
#   - Repo Type: single-language
#   - Variant: Minimal
#   - Personas: Fullstack Software Engineer, QA / Tester
#   - Language: Python
#   - Runtime: 3.12
#   - Package Manager: uv
#   - Testing Framework: pytest

# Result: Generated .kilo/agents/ with:
#   - code.md, test.md, review.md, refactor.md, document.md
#   (Plus universal: ask.md, debug.md, explain.md)

# Validate
prompticorn validate
```

### Workflow 2: Multi-Language Monorepo

```bash
# Initialize
prompticorn init

# Select:
#   - AI Tool: Cline
#   - Repo Type: multi-language-monorepo
#   - Variant: Verbose
#   - Personas: Fullstack Software Engineer, DevOps Engineer

# Then configure folders:
#   Folder 1: backend/api (Python 3.12, uv, pytest)
#   Folder 2: frontend (TypeScript 5.4, npm, vitest)

# Result: Generated .clinerules with:
#   - All agent configs for both personas
#   - Language-specific configurations for Python and TypeScript

# Validate
prompticorn validate
```

### Workflow 3: Switching Tools

```bash
# Started with Kilo, now want Cursor
prompticorn switch

# Select: Cursor
# Result: Generates .cursor/rules/ from existing .prompticorn.yaml

# Both .kilo/ and .cursor/ now exist
# You can use either tool
```

---

## Configuration File

The configuration lives at `.prompticorn/.prompticorn.yaml` and stores your
project configuration.

### Single-Language Example

```yaml
repository:
  type: "single_language"
spec:
  language: "python"
  runtime: "3.12"
  package_manager: "uv"
  test_framework: "pytest"
  linter: ["ruff"]
  formatter: ["ruff"]
  coverage: ...
variant: "minimal"
active_personas:
  - "fullstack_software_engineer"
  - "qa_tester"
ai_tool: "kilo-ide"
project:
  layout_style: "flat"        # or "src"
  database: "PostgreSQL"
  orm: "SQLAlchemy"
  error_handling: "Exceptions"
  commit_style: "Conventional Commits"
  pr_size: "400"
  deploy_target: "AWS Lambda"
```

### Multi-Language Monorepo Example

```yaml
repository:
  type: "multi_language_monorepo"
spec:
  - folder: "backend/api"
    type: "backend"
    subtype: "api"
    language: "python"
    runtime: "3.12"
    package_manager: "uv"
    test_framework: "pytest"
  - folder: "frontend"
    type: "frontend"
    subtype: "ui"
    language: "typescript"
    runtime: "5.4"
    package_manager: "npm"
    test_framework: "vitest"
variant: "minimal"
active_personas:
  - "fullstack_software_engineer"
  - "devops_engineer"
ai_tool: "cline"
project:
  layout_style: "flat"
```

---

## Persona-Based Filtering

prompticorn uses **personas** to filter which agents are generated, reducing cognitive load.

### Available Personas

| Persona | Description |
|---------|-------------|
| Backend Software Engineer | Backend development, APIs, microservices, and distributed systems |
| Frontend Software Engineer | Frontend development, UI/UX, and accessible web experiences |
| Fullstack Software Engineer | Full-stack development across frontend and backend |
| Architect | System design, architecture planning, and technical decisions |
| QA / Tester | Quality assurance, testing strategy, and test automation |
| DevOps Engineer | Infrastructure, deployment, operations, and CI/CD |
| Security Engineer | Security hardening, threat modeling, and compliance |
| Product Manager | Requirements, prioritization, and roadmap planning |
| Data Engineer | Data pipelines, data quality, and data infrastructure |
| Data Scientist | Machine learning, model development, and optimization |
| Technical Writer | Documentation and technical communication |

### Universal Agents (Always Available)

These agents are always generated regardless of personas:
- **ask** - Q&A and decision logs
- **debug** - Debugging assistance
- **explain** - Code explanations
- **plan** - Planning and task breakdowns
- **orchestrator** - Workflow coordination

---

## Troubleshooting

### Command not found: prompticorn

**Cause:** Not installed or not in PATH

**Solution:**
```bash
# Check if installed
pip show prompticorn

# If not installed
pip install prompticorn

# If installed but not in PATH, use:
python -m prompticorn.cli --help
```

### Configuration file not found

**Cause:** Haven't run `prompticorn init` yet

**Solution:**
```bash
prompticorn init
```

### No agents generated

**Cause:** No personas selected or persona filtering too restrictive

**Solution:**
- Select at least one persona during `init`
- Universal agents (ask, debug, explain) are always generated
- Run `prompticorn swap` to change persona selection

### YAML syntax error

**Cause:** Manually edited `.prompticorn/.prompticorn.yaml` with invalid syntax

**Solution:**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('.prompticorn/.prompticorn.yaml'))"

# Or delete and re-run init
rm .prompticorn/.prompticorn.yaml
prompticorn init
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
| `prompticorn init` | Initialize configuration (interactive) |
| `prompticorn list` | List all registered agents/modes |
| `prompticorn validate` | Validate configuration integrity |
| `prompticorn switch` | Switch to different AI tool |
| `prompticorn swap` | Swap active personas |
| `prompticorn update` | Update configuration options |

---

**Need help?** See [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) or file an issue on GitHub.
