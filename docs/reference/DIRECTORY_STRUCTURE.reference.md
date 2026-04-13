# Directory Structure

This document explains the organization of the repository after the docs/planning/_temp restructuring.

## Overall Structure

```
.
├── docs/                    # User-facing documentation (PUBLISHED)
├── planning/                # Development planning (INTERNAL)
├── _temp/                   # Ephemeral working files (GITIGNORED)
├── promptosaurus/           # Source code
├── tests/                   # Tests
├── examples/                # Examples
└── [root config files]
```

---

## docs/ - User-Facing Documentation

Contains documentation meant for users, developers, and operators using Promptosaurus.

```
docs/
├── README.md                # Documentation landing page
├── INDEX.md                 # Navigation guide
├── QUICKSTART.md            # 5-minute quick start
├── PERSONA_GUIDES.md        # Guides by role (dev, architect, QA)
├── LIBRARY_INDEX.md         # Complete catalog of agents/workflows/skills
├── RELATIONSHIPS_MATRIX.md  # How agents relate to workflows and skills
│
├── TECHNICAL_DEBT.md        # Known issues and debt
├── TEST_CONVENTIONS.md      # Testing patterns and conventions
├── MAINTENANCE_WORKFLOW.md  # Operations and maintenance guide
├── QUALITY_METRICS.md       # Code quality and coverage metrics
│
├── reference/               # How-to guides and reference materials
│   ├── DIRECTORY_STRUCTURE.reference.md  # This file
│   ├── GETTING_STARTED.reference.md
│   ├── API_REFERENCE.reference.md
│   ├── MIGRATION_GUIDE.reference.md
│   └── TOOL_CONFIGURATION_EXAMPLES.reference.md
│
├── design/                  # Architecture and design decisions
├── decisions/               # Final approved architecture decision records
│   ├── ADVANCED_PATTERNS.design.md
│   ├── LANGUAGE_INTEGRATION_DESIGN.design.md
│   ├── VARIANT_DIFFERENTIATION_STRATEGY.design.md
│   └── WORKFLOW_HANDLING_ANALYSIS.design.md
│
│   └── [ADR files]
│
├── builders/                # Builder implementation and patterns
│   ├── BUILDER_API_REFERENCE.md
│   ├── BUILDER_IMPLEMENTATION_GUIDE.md
│   └── INTEGRATION_GUIDE.md
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

**Reference Materials:**
- reference/ - How-to guides, getting started, configuration examples
- RELATIONSHIPS_MATRIX.md - Understanding connections between components
- TECHNICAL_DEBT.md - Known issues and technical debt
- TEST_CONVENTIONS.md - Testing standards and patterns
- MAINTENANCE_WORKFLOW.md - Operations procedures

**Architecture & Design:**
- design/ - Architecture diagrams, design patterns, system design documents
- decisions/ - Approved architectural decision records (ADRs)

**Builders:**
- builders/ - Documentation for building custom builders

**Assets:**
- misc/ - Images, logos, and diagrams

---

## planning/ - Development Planning (INTERNAL)

Contains all AI-generated and user-added development planning. **NOT user-facing.**

```
planning/
├── README.md                # Explains planning directory
│
├── current/                 # Active, in-scope work
│   ├── README.md
│   ├── adrs/                # Architecture decisions for current work
│   │   └── README.md
│   ├── execution-plans/     # Task breakdowns and phase plans
│   │   └── README.md
│   ├── features/            # Feature specifications being implemented
│   │   └── README.md
│   ├── prds/                # Product requirements documents
│   │   └── README.md
│   ├── (internal planning files)
│   └── [other phase execution plans]
│
├── complete/                # Finished work and delivered phases
│   ├── README.md
│   ├── adrs/                # ADRs from completed phases
│   │   └── README.md
│   ├── execution-plans/     # Completed phase execution plans
│   │   └── README.md
│   ├── features/            # Specifications of shipped features
│   │   └── README.md
│   ├── prds/                # Completed project requirements
│   │   └── README.md
│   ├── (internal reference)
│
├── backlog/                 # Future work (not in current scope)
│   ├── README.md
│   ├── adrs/                # Exploratory ADRs for future work
│   │   └── README.md
│   ├── execution-plans/     # Rough execution plans for future phases
│   │   └── README.md
│   ├── features/            # Feature ideas and specifications
│   │   └── README.md
│   └── prds/                # Future project requirements
│       └── README.md
│
└── research/                # Research and investigation findings
    ├── README.md
    ├── AI_TOOL_CAPABILITY_MATRIX.research.md
    ├── EXECUTION_INFERENCE.research.md
    ├── EXECUTION_MODELS_KILO_VERIFIED.research.md
    ├── EXECUTION_MODELS.research.md
    ├── EXECUTION_MODELS_VERIFIED.research.md
    └── EXECUTION_RESEARCH.research.md
```

### Content Organization

**current/** - Active work in progress:
- ADRs (architecture decisions)
- Execution plans (task breakdowns)
- Features (specifications)
- PRDs (project requirements)

**complete/** - Finished phases:
- Historical ADRs
- Completed execution plans
- Shipped feature specifications
- Archived project requirements
- Phase deliverables (skills/workflows references)

**backlog/** - Future planning:
- Exploratory ADRs
- Rough execution plans
- Feature ideas
- Future project requirements

**research/** - Research documents:
- Tool evaluations
- Capability analysis
- Technology research
- Findings that inform planning

---

## _temp/ - Ephemeral Working Files

Contains temporary working files with no long-term value. **NOT committed to git.**

```
_temp/
├── .gitkeep               # Ensures directory exists
├── README.md              # Explains ephemeral nature
├── PHASE2_CLEANUP_NOTES.md
├── PHASE3_RELEASE_NOTES.md
└── validation/            # Test validation reports
    ├── README.md
    ├── COVERAGE_REPORT.validation.md
    ├── MUTATION_TESTING_RESULTS.validation.md
    ├── PERFORMANCE_REPORT.validation.md
    ├── EXTRACTION_STATUS.validation.md
    ├── PHASE2_FINAL_AUDIT.validation.md
    ├── VARIANT_REWRITE_CHECKLIST.validation.md
    └── subagent-variant-audit-2026-04-10.validation.md
```

### Contents

- Validation reports (generated, reviewed, then obsolete)
- Cleanup notes (relevant during work, not after)
- Release notes (working copies)
- Temporary analysis outputs
- Build artifacts

### Guidelines

- Delete files once work completes
- Archive important findings to `planning/research/`
- Keep directory lean—it's a workspace, not an archive

---

## promptosaurus/ - Source Code

Main Python package for Promptosaurus CLI.

```
promptosaurus/
├── __init__.py
├── cli.py                   # Command-line interface
├── builders/                # Builder implementations
├── agents/                  # Agent definitions
├── workflows/               # Workflow definitions
├── skills/                  # Skill definitions
├── registry.py              # Central registry
└── [other modules]
```

---

## tests/ - Test Suite

```
tests/
├── unit/                    # Unit tests
├── integration/             # Integration tests
└── [test files]
```

---

## Directory Lifecycle

### Document Lifecycle

1. **Research** → Start in `planning/research/`
2. **Design** → Document in `docs/design/`
3. **Planning** → Create PRD/ADR/Features in `planning/current/`
4. **Execution** → Execution plan in `planning/current/execution-plans/`
5. **Implementation** → Build based on planning
6. **Completion** → Move to `planning/complete/`
7. **Reference** → User-facing documentation in `docs/`

### File Movement Guidelines

**When to move to planning/complete/**
- Phase/feature work is finished
- All ADRs, execution plans, and features are done
- Ready to archive current phase

**When to move to planning/backlog/**
- Feature is deprioritized
- Deferred to future work
- No longer in current scope

**When to delete from _temp/**
- Validation complete
- Report reviewed
- No longer need for reference
- Can be regenerated if needed

**When to add to docs/**
- Information is final and stable
- Useful for ongoing reference
- Intended for users or developers
- Ready to potentially publish

---

## Key Principles

**docs/** is for:
- ✓ User-facing documentation
- ✓ Reference guides
- ✓ Final design and architecture
- ✗ Work in progress
- ✗ Phase-specific artifacts

**planning/** is for:
- ✓ Development planning
- ✓ Phase-specific work
- ✓ Internal decision-making
- ✗ User-facing content

**_temp/** is for:
- ✓ Ephemeral working files
- ✓ Generated reports (temporary)
- ✓ Scratch work
- ✗ Anything that needs to persist

---

## Maintenance

- **Weekly:** Archive completed _temp/ files to planning/
- **Monthly:** Move completed planning/current/ to planning/complete/
- **As needed:** Update docs/ with stable, final documentation
