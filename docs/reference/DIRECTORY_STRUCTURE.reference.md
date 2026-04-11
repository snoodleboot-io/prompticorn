# Documentation Directory Structure

This document explains the organization of the `docs/` directory.

## Directory Structure

```
docs/
├── design/                          # Design & architecture documents
│   ├── ADVANCED_PATTERNS.md
│   ├── LANGUAGE_INTEGRATION_DESIGN.md
│   ├── VARIANT_DIFFERENTIATION_STRATEGY.md
│   └── WORKFLOW_HANDLING_ANALYSIS.md
│
├── research/                        # Research & exploration documents
│   ├── AI_TOOL_CAPABILITY_MATRIX.md
│   ├── EXECUTION_INFERENCE.md
│   ├── EXECUTION_MODELS*.md
│   └── EXECUTION_RESEARCH.md
│
├── planning/                        # Project planning documents
│   ├── current/                     # Active planning
│   │   ├── prds/                    # Product Requirements Documents
│   │   ├── adrs/                    # Architecture Decision Records
│   │   ├── features/                # Feature specifications
│   │   └── execution-plans/         # Active execution plans
│   │       ├── COVERAGE_GAP_ANALYSIS.md
│   │       └── PHASE1_EXECUTION_PLAN.md
│   │
│   ├── future/                      # Future planning
│   │   ├── prds/
│   │   ├── adrs/
│   │   ├── features/
│   │   └── execution-plans/
│   │
│   └── finished/                    # Completed planning
│       ├── prds/                    # Completed PRDs
│       │   └── PHASE2_UNIFIED_PROMPT_ARCHITECTURE.md
│       ├── adrs/                    # Completed ADRs
│       │   ├── PHASE2A_IR_MODELS_AND_BUILDERS.md
│       │   ├── PHASE2_REGISTRY_ARCHITECTURE.md
│       │   └── PHASE2_UNIFIED_ARCHITECTURE.md
│       ├── features/                # Completed features
│       │   ├── FEATURE_001_unified_prompt_architecture.md
│       │   ├── README.md
│       │   ├── ROADMAP.md
│       │   ├── stories/
│       │   └── tasks/
│       ├── execution-plans/         # Completed execution plans
│       │   └── [46 completed phase documents]
│       └── [archived exploration work]
│
├── audits/                          # Code audits & status reports
│   ├── COVERAGE_REPORT.md
│   ├── MUTATION_TESTING_RESULTS.md
│   ├── PERFORMANCE_REPORT.md
│   ├── EXTRACTION_STATUS.md
│   └── VARIANT_REWRITE_CHECKLIST.md
│
├── builders/                        # Builder implementation documentation
│   ├── BUILDER_API_REFERENCE.md
│   ├── BUILDER_IMPLEMENTATION_GUIDE.md
│   └── INTEGRATION_GUIDE.md
│
├── misc/                            # Images and miscellaneous assets
│   ├── promptosaurs 1.png
│   ├── promptosaurus2.png
│   └── promptosaurus3-no-bg.png
│
└── [Reference documentation]        # User-facing docs (in root)
    ├── API_REFERENCE.md             # User API reference
    ├── DIRECTORY_STRUCTURE.md       # This file
    ├── GETTING_STARTED.md           # Quick start guide
    ├── MIGRATION_GUIDE.md           # Migration instructions
    ├── README.md                    # Documentation index
    └── TOOL_CONFIGURATION_EXAMPLES.md  # Configuration examples
```

## Document Categories

### Design (`docs/design/`)
Architecture and design documents that explain system structure, patterns, and design decisions.

**Purpose:** Technical design documentation for contributors and maintainers.

**Examples:**
- System architecture designs
- Design pattern documentation
- Integration designs
- Differentiation strategies

### Research (`docs/research/`)
Research documents exploring new technologies, approaches, or capabilities.

**Purpose:** Background research and exploration that informs design decisions.

**Examples:**
- Tool capability comparisons
- Technology research
- Proof-of-concept findings
- Inference models

### Planning (`docs/planning/`)
All project planning artifacts organized by status (current, future, finished).

#### Current (`docs/planning/current/`)
**Active planning documents** for ongoing work.

- **prds/** - Active Product Requirements Documents
- **adrs/** - Active Architecture Decision Records
- **features/** - Active feature specifications
- **execution-plans/** - Current execution plans and gap analysis

#### Future (`docs/planning/future/`)
**Future planning documents** for planned but not yet started work.

Same subdirectories as current, but for future phases.

#### Finished (`docs/planning/finished/`)
**Completed planning documents** from past phases.

Contains all completed PRDs, ADRs, features, and execution plans.

### Audits (`docs/audits/`)
Code quality audits, coverage reports, and status tracking.

**Purpose:** Track code quality metrics and audit results.

**Examples:**
- Coverage reports
- Mutation testing results
- Performance reports
- Extraction status
- Variant rewrite checklists

### Builders (`docs/builders/`)
Builder implementation documentation for developers creating or extending builders.

**Purpose:** Technical documentation for builder developers and contributors.

**Examples:**
- Builder API reference
- Builder implementation guide
- Integration guide for Phase 2A IR models
- Custom builder examples

### Misc (`docs/misc/`)
Images, logos, and miscellaneous assets.

**Purpose:** Store non-documentation files referenced by documentation.

**Examples:**
- Project logos
- Diagrams and images
- Screenshots

### Reference Documentation (Root)
User-facing reference documentation kept in the root `docs/` directory for easy access.

**Purpose:** Primary documentation for end users and developers using promptosaurus.

**Examples:**
- API reference (user-facing)
- Getting started guide
- Migration guide
- Tool configuration examples
- Documentation index (README)

## Guidelines

### When to Add Documents

**Design:**
- Creating a new system architecture
- Documenting a design pattern or strategy
- Explaining integration approaches

**Research:**
- Exploring new tools or technologies
- Comparing alternatives
- Proof-of-concept findings

**Planning/Current:**
- Starting a new phase or feature
- Active execution plans
- Ongoing gap analysis

**Planning/Future:**
- Planning future phases
- Backlog items with detailed planning
- Future features that need PRDs/ADRs

**Planning/Finished:**
- Move current planning docs here when phase completes
- Keep for historical reference
- Archive old execution plans

**Audits:**
- Code quality reports
- Coverage analysis
- Status tracking documents

**Builders:**
- Builder API documentation
- Builder implementation guides
- Integration documentation for IR models
- Custom builder examples

**Misc:**
- Images and logos
- Diagrams referenced by docs
- Screenshots and assets

**Reference (Root):**
- User guides
- API documentation (user-facing)
- Migration guides
- Configuration examples

### Document Lifecycle

1. **Research** → Exploration in `docs/research/`
2. **Design** → Architecture in `docs/design/`
3. **Planning** → PRD/ADR/Features in `docs/planning/current/`
4. **Execution** → Execution plan in `docs/planning/current/execution-plans/`
5. **Completion** → Move all to `docs/planning/finished/`
6. **Audits** → Quality reports in `docs/audits/`

### Naming Conventions

- Use SCREAMING_SNAKE_CASE for all documentation files
- Prefix with phase/version when relevant: `PHASE1_EXECUTION_PLAN.md`
- Use descriptive names: `LANGUAGE_INTEGRATION_DESIGN.md` not `DESIGN_1.md`
- Include dates in audit reports: `COVERAGE_REPORT_20260410.md`

## Maintenance

- **Regularly review current/**: Move completed items to finished/
- **Archive old audits**: Keep only recent reports in audits/
- **Update README.md**: When adding major new reference docs
- **Clean up finished/**: Archive very old exploration work periodically
