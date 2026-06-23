# Directory Structure

This document explains the organization of the prompticorn repository.

## Overall Structure

```
.
├── docs/                    # User-facing documentation
├── planning/                # Development planning (internal)
├── prompticorn/           # Source code
├── tests/                   # Tests
├── examples/                # Example configurations
└── [root config files]
```

---

## docs/ - User-Facing Documentation

Contains documentation for users, developers, and operators using prompticorn.

```
docs/
├── README.md                # Documentation landing page
├── INDEX.md                 # Navigation guide
├── QUICKSTART.md            # 5-minute quick start
├── PERSONA_GUIDES.md        # Guides by role (dev, architect, QA)
├── PERSONAS.md              # Persona-based filtering system
├── LIBRARY_INDEX.md         # Complete catalog of agents/workflows/skills
├── RELATIONSHIPS_MATRIX.md  # Agent → subagent mappings
├── ARCHITECTURE.md          # System architecture overview
├── TEMPLATE_SYSTEM.md       # Template substitution system
├── TROUBLESHOOTING.md       # Common issues and solutions
├── DIAGRAMS_GUIDE.md        # Visual diagrams and flows
├── INTEGRATION_GUIDES.md    # Integration with IDEs and tools
├── INTERACTIVE_WALKTHROUGH.md
├── ADVANCED_CONFIGURATION.md
│
├── reference/               # How-to guides and reference materials
│   ├── DIRECTORY_STRUCTURE.reference.md  # This file
│   ├── GETTING_STARTED.reference.md
│   ├── API_REFERENCE.reference.md
│   └── TOOL_CONFIGURATION_EXAMPLES.reference.md
│
├── design/                  # Architecture and design decisions
│   ├── ADVANCED_PATTERNS.design.md
│   ├── AGENTIC_PERFORMANCE_ANALYSIS.md
│   ├── HYBRID_VARIANT_STRATEGY.md
│   ├── LANGUAGE_INTEGRATION_DESIGN.design.md
│   ├── MINIMAL_VS_VERBOSE_TOKENS.md
│   ├── VARIANT_DIFFERENTIATION_STRATEGY.design.md
│   └── WORKFLOW_HANDLING_ANALYSIS.design.md
│
├── components/              # Component-level documentation
│   ├── BUILDER_ARCHITECTURE.md
│   ├── IR_SYSTEM.md
│   ├── LOADER_PARSER.md
│   ├── PERSONA_FILTERING.md
│   ├── REGISTRY_SYSTEM.md
│   └── TEMPLATE_SUBSTITUTION.md
│
├── builders/                # Builder implementation guides
│   ├── README.builder.md
│   ├── BUILDER_API_REFERENCE.builder.md
│   ├── BUILDER_IMPLEMENTATION_GUIDE.builder.md
│   ├── INTEGRATION_GUIDE.builder.md
│   ├── KILO_BUILDER_GUIDE.builder.md
│   ├── CLINE_BUILDER_GUIDE.builder.md
│   ├── CURSOR_BUILDER_GUIDE.builder.md
│   ├── COPILOT_BUILDER_GUIDE.builder.md
│   └── CLAUDE_BUILDER_GUIDE.builder.md
│
├── user-guide/              # End-user guides
│   ├── CLI_REFERENCE.md
│   ├── CLAUDE_USAGE.md
│   ├── COMMON_USE_CASES.md
│   ├── GETTING_STARTED.md
│   └── PROJECT_SETTINGS.md
│
└── blog/                    # Long-form articles
    └── CHOOSING_THE_RIGHT_VARIANT.md
```

### Content Categories

**Landing & Navigation:**
- README.md - Entry point for all documentation
- INDEX.md - Navigation guide
- QUICKSTART.md - Get started in 5 minutes

**User Guides:**
- PERSONA_GUIDES.md - By role (architect, developer, QA engineer)
- LIBRARY_INDEX.md - Searchable catalog of all agents, workflows, skills
- PERSONAS.md - Understanding persona-based filtering

**Reference Materials:**
- reference/ - How-to guides, getting started, configuration examples
- RELATIONSHIPS_MATRIX.md - Understanding agent → subagent relationships

**Architecture & Design:**
- ARCHITECTURE.md - High-level system architecture
- design/ - Architecture patterns, design decisions, variant strategy
- components/ - Component-level documentation

**Builders:**
- builders/ - Documentation for creating custom builders for IDEs

**User Guides:**
- user-guide/ - CLI reference, Claude usage, common use cases, project settings

**Articles:**
- blog/ - Long-form articles (e.g. choosing the right variant)

---

## planning/ - Development Planning (INTERNAL)

Contains AI-generated and internal development planning. **NOT user-facing.**

```
planning/
├── current/                 # Active development plans
│   ├── adrs/               # Architecture Decision Records (in progress)
│   ├── execution-plans/    # Task breakdowns and execution plans
│   └── [planning docs]
│
├── complete/               # Finished work
│   └── [completed plans]
│
├── backlog/                # Future work and ideas
│   └── [backlog items]
│
└── research/               # Research and investigations
    └── [research notes]
```

### Purpose

The `planning/` directory is for internal development work:
- Architecture Decision Records (ADRs) - before finalization
- Execution plans and task breakdowns
- Research findings and investigations
- Backlog and future work

**Note:** This is NOT user-facing documentation. Users should refer to `docs/` for all documentation needs.

---

## prompticorn/ - Source Code

The bundled prompt library (agents, skills, workflows, conventions) lives
alongside the Python modules that discover and build configurations from it.

```
prompticorn/
├── __about__.py             # Single source of the (dynamic) version
├── __init__.py
├── cli.py                   # CLI entry point: init, list, validate, switch, swap, update
├── config_handler.py        # Read/write .prompticorn/.prompticorn.yaml
├── registry.py              # Component registry (e.g. .gitignore patterns)
├── source_layouts.py        # Resolve per-language source-tree layout (flat/src)
│
├── agents/                  # Agent prompt files (25 agents + core/)
│   ├── core/                # Shared conventions: conventions-<lang>.md (29 languages),
│   │                        #   system.md, session.md, etc.
│   ├── architect/
│   ├── ask/
│   ├── backend/
│   └── [22 more agents]     # each: prompt.md (+ minimal/verbose variants, subagents/)
│
├── skills/                  # Reusable skill definitions (~95 skills)
├── workflows/               # Workflow definitions (~100 workflows)
│
├── agent_registry/          # Live agent discovery and loading
│   ├── discovery.py         # RegistryDiscovery: scans the agents/ tree
│   ├── registry.py          # Registry: builds from discovery
│   └── errors.py
│
├── builders/                # Tool-specific builders (Kilo, Cline, Claude, Cursor, Copilot)
│   ├── base.py
│   ├── factory.py           # BuilderFactory
│   ├── kilo_builder.py
│   ├── cline_builder.py
│   ├── claude_builder.py
│   ├── cursor_builder.py
│   ├── copilot_builder.py
│   ├── convention_generator.py  # Populates conventions from the user's spec choices
│   └── template_handlers/
│
├── ir/                      # Intermediate Representation
│   ├── models/              # agent, skill, workflow, project, rules, tool
│   ├── parsers/
│   └── loaders/
│
├── configurations/          # YAML data
│   ├── languages.yaml       # Supported languages (drives LanguageRegistry)
│   ├── source_layouts.yaml  # Per-language flat/src source-tree layouts
│   ├── agent_skill_mapping.yaml
│   └── [more config files]
│
├── personas/                # Persona definitions (personas.yaml + registry.py)
│
├── questions/               # Interactive questions asked during init
│   ├── base/
│   ├── project/             # Project-level questions (database, ORM, layout, etc.)
│   ├── python/
│   └── [one package per supported language]
│
├── ui/                      # Terminal UI (input, commands, render, state, pipeline)
├── prompts/                 # Shared prompt assets
│   └── macros/              # Jinja2 macros (checklist, coverage_targets, error_handling, ...)
└── templates/               # Jinja2 templates (claude/)
```

### Supported AI tools

The builders generate configurations for five AI coding assistants: **Kilo**
(CLI and IDE), **Cline**, **Claude**, **Cursor**, and **Copilot**.

### Bundled library inventory

| Component | Location | Count |
|-----------|----------|-------|
| Agents | `prompticorn/agents/` (excluding `core/`) | 25 |
| Workflows | `prompticorn/workflows/` | ~100 |
| Skills | `prompticorn/skills/` | ~95 |
| Language conventions | `prompticorn/agents/core/conventions-*.md` | 29 |

---

## tests/ - Test Suite

```
tests/
├── unit/                    # Unit tests (fast, isolated)
│   ├── agents/             # Agent tests
│   ├── builders/           # Builder tests
│   ├── personas/           # Persona system tests
│   ├── registry/           # Registry tests
│   └── [more test directories]
│
├── integration/            # Integration tests (multi-component)
├── security/               # Security tests
├── slow/                   # Slow end-to-end builder tests (marked `slow`)
└── conftest.py             # Shared test fixtures
```

Tests run with `uv run pytest` (configured in `[tool.pytest.ini_options]`).
Markers (`slow`, `integration`, `security`, `unit`) let you select subsets, e.g.
`uv run pytest -m "not slow"`.

---

## examples/ - Example Configurations

```
examples/
└── [example project configurations]
```

Example configurations showing how to use prompticorn in different scenarios.

---

## Root Configuration Files

```
.
├── pyproject.toml          # Project metadata + tool config (ruff, pyright, pytest, mutmut)
├── uv.lock                 # Locked dependency versions (uv)
├── README.md               # Repository README
├── CONTRIBUTING.md         # Contributor guide
├── CHANGELOG.md            # Release notes
├── .pre-commit-config.yaml # Pre-commit hooks
├── .coveragerc             # Coverage configuration
└── .prompticorn/           # prompticorn's own config for this repo
    └── .prompticorn.yaml   # Stored config (written by `init`; default dir is .prompticorn/)
```

> **Versioning:** there is no version field to edit by hand. `pyproject.toml`
> declares `dynamic = ["version"]`, sourced from `prompticorn/__about__.py`
> (`0.0.0.dev0` for local installs) and injected by CI/CD at build time. See
> CONTRIBUTING.md → "Release Process" for the MAJOR.MINOR.PATCH scheme.

---

## File Naming Conventions

Intent is encoded in filename suffixes:

- `.design.md` - Architecture and design decisions
- `.reference.md` - Reference guides and how-to documentation
- `.builder.md` - Builder tool documentation
- `.plan.md` - Execution plans (planning/ directory only)
- `.research.md` - Research findings (planning/ directory only)

---

## Navigation

- **For users:** Start with `docs/README.md` or `docs/QUICKSTART.md`
- **For developers:** See `docs/builders/` for building custom integrations
- **For architecture:** See `docs/ARCHITECTURE.md` and `docs/design/`
- **For source code:** Navigate `prompticorn/` directory

---

## Revision History

These are revisions of *this document*, not product releases (the package itself
is versioned dynamically — see CONTRIBUTING.md → "Release Process").

| Revision | Date | Changes |
|----------|------|---------|
| 3 | 2026-06-23 | Refreshed source tree (skills/, workflows/, ir/, ui/, questions/, prompts/macros, agent_registry/, configurations/), library inventory, dynamic versioning notes, accurate docs/ and tests/ layout |
| 2 | 2026-04-13 | Updated to reflect actual structure, removed deleted files |
| 1 | 2026-04-09 | Initial directory structure documentation |
