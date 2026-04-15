# Debugging Methodology

**Purpose:** Execute debugging-methodology workflow  
**Typical Duration:** Variable  
**Prerequisites:** None

## Overview

This workflow guides you through debugging-methodology.

## Step 1: Language Detection

**Detect the language** being used:

```bash
# Check file extensions in scope
# OR ask user if unclear
```

**Load the appropriate language convention:**

```
IF language = python:
    Read: .claude/conventions/languages/python.md
ELSE IF language = typescript:
    Read: .claude/conventions/languages/typescript.md
ELSE IF language = rust:
    Read: .claude/conventions/languages/rust.md
ELSE IF language = golang:
    Read: .claude/conventions/languages/golang.md
```

**Do NOT proceed until language convention is loaded.**

## Step 2: Example Step

Perform the task

**Actions:**
- Action 1
- Action 2



## Completion Criteria

- [ ] Task completed successfully
- [ ] All tests passing

