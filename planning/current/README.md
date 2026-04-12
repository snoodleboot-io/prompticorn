# Current Planning

This directory contains active, in-scope planning documents.

## Contents

- **adrs/** - Architecture Decision Records for current work
- **execution-plans/** - Task breakdowns and execution plans for current phase
- **features/** - Feature specifications currently being implemented
- **prds/** - Product/project requirements for current scope

## Workflow

1. **Planning Phase**: Create PRDs and feature specs
2. **Decision Phase**: Document decisions in ADRs
3. **Execution Phase**: Create detailed execution plans
4. **Implementation**: Reference these docs during development
5. **Completion**: Move to `../complete/` when finished

## Guidelines

- Keep only active work here
- Move completed work to `../complete/`
- Archive or remove outdated planning docs
- Update execution plans as work progresses

## File Naming Conventions

- Execution plans: `PHASE{N}_{DESCRIPTION}.plan.md`
- ADRs: `{YYYYMMDD}_{decision_topic}.adr.md`
- Features: `{feature_name}.feature.md`
- PRDs: `{project_name}.prd.md`
