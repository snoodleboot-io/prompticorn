# Quick Start Guide

Get up to speed with Promptosaurus in 5 minutes.

## What is Promptosaurus?

Promptosaurus is a comprehensive AI agent library with:
- **9 specialized agents** across different domains (data, DevOps, testing, backend, frontend, etc.)
- **49 workflows** for common development tasks
- **58 specialized skills** for domain-specific expertise
- **220+ test suite** validating all content
- **Production-ready** rules for Kilo, Cline, Cursor, and Copilot

## Pick Your Path

### I want to explore what's available
→ Start with **[LIBRARY_INDEX.md](./LIBRARY_INDEX.md)** (searchable catalog of all 180+ agents, workflows, skills)

### I want to use this in my AI tool right now
→ Follow **[GETTING_STARTED.reference.md](./reference/GETTING_STARTED.reference.md)** for step-by-step setup

### I want to understand the architecture
→ Read **[ADVANCED_PATTERNS.design.md](./design/ADVANCED_PATTERNS.design.md)** for design decisions

### I want to see test coverage & quality metrics

### I want to understand how components relate
→ Review **[RELATIONSHIPS_MATRIX.md](./RELATIONSHIPS_MATRIX.md)** for dependency mapping

## Key Concepts (60 seconds)

### Agents
Instructions for specialized AI assistants (data engineer, DevOps engineer, backend developer, etc.). Each agent has a clear purpose and defined responsibilities.

### Workflows
Step-by-step guides for common development tasks (error debugging, code refactoring, performance optimization, etc.). Workflows can be minimal (quick reference) or verbose (detailed instructions).

### Skills
Specialized knowledge domains that agents leverage (SQL optimization, Kubernetes debugging, React patterns, etc.). Skills provide focused expertise on narrow topics.

## Directory Map

```
promptosaurus/
├── agents/              # All agent definitions (25 agents, 82 subagents)
├── workflows/           # Task workflows (49 total, minimal/verbose variants)
├── skills/              # Specialized knowledge (58 total, minimal/verbose variants)
├── docs/
│   ├── LIBRARY_INDEX.md           # Complete searchable catalog ⭐
│   ├── RELATIONSHIPS_MATRIX.md    # Component dependency map
│   ├── reference/                 # How-to guides
│   ├── design/                    # Architecture decisions
│   ├── planning/                  # Execution roadmaps
│   └── research/                  # Investigation findings
└── tests/               # 1292 passing tests (98.3% coverage)
```

## Common Tasks

### Find an agent for a specific role
1. Open [LIBRARY_INDEX.md](./LIBRARY_INDEX.md)
2. Search for your role (e.g., "backend", "DevOps", "testing")
3. Get agent ID and path
4. Open `promptosaurus/agents/{agent-id}/` to read instructions

### Find a workflow for a task
1. Open [LIBRARY_INDEX.md](./LIBRARY_INDEX.md)
2. Search for your task (e.g., "refactor", "debug", "optimize")
3. Get workflow path
4. Read `minimal/workflow.md` for quick reference or `verbose/workflow.md` for detailed guide

### Set up Promptosaurus in your IDE
1. Read [TOOL_CONFIGURATION_EXAMPLES.reference.md](./reference/TOOL_CONFIGURATION_EXAMPLES.reference.md)
2. Choose your tool (Kilo, Cline, Cursor, Copilot)
3. Copy the appropriate rules to your project

### Understand content quality
3. See [RELATIONSHIPS_MATRIX.md](./RELATIONSHIPS_MATRIX.md) for dependencies

## What's Next?

- **5 min:** Browse [LIBRARY_INDEX.md](./LIBRARY_INDEX.md) to see what's available
- **15 min:** Read one agent instruction to understand the style
- **30 min:** Follow [GETTING_STARTED.reference.md](./reference/GETTING_STARTED.reference.md) to integrate into your tool
- **1 hour:** Explore workflows and skills for your domain

## Questions?

- **How do I use this?** → [GETTING_STARTED.reference.md](./reference/GETTING_STARTED.reference.md)
- **What can I do with it?** → [LIBRARY_INDEX.md](./LIBRARY_INDEX.md)
- **How does it work?** → [ADVANCED_PATTERNS.design.md](./design/ADVANCED_PATTERNS.design.md)

