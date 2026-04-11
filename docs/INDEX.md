# Documentation Index

Promptosaurus documentation is organized by intent and purpose.

## Navigation by Purpose

### 📊 Overview & Dashboards
- **LIBRARY_INDEX.md** - Complete catalog of all agents, workflows, skills (start here)
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

### 📋 Planning & Execution
See: `docs/planning/`
- **current/** - Active phase plans
  - PHASE1_EXECUTION_GUIDE.plan.md
  - PHASE1_TASK_CHECKLIST.plan.md
  - PHASE2_OUTLINE.plan.md
  - PHASE2_TASK_CHECKLIST.plan.md
  - PHASE2_EXECUTION_STATUS.plan.md
- **finished/** - Completed phases

### ✅ Validation & Quality Reports
See: `docs/validation/`
- COVERAGE_REPORT.validation.md - Line/branch/mutation coverage
- MUTATION_TESTING_RESULTS.validation.md - Mutation test results
- PERFORMANCE_REPORT.validation.md - Performance benchmarks
- EXTRACTION_STATUS.validation.md - Content extraction validation
- VARIANT_REWRITE_CHECKLIST.validation.md - Variant quality checklist
- subagent-variant-audit-2026-04-10.validation.md - Audit report

### 🔬 Research & Investigation
See: `docs/research/`
- Investigation reports and research findings

### 🛠️ Builder Documentation
See: `docs/builders/`
- Builder implementation guides and patterns

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

