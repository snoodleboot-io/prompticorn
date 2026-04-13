---
name: "strategy"
description: Streamlined strategy planning process
languages: [all]
subagents: [planning/strategy, architect/scaffold]
steps:
  - Read target files and imports
  - Identify code smells
  - Define interface constraints
  - Propose refactoring approach
  - Flag decision points
  - Estimate scope and effort
  - Get confirmation
---

## Strategy Planning Workflow

### Step 1: Read target files and imports
Read the file(s) being refactored and all files they import to understand context.

### Step 2: Identify code smells
Pick smells from standard list or name custom ones affecting the code.

### Step 3: Define interface constraints
State which parts of the observable interface must be preserved.

### Step 4: Propose refactoring approach
Describe the specific refactoring moves you will make with rationale.

### Step 5: Flag decision points
Identify steps requiring judgment calls or assumptions.

### Step 6: Estimate scope and effort
Estimate file count, complexity, and whether it can be done incrementally.

### Step 7: Get confirmation
Wait for user approval before proceeding with implementation.
