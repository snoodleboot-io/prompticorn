# Documentation Index

Promptosaurus documentation is organized by intent and purpose.

## Getting Started (Pick Your Path)

### 🚀 Quick Start
- **QUICKSTART.md** - 5-minute overview (start here first)
- **PERSONA_GUIDES.md** - Find resources for your role (architect, developer, QA, etc.)
- **LIBRARY_INDEX.md** - Complete searchable catalog of 180+ agents, workflows, skills

## Navigation by Purpose

### 📊 Overview & Dashboards
- **QUALITY_METRICS.md** - Test coverage, validation results, quality gates
- **RELATIONSHIPS_MATRIX.md** - How agents, workflows, and skills relate to each other

### 📖 Getting Started & How-To Guides
See: `docs/reference/`
- GETTING_STARTED.reference.md
- API_REFERENCE.reference.md
- MIGRATION_GUIDE.reference.md
- TOOL_CONFIGURATION_EXAMPLES.reference.md
- DIRECTORY_STRUCTURE.reference.md

### 🏗️ Design Decisions & Architecture
See: `docs/design/`
- ADVANCED_PATTERNS.design.md
- LANGUAGE_INTEGRATION_DESIGN.design.md
- VARIANT_DIFFERENTIATION_STRATEGY.design.md
- WORKFLOW_HANDLING_ANALYSIS.design.md

### 🛠️ Builder Documentation
See: `docs/builders/`
- Builder implementation guides and patterns

---

## Development Planning (Internal)

For internal development planning, see: `../planning/`
- **current/** - Active phase plans and execution
- **complete/** - Finished phases and delivered features
- **backlog/** - Future work and ideas
- **research/** - Research findings and investigations

Note: Planning directory contains AI-generated and internal development artifacts. This documentation (docs/) is user-facing.

## File Naming Conventions

Intent is encoded in filename suffixes:
- `.design.md` - Architecture and design decisions
- `.plan.md` - Execution plans and checklists
- `.validation.md` - Test results and quality reports
- `.reference.md` - Reference guides and how-to documentation
- `.research.md` - Investigation and research findings
- `.builder.md` - Builder tool documentation

## Content Types

### In promptosaurus/
- `agents/**/*.prompt.md` - Agent instructions
- `workflows/**/minimal|verbose/workflow.md` - Workflow guides
- `skills/**/minimal|verbose/skill.md` - Specialized skills

