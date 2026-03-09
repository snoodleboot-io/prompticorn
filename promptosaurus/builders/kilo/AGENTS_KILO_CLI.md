# Kilo Code Agents

This directory contains the agent instructions for Kilo Code (CLI format).

## Structure

- **`AGENTS.md`** (this file) — User guide for understanding the agents
- **`.opencode/rules/_base.md`** — Core behaviors, conventions, and session management (always loaded)
- **`.opencode/rules/{MODE}.md`** — Mode-specific behaviors for each agent

## Core Instructions

The `_base.md` file contains:
- Core system behaviors (from `core-system.md`)
- General conventions (from `core.md`)
- Session management (from `core-session.md`)
- Language-specific conventions (if configured)

**Important:** Always load `_base.md` first for any task, as it contains the foundational behaviors and conventions for this project.

## Available Agents

Custom agents are collapsed into individual `.opencode/rules/{MODE}.md` files:

| Mode | Purpose |
|------|---------|
| **test** | Write comprehensive tests with coverage-first approach |
| **refactor** | Improve code structure while preserving behavior |
| **document** | Generate documentation, READMEs, and changelogs |
| **explain** | Code walkthroughs and onboarding assistance |
| **migration** | Handle dependency upgrades and framework migrations |
| **review** | Code, performance, and accessibility reviews |
| **security** | Security reviews for code and infrastructure |
| **compliance** | SOC 2, ISO 27001, GDPR, HIPAA, PCI-DSS compliance |
| **enforcement** | Reviews code against established coding standards |
| **planning** | Develops PRDs and works with architects to create ARDs |

> **Note:** The architect, code, ask, debug, and orchestrator modes are built-in to Kilo and are not generated here.

## Usage

Switch between agents based on the task at hand. Each agent has specialized
behaviors and will suggest switching when appropriate.

## Configuration

The `opencode.json` file references these instructions:

```json
{
  "instructions": [
    "AGENTS.md",
    ".opencode/rules/_base.md",
    ".opencode/rules/{MODE}.md"
  ]
}
```

Replace `{MODE}` with the agent you want to use (architect, code, ask, etc.).
