# Kilo Code Agents

This directory contains the agent instructions for Kilo Code (IDE format).

## Structure

- **`AGENTS.md`** (this file) — User guide for understanding the agents
- **`.kilocode/rules/`** — Core behaviors and conventions (always loaded)
- **`.kilocode/rules-{mode}/`** — Mode-specific behaviors for each agent

## Core Instructions

The `.kilocode/rules/` directory contains core files that are always loaded:
- `system.md` — Core system behaviors
- `conventions.md` — General conventions
- `session.md` — Session management
- `{language}.md` — Language-specific conventions (if configured)

**Important:** Always load the core files from `.kilocode/rules/` for any task, as they contain the foundational behaviors and conventions for this project.

## Available Agents

Each agent has its own directory under `.kilocode/rules-{mode}/`:

| Mode | Directory | Purpose |
|------|-----------|---------|
| **test** | `.kilocode/rules-test/` | Write comprehensive tests with coverage-first approach |
| **refactor** | `.kilocode/rules-refactor/` | Improve code structure while preserving behavior |
| **document** | `.kilocode/rules-document/` | Generate documentation, READMEs, and changelogs |
| **explain** | `.kilocode/rules-explain/` | Code walkthroughs and onboarding assistance |
| **migration** | `.kilocode/rules-migration/` | Handle dependency upgrades and framework migrations |
| **review** | `.kilocode/rules-review/` | Code, performance, and accessibility reviews |
| **security** | `.kilocode/rules-security/` | Security reviews for code and infrastructure |
| **compliance** | `.kilocode/rules-compliance/` | SOC 2, ISO 27001, GDPR, HIPAA, PCI-DSS compliance |
| **enforcement** | `.kilocode/rules-enforcement/` | Reviews code against established coding standards |
| **planning** | `.kilocode/rules-planning/` | Develops PRDs and works with architects to create ARDs |

> **Note:** The architect, code, ask, debug, and orchestrator modes are built-in to Kilo and are not generated here.

## Usage

Switch between agents based on the task at hand. Each agent has specialized
behaviors and will suggest switching when appropriate.

## Configuration

The KiloCode IDE extensions automatically load the appropriate mode instructions
from the `.kilocode/` directory based on the current mode selection.
