---
name: "task-breakdown"
description: "Break features and epics into implementable tasks"
version: "1.0"
languages: ["agile", "project-management"]
subagents: ["architect", "orchestrator"]
---

# Task Breakdown Workflow (Minimal)

## Purpose
Transform features, epics, or requirements into discrete, independently deliverable tasks with clear acceptance criteria and dependencies.

## Steps

### 1. Clarify Requirements
- Identify ambiguities or missing requirements
- Ask clarifying questions before proceeding
- Confirm scope boundaries (what's included, what's not)
- Understand success criteria

### 2. Break Work into Tasks
- Decompose feature into discrete, independently testable units
- Each task should deliver value or enable next task
- Tasks should be completable in 0.5-3 days
- Avoid tasks that are too large (>3 days) or too small (<2 hours)

### 3. Define Each Task
- **Title:** Verb-first (e.g., "Add rate limiting to /auth endpoint")
- **Description:** What and why, not how
- **Acceptance criteria:** Bulleted, testable statements
- **Dependencies:** Which tasks must complete first
- **Size estimate:** XS / S / M / L / XL (or hours/days)
- **Type:** feat / fix / chore / spike

### 4. Identify Architectural Decisions
- Flag tasks requiring design decisions before implementation
- Mark tasks as "spike" if outcome uncertain
- Note tasks that need stakeholder approval
- Identify tasks with high technical risk

### 5. Sequence Tasks
- Order tasks by dependencies (what must happen first)
- Identify tasks that can be parallelized
- Suggest logical delivery sequence
- Group related tasks into milestones

### 6. Output Structured Task List
- Present as numbered list or table
- Include all metadata (size, type, dependencies)
- Highlight critical path tasks
- Note any assumptions or unknowns
