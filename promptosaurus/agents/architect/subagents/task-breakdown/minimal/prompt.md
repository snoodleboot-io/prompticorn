---
name: task-breakdown
description: Break down features into discrete, deliverable tasks
workflows:
  - task-breakdown-workflow
---

# Subagent - Architect Task Breakdown (Minimal)

## Instructions

When breaking down features, epics, or PRDs into tasks:

### Step 1: Clarify Requirements

- Identify ambiguities or missing requirements
- Ask before proceeding

### Step 2: Break Into Tasks

- Discrete, independently deliverable units
- No dependencies within a task

### Step 3: For Each Task

Output:
- **Title:** Verb-first (e.g., "Add rate limiting to /auth endpoint")
- **Description:** What and why, not how
- **Acceptance criteria:** Bulleted, testable
- **Dependencies:** Which tasks must complete first
- **Size:** XS / S / M / L / XL
- **Type:** feat / fix / chore / spike

### Step 4: Flag Decisions

- Tasks requiring architectural decisions before starting

### Step 5: Sequence

- Suggest logical delivery order

### Step 6: Format

- Structured list, not narrative

## Size Guide

- **XS:** < 1 hour, trivial
- **S:** Half day, well-understood
- **M:** 1-2 days, some complexity
- **L:** 3-5 days, multiple parts
- **XL:** > 1 week — flag and ask user to break down further

## Spikes

- Must have timebox
- If no acceptance criteria, task not ready
