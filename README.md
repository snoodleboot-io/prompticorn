# prompticorn

**Version 0.1.0** - A unified, tool-agnostic prompt architecture for managing AI agent configurations across 5 coding assistants.

Define your agent once in a simple IR format, automatically generate outputs for:
- **Kilo** IDE (YAML + Markdown)
- **Cline** (Markdown with skill directives)
- **Claude** (Markdown `.claude/` directory)
- **Cursor** (Markdown rules)
- **GitHub Copilot** (GitHub instructions)

## Install

Install via pip:

```bash
pip install prompticorn
```

Or with uv:

```bash
uv add prompticorn
```

This installs the `prompticorn` CLI command.

## Quick Start

See [QUICKSTART.md](./docs/QUICKSTART.md) for a 5-minute guide.

## Key Features

- **Unified IR System** - Define agents once, generate for all tools
- **5 Production-Ready Builders** - Kilo, Cline, Claude, Cursor, Copilot
- **Minimal/Verbose Variants** - Save tokens by choosing variant at build time
- **Persona-Based Filtering** - Select your team\'s roles, get only relevant agents
- **Auto-Discovery Registry** - Zero-config agent registration
- **CLI Tool** - Interactive `prompticorn init` command
- **Backwards Compatible** - Existing configurations still work

## Commands Reference

| Command | Description |
|---------|-------------|
| `prompticorn init` | Interactively initialize prompt configuration for your project |
| `prompticorn list` | List all registered modes and their prompt files |
| `prompticorn switch` | Switch to a different AI assistant tool |
| `prompticorn swap` | Swap active personas and regenerate AI assistant configurations |
| `prompticorn update` | Update configuration options interactively |
| `prompticorn validate` | Check that all registered prompt files exist and no files are missing |

## Documentation

### User Guides
- **[QUICKSTART.md](./docs/QUICKSTART.md)** - Quick start guide
- **[PERSONAS.md](./docs/PERSONAS.md)** - Documentation on persona-based filtering
- **[GETTING_STARTED.md](./docs/user-guide/GETTING_STARTED.md)** - Detailed getting started guide

### Reference
- **[API_REFERENCE.reference.md](./docs/reference/API_REFERENCE.reference.md)** - API reference documentation
- **[BUILDER_API_REFERENCE.builder.md](./docs/builders/BUILDER_API_REFERENCE.builder.md)** - Builder API reference
- **[BUILDER_IMPLEMENTATION_GUIDE.builder.md](./docs/builders/BUILDER_IMPLEMENTATION_GUIDE.builder.md)** - Guide for implementing new builders
- **[ARCHITECTURE_OVERVIEW.md](./docs/architecture/ARCHITECTURE_OVERVIEW.md)** - System architecture overview
- **[INDEX.md](./docs/INDEX.md)** - Documentation navigation hub

### Workflow
- **Adding prompts**: Run `prompticorn init` to generate configurations, then edit files in generated directories (e.g., `.kilo/rules/`)
- **Updating prompts**: Edit source prompts, then re-run `prompticorn init` to regenerate

### Mode Reference
| Mode | Key | Purpose |
|------|-----|---------|  
| Architect | `architect` | Scaffold projects, task breakdowns, data models |
| Test | `test` | Coverage-first test writing |
| Refactor | `refactor` | Structural changes, behavior preserved |
| Document | `document` | Docstrings, READMEs, changelogs |
| Explain | `explain` | Code walkthroughs for onboarding |
| Migration | `migration` | Dependency upgrades, framework ports |
| Code | `code` | Feature implementation, boilerplate |
| Review | `review` | Code, performance, accessibility review |
| Debug | `debug` | Root cause, log analysis, rubber duck |
| Ask | `ask` | Q&A, decision logs |
| Security | `security` | Security review (code and infra) |
| Compliance | `compliance` | SOC 2, ISO 27001, GDPR, HIPAA, PCI-DSS |
| Orchestrator | `orchestrator` | CI/CD, DevOps, PR descriptions |

## Development

To contribute or develop locally:

```bash
# Clone the repository
git clone https://github.com/snoodleboot-io/prompticorn.git
cd prompticorn

# Install in development mode
pip install -e .

# Or with uv
uv pip install -e .

# Run tests
pytest -v

# Type checking
pyright
```
