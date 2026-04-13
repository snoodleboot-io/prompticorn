# Completed Planning

This directory contains planning artifacts from finished work.

## Purpose

Preserves historical context for:
- Understanding past decisions
- Reviewing what was delivered
- Learning from previous phases
- Onboarding new team members

## Contents

- **adrs/** - Architecture decisions from completed work
- **execution-plans/** - Execution plans from delivered phases
- **features/** - Specifications of implemented features
- **prds/** - Requirements documents from finished projects

## Usage

**READ-ONLY**: These are historical records.

Do not modify unless correcting documentation errors.
For new work, create files in `../current/` instead.

## Organization

Consider organizing by phase or release:
```
complete/
├── phase1/
├── phase2/
└── v1.0.0/
```

Or keep flat with clear naming:
```
complete/
├── execution-plans/PHASE1_EXECUTION.plan.md
├── execution-plans/PHASE2_EXECUTION.plan.md
└── adrs/20260301_database_choice.adr.md
```
