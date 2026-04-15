# Kilo Code Agents

This directory contains the agent instructions and system configuration for your project.

## In-Scope Agents

This configuration includes the following 13 primary agent(s):

| Agent | Purpose |
|-------|---------|
| **refactor** | Improve code structure while preserving behavior |
| **code** | Implement features and make direct code changes |
| **migration** | Handle dependency upgrades and framework migrations |
| **review** | Code, performance, and accessibility reviews |
| **orchestrator** | Coordinate multi-step workflows and manage complex tasks |
| **test** | Write comprehensive tests with coverage-first approach |
| **performance** | Optimize application performance, identify bottlenecks, and implement benchmarking |
| **explain** | Code walkthroughs and onboarding assistance |
| **ask** | Answer questions and provide explanations |
| **plan** | Develops PRDs and works with architects to create ARDs |
| **enforcement** | Reviews code against established coding standards and creates change requests |
| **backend** | Design scalable backend systems, APIs, microservices, and distributed architectures |
| **debug** | Diagnose and fix bugs, issues, and errors |

## Structure

- **`AGENTS.md`** (this file) — User guide for understanding the agents in scope
- **`.kilo/rules/`** — Core behaviors and conventions (always loaded)
- **`.kilo/agents/`** — Agent definitions and subagents

## Core Instructions

The `.kilo/rules/` directory contains core files that are always loaded:
- `system.md` — Core system behaviors
- `conventions.md` — General conventions
- `session.md` — Session management
- `conventions-{language}.md` — Language-specific conventions (if configured)

**Important:** Always load the core files from `.kilo/rules/` for any task, as they contain the foundational behaviors and conventions for this project.

## Usage

Switch between agents based on the task at hand. Each agent has specialized behaviors and will suggest switching when appropriate.

## Configuration

The IDE extensions automatically load the appropriate agent instructions from the `.kilo/` directory based on the current mode selection.

For other tools (Claude, Cline, Cursor, Copilot), the agent instructions are adapted to that tool's format but maintain the same structure and purpose.
