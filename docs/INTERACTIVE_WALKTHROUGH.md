# Interactive Walkthroughs

Step-by-step guided walkthroughs for common Promptosaurus tasks.

## Table of Contents

- [First-Time Setup](#first-time-setup)
- [Adding a New Tool](#adding-a-new-tool)
- [Changing Team Personas](#changing-team-personas)
- [Multi-Language Monorepo Setup](#multi-language-monorepo-setup)
- [Troubleshooting Guide](#troubleshooting-guide)

---

## First-Time Setup

### Scenario
You're starting a new Python project and want to use Kilo Code IDE as your AI assistant.

### Duration
**5-10 minutes**

### Step 1: Install Promptosaurus

```bash
# Install the package
pip install promptosaurus

# Verify installation
promptosaurus --help
```

**Expected Output:**
```
Usage: promptosaurus [OPTIONS] COMMAND [ARGS]...

  Prompt library CLI — manage and validate your prompt configurations.

Options:
  --help  Show this message and exit.

Commands:
  init      Interactively initialize prompt configuration for your project.
  list      List all registered modes and their prompt files.
  switch    Switch to a different AI assistant tool.
  swap      Swap active personas and regenerate configurations.
  update    Update configuration options interactively.
  validate  Check that all registered prompt files exist...
```

**✓ If you see this, installation is successful!**

### Step 2: Run Interactive Setup

```bash
# Navigate to your project directory
cd my-python-project

# Start setup wizard
promptosaurus init
```

### Step 3: Question 1 - Select AI Tool

```
Which AI assistant would you like to configure?

Options:
  1) Kilo CLI      - Kilo Code (CLI) - .opencode/rules/
  2) Kilo IDE      - Kilo Code (IDE) - .kilo/agents/
  3) Claude        - Claude - .claude/ + CLAUDE.md
  4) Cline         - Cline - .clinerules file
  5) Cursor        - Cursor - .cursor/rules/
  6) Copilot       - GitHub Copilot - .github/copilot-instructions.md

Select (default: 2): 2
```

**Choice:** `2` (Kilo IDE)

**✓ Selected Kilo IDE**

### Step 4: Question 2 - Repository Type

```
What type of repository is this?

Options:
  1) single-language           - One language for entire project
  2) multi-language-monorepo   - Multiple languages in different folders

Select (default: 1): 1
```

**Choice:** `1` (single-language)

**✓ Selected single-language repository**

### Step 5: Question 3 - Prompt Variant

```
Which prompt variant would you like to use?

Options:
  1) Minimal    - Lightweight prompts, lower token costs
  2) Verbose    - Detailed prompts with more examples

Select (default: 1): 1
```

**Choice:** `1` (Minimal)

**✓ Selected Minimal variant**

### Step 6: Question 4 - Choose Personas

```
Which personas will be working on this codebase?

  1) Software Engineer
  2) QA/Tester
  3) DevOps Engineer
  4) Security Engineer
  5) Architect
  6) Data Engineer
  7) Data Scientist
  8) Technical Writer
  9) Product Manager

Controls: type number + space/comma to toggle (or wait 0.5s), ↑↓ navigate, Enter confirm, q quit
Current selection: Software Engineer, QA/Tester
```

**How to select:**
- Type a number then press **space** or **comma** to toggle that item (e.g. `1 ` toggles Software Engineer)
- For items 10+, type the full number then space/comma (e.g. `1`, `0`, space)
- Or type the number and wait **0.5 seconds** — it commits automatically
- Press **Enter** when done

**✓ Selected Software Engineer and QA/Tester**

### Step 7: Question 5 - Language Configuration

```
What is your primary programming language?

Options:
  1) Python
  2) TypeScript
  3) JavaScript
  4) Go
  5) Java
  6) Rust

Select (default: 1): 1
```

**Choice:** `1` (Python)

**✓ Selected Python**

### Step 8: Python-Specific Questions

```
What Python runtime version?
  1) 3.10
  2) 3.11
  3) 3.12
  4) 3.13
  5) 3.14

Select (default: 3): 3
```

**Choice:** `3` (Python 3.12)

**✓ Selected Python 3.12**

### Step 9: More Python Questions

```
What package manager?
  1) pip
  2) poetry
  3) uv

Select (default: 3): 3
```

**Choice:** `3` (uv)

**✓ Selected uv**

### Step 10: Testing Framework

```
What testing framework?
  1) pytest
  2) unittest

Select (default: 1): 1
```

**Choice:** `1` (pytest)

**✓ Selected pytest**

### Step 11: Verification

```
=========================================================
  Configuration saved!
=========================================================

  Config file: /Users/you/my-python-project/.promptosaurus/.promptosaurus.yaml

------------------------------------------------------------
  Generating AI assistant configurations (minimal)...
------------------------------------------------------------
  ✓ Created .kilo/agents/code.md
  ✓ Created .kilo/agents/test.md
  ✓ Created .kilo/agents/review.md
  ✓ Created .kilo/agents/refactor.md
  ✓ Created .kilo/agents/document.md
  ✓ Created .kilo/agents/ask.md
  ✓ Created .kilo/agents/debug.md
  ✓ Created .kilo/agents/explain.md

=========================================================
  Setup complete!
=========================================================
```

**✓ Setup successful!**

### Step 12: Verify Setup

```bash
# List all generated agents
promptosaurus list

# Should show agents grouped by role
```

**Expected:**
```
ALWAYS ON (all modes)
  ✓  ask.md
  ✓  debug.md
  ✓  explain.md

CODE MODE  [code]
  ✓  .kilo/agents/code.md

TEST MODE  [test]
  ✓  .kilo/agents/test.md
```

**✓ All agents configured!**

### Next Steps

1. **Open Kilo Code IDE**
   - `.kilo/agents/code.md` contains your code agent prompt
   - Kilo will auto-discover these agents

2. **Start Using**
   - Use `code` agent for implementation
   - Use `test` agent for test writing
   - Use `review` agent for code review

3. **Update Configuration Later**
   ```bash
   # Update settings without re-running init
   promptosaurus update
   ```

---

## Adding a New Tool

### Scenario
You've been using Kilo IDE, now you want to also use Cline.

### Duration
**2-3 minutes**

### Current State
```
.promptosaurus.yaml  (exists from previous setup)
.kilo/agents/        (all agents for Kilo)
```

### Step 1: Switch to Cline

```bash
# This is simple! Just run switch command
promptosaurus switch

# Or directly:
promptosaurus switch cline
```

### Step 2: Select Tool

```
Which AI assistant would you like to configure?

Options:
  1) Kilo CLI
  2) Kilo IDE
  3) Claude
  4) Cline
  5) Cursor
  6) Copilot

Select: 4
```

**Choice:** `3` (Cline)

**✓ Switched to Cline**

### Step 3: Verification

```
✓ Generating AI assistant configurations (minimal)...
✓ Created .clinerules

Setup complete!
```

### Result

Now you have BOTH:
- `.kilo/agents/` (Kilo Code IDE configs)
- `.clinerules` (Cline config)

You can use either tool with the same project configuration!

---

## Changing Team Personas

### Scenario
Your team added a DevOps engineer. You want to include DevOps-specific agents.

### Duration
**2-3 minutes**

### Current State
```
active_personas: ["software_engineer", "qa_tester"]
```

### Step 1: Swap Personas

```bash
promptosaurus swap
```

### Step 2: Select New Personas

```
Which personas will be working on this codebase?

Current: Software Engineer, QA/Tester

Available:
  [X] Software Engineer     (keep)
  [X] QA/Tester           (keep)
  [ ] DevOps Engineer     (add)
  [ ] Security Engineer
  [ ] Architect
  ...

Select (space to toggle, enter when done):
```

**Action:**
- Select DevOps Engineer with space
- Press enter when done

**✓ Selected new personas**

### Step 3: Regenerate

```
✓ Updating configuration...
✓ Regenerating agents for new personas...
✓ Personas updated!

New agents generated:
  ✓ deployment.md   (DevOps)
  ✓ ci-cd.md        (DevOps)
  ✓ monitoring.md   (DevOps)
```

### Result

Your config now includes DevOps agents alongside your existing agents!

---

## Multi-Language Monorepo Setup

### Scenario
You have a project with both Python backend and TypeScript frontend.

### Duration
**10-15 minutes**

### Step 1: Run Init

```bash
promptosaurus init
```

### Step 2-4: Select Tool, Repository Type, Variant

(Same as First-Time Setup, steps 1-3)

### Step 5: Choose Monorepo

```
What type of repository is this?

Options:
  1) single-language
  2) multi-language-monorepo

Select: 2
```

**Choice:** `2`

**✓ Selected multi-language-monorepo**

### Step 6: Configure Folder 1 - Backend

```
Would you like to add a folder?

Preset or Custom?
  1) backend - Backend preset
  2) frontend - Frontend preset
  3) custom - Custom path

Select: 1
```

**Choice:** `1` (Backend)

```
Which backend subtype?
  1) api - REST/GraphQL API server
  2) worker - Background worker
  3) library - Shared library
  4) cli - Command-line tool

Select: 1
```

**Choice:** `1` (api)

```
Folder path: backend/api
Language: python (default)
Runtime: 3.12 (default)
Package manager: uv (default)
Testing framework: pytest (default)

✓ Folder configured: backend/api
```

### Step 7: Configure Folder 2 - Frontend

```
Would you like to add another folder?
  1) Yes
  2) No

Select: 1
```

**Choice:** `1` (Yes)

```
Preset or Custom?
  1) backend
  2) frontend
  3) custom

Select: 2
```

**Choice:** `2` (Frontend)

```
Which frontend subtype?
  1) ui - Web application
  2) library - Frontend library
  3) e2e - End-to-end tests

Select: 1
```

**Choice:** `1` (ui)

```
Folder path: frontend
Language: typescript (default)
Runtime: 5.4 (default)
Package manager: npm (default)
Testing framework: vitest (default)

✓ Folder configured: frontend
```

### Step 8: Verify

```
=========================================================
  Configuration saved!
=========================================================

Generated configuration:
  backend/api (Python 3.12, uv)
  frontend (TypeScript 5.4, npm)

Setup complete!
```

### Result

Your `.promptosaurus.yaml`:
```yaml
spec:
  - folder: "backend/api"
    language: "python"
    runtime: "3.12"
    package_manager: "uv"
  
  - folder: "frontend"
    language: "typescript"
    runtime: "5.4"
    package_manager: "npm"
```

Agents are generated with language-specific prompts for each folder!

---

## Troubleshooting Guide

### Problem: "Configuration file not found"

```bash
$ promptosaurus list
Error: No configuration found. Run 'promptosaurus init' first.
```

**Solution:**
```bash
# Initialize configuration
promptosaurus init
```

---

### Problem: "Missing: .kilo/agents/code.md"

```bash
$ promptosaurus validate
✗ MISSING: .kilo/agents/code.md
```

**Solution:**
```bash
# Regenerate all configurations
promptosaurus init

# Or if you switched tools and need to regenerate
promptosaurus switch kilo-ide
```

---

### Problem: Agents not showing in tool

```
# List shows agents but they don't appear in Kilo/Cline
$ promptosaurus list
(Shows all agents)
```

**Solution:**
1. Check file locations are correct
2. Restart your AI tool
3. Validate configuration:
```bash
promptosaurus validate
```

---

## Next Steps

- [GETTING_STARTED.md](./user-guide/GETTING_STARTED.md) - Full guide
- [ADVANCED_CONFIGURATION.md](./ADVANCED_CONFIGURATION.md) - Power user features
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - More troubleshooting

