# Directory Structure

This document explains the organization of the Promptosaurus repository.

## Overall Structure

```
.
├── docs/                    # User-facing documentation
├── planning/                # Development planning (internal)
├── promptosaurus/           # Source code
├── tests/                   # Tests
├── examples/                # Example configurations
└── [root config files]
```

---

## docs/ - User-Facing Documentation

Contains documentation for users, developers, and operators using Promptosaurus.

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
│   ├── LANGUAGE_INTEGRATION_DESIGN.design.md
│   ├── VARIANT_DIFFERENTIATION_STRATEGY.design.md
│   └── WORKFLOW_HANDLING_ANALYSIS.design.md
│
├── architecture/            # Architecture documentation
│   └── ARCHITECTURE_OVERVIEW.md
│
├── components/              # Component documentation
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
│   ├── COMMON_USE_CASES.md
│   └── GETTING_STARTED.md
│
└── misc/                    # Images and assets
    ├── promptosaurs 1.png
    ├── promptosaurus2.png
    └── promptosaurus3-no-bg.png
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
- design/ - Architecture patterns, design decisions
- architecture/ - Detailed architecture documentation
- components/ - Component-level documentation

**Builders:**
- builders/ - Documentation for creating custom builders for IDEs

**User Guides:**
- user-guide/ - CLI reference, common use cases, getting started

**Assets:**
- misc/ - Images, logos, and diagrams

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

## promptosaurus/ - Source Code

```
promptosaurus/
├── agents/                  # Agent prompt files (25 primary agents)
│   ├── architect/
│   ├── ask/
│   ├── backend/
│   └── [22 more agents]
│
├── builders/                # Builder implementations
│   ├── base.py
│   ├── kilo_builder.py
│   ├── cline_builder.py
│   └── [more builders]
│
├── configurations/          # Configuration files
│   ├── agent_skill_mapping.yaml
│   └── [config files]
│
├── personas/                # Persona definitions
│   ├── personas.yaml
│   └── registry.py
│
├── agent_registry/          # Agent discovery and loading
│   ├── discovery.py
│   └── registry.py
│
└── cli.py                   # CLI entry point
```

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
└── conftest.py            # Shared test fixtures
```

---

## examples/ - Example Configurations

```
examples/
└── [example project configurations]
```

Example configurations showing how to use Promptosaurus in different scenarios.

---

## Root Configuration Files

```
.
├── pyproject.toml          # Python project configuration
├── README.md               # Repository README
├── .promptosaurus.yaml     # Promptosaurus configuration
└── [other config files]
```

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
- **For source code:** Navigate `promptosaurus/` directory

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-04-13 | Updated to reflect actual structure, removed deleted files |
| 1.0 | 2026-04-09 | Initial directory structure documentation |
