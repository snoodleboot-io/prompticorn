# Claude Configuration Guide

**Last Updated:** 2026-04-14  
**Version:** 1.0

---

## Overview

Promptosaurus generates a clean, organized `.claude/` directory structure for Claude AI assistant usage. The system uses lazy loading, where Claude only loads what it needs when it needs it.

---

## Quick Start

### 1. Initialize for Claude

```bash
cd your-project
promptosaurus init
# Select "claude" when prompted
```

This creates:
- `CLAUDE.md` - Routing file (read this first)
- `.claude/` - All Claude artifacts

### 2. What Gets Generated

```
your-project/
├── CLAUDE.md                     # Start here - routing & instructions
└── .claude/
    ├── agents/                   # Primary agents (14 for software_engineer)
    │   ├── code-agent.md
    │   ├── debug-agent.md
    │   ├── architect-agent.md
    │   └── ...
    ├── subagents/                # Specialized helpers (35+)
    │   ├── code-reviewer.md
    │   ├── rubber-duck.md
    │   └── ...
    ├── workflows/                # Multi-step processes
    │   ├── feature-implementation.md
    │   ├── code-review.md
    │   └── ...
    ├── conventions/              # Rules and standards
    │   ├── core/
    │   │   └── general.md        # System + conventions + session
    │   └── languages/
    │       ├── python.md
    │       ├── typescript.md
    │       └── ... (30 languages)
    └── skills/                   # Reusable capabilities
        ├── feature-planning/
        └── ...
```

---

## How It Works

### Lazy Loading Pattern

Claude follows a 3-step loading process:

**Step 1: Read CLAUDE.md** (3.7KB)
```
Read: CLAUDE.md
```
This gives Claude:
- Agent registry (which agents are available)
- Routing rules (how to pick the right agent)
- Core instructions

**Step 2: Load Core Conventions** (~10KB)
```
Read: .claude/conventions/core/general.md
```
This gives Claude:
- System startup checklist
- Feature branch conventions
- Session management
- Core development rules

**Step 3: Load One Agent** (~2KB)
```
Read: .claude/agents/code-agent.md
```
The agent file tells Claude what to load next:
- Which workflow to follow
- Which language conventions to load
- Which subagents are available
- Which skills to use

**Step 4: Load Resources As Needed**
The workflow instructs Claude to load:
- Language convention (e.g., python.md) - ~8KB
- Subagents (when needed) - ~1KB each
- Skills (when needed) - ~2KB each

**Total Initial Load:** ~19KB vs 728KB in old format (97% reduction)

---

## CLAUDE.md Explained

The CLAUDE.md file is your routing table. Here's what it contains:

### 1. Agent Registry

Lists all available agents:

```markdown
| Agent | Purpose | File Path |
|-------|---------|-----------|
| code-agent | Write, edit, refactor code | .claude/agents/code-agent.md |
| debug-agent | Diagnose and fix bugs | .claude/agents/debug-agent.md |
| ...
```

### 2. Routing Rules

Matches your request to the right agent:

```markdown
### Code Implementation
- Keywords: "write", "implement", "create", "build"
- Agent: code-agent

### Bug Fixing
- Keywords: "debug", "fix bug", "error", "failing"
- Agent: debug-agent
```

### 3. Instructions

Tells Claude how to:
1. Load core conventions
2. Analyze your request
3. Pick the right agent
4. Follow agent's instructions
5. Load resources on-demand

---

## Agent Files Explained

Each agent file (e.g., `code-agent.md`) contains:

### 1. Purpose & When to Use
```markdown
**Purpose:** Write, edit, and refactor code
**When to Use:** Implementing features, fixing bugs, refactoring code
```

### 2. Role Description
What this agent does and how it behaves.

### 3. Workflow Reference
```markdown
**Read and follow this workflow file:**
.claude/workflows/feature-implementation.md
```

### 4. Subagents Table
Lists specialized helpers this agent can delegate to:

```markdown
| Subagent | Purpose | File Path | When to Use |
|----------|---------|-----------|-------------|
| code-reviewer | Review code quality | .claude/subagents/code-reviewer.md | After implementation |
```

### 5. Skills Table
Lists reusable capabilities:

```markdown
| Skill | Purpose | File Path | When to Use |
|-------|---------|-----------|-------------|
| feature-planning | Plan features | .claude/skills/feature-planning/SKILL.md | Before complex features |
```

### 6. Startup Sequence
Step-by-step instructions for what to load first.

---

## Workflows Explained

Workflows are multi-step processes. Example: `feature-implementation.md`

### Structure
```markdown
# Feature Implementation Workflow

## Step 1: Language Detection
- Detect the language being used
- Load appropriate language convention (.claude/conventions/languages/python.md)

## Step 2: Understand Requirements
- Read requirements carefully
- Ask questions if unclear

## Step 3: Plan Implementation
- List files to modify
- Estimate scope
- Confirm plan

## Step 4: Implement Incrementally
- Write code in small chunks
- Follow language conventions
- Test as you go

## Step 5: Self-Review
- Delegate to code-reviewer subagent
- Fix issues found

## Completion Criteria
- [ ] Feature implemented
- [ ] Tests passing
- [ ] Code reviewed
```

---

## Conventions Explained

### Core Convention (general.md)

Combines three files into one:
- **system.md** - Startup checklist, branch management
- **conventions.md** - General development rules
- **session.md** - Session tracking

**Size:** ~10KB  
**Always loaded first**

### Language Conventions

Each language has its own file (e.g., `python.md`, `typescript.md`):

**Contains:**
- Naming conventions
- Error handling patterns
- Import organization
- Type hints / type annotations
- Testing patterns
- Documentation standards

**Size:** ~8KB each  
**Loaded by workflow** when language is detected

**Available Languages:** 30 languages including Python, TypeScript, Rust, Go, Java, JavaScript, C, C++, Kotlin, Swift, Ruby, PHP, Scala, and more.

---

## Subagents Explained

Subagents are specialized helpers. Example: `code-reviewer.md`

**Purpose:** Focused assistance for specific tasks

**Structure:**
```markdown
# Code Reviewer

**Purpose:** Review code for quality, patterns, bugs
**Delegation Context:** Called by code agent

## Role
Reviews code systematically...

## Instructions
1. Check for code smells
2. Verify patterns match existing code
3. Look for edge cases
...

## Return to Parent
After review, report findings and return control to parent agent.
```

**When Used:**
- Delegated to by primary agents
- Not user-selectable
- Focused, single-purpose

---

## Skills Explained

Skills are reusable capabilities stored in directories:

```
.claude/skills/feature-planning/
├── SKILL.md          # Main instructions
├── templates/        # Optional templates
└── examples/         # Optional examples
```

**Used by:** Workflows when specific capabilities needed

**Example:** feature-planning skill provides templates and checklists for planning complex features.

---

## Switching Between Tools

### From Another Tool to Claude

```bash
promptosaurus switch claude
```

This will:
1. Remove artifacts from other tools (.kilo/, .cursorrules, etc.)
2. Remove old custom_instructions/ if present
3. Create .claude/ directory
4. Generate CLAUDE.md
5. Generate all convention files

**No manual migration needed** - the system handles it automatically.

### From Claude to Another Tool

```bash
promptosaurus switch kilo-ide
```

This will:
1. Remove .claude/ directory
2. Remove CLAUDE.md
3. Create tool-specific artifacts

---

## Customizing for Your Project

### Add Project-Specific Conventions

Edit `.claude/conventions/core/general.md` to add:
- Project-specific rules
- Team conventions
- Custom workflows

### Add Custom Subagents

Create new subagent files in `.claude/subagents/`:

```markdown
# My Custom Helper

**Purpose:** Project-specific assistance
**Delegation Context:** Called by code agent

## Role
...

## Instructions
...
```

Update relevant agent files to reference your custom subagent.

---

## Troubleshooting

### "Claude isn't following conventions"

**Solution:** Check that the workflow is loading language conventions:
```markdown
## Step 1: Language Detection
Read: .claude/conventions/languages/python.md
```

### "Too many files, confused about structure"

**Solution:** Claude should follow lazy loading:
1. Read CLAUDE.md only
2. Load one agent
3. Follow that agent's instructions
4. Load resources as directed

Don't try to load everything at once.

### "Missing subagent file"

**Solution:** The subagent might be in a different location. Check the agent file for the correct path. Subagents are organized by parent agent in the source, but all written to `.claude/subagents/` in output.

### "Old custom_instructions/ still exists"

**Solution:** Run:
```bash
rm -rf custom_instructions/
promptosaurus switch claude
```

The new system doesn't use custom_instructions/.

---

## Best Practices

### 1. Always Start with CLAUDE.md
Don't try to read agent files directly. Start with CLAUDE.md for routing.

### 2. Load One Agent at a Time
Follow the lazy loading pattern. Don't load multiple agents unless explicitly instructed.

### 3. Let Workflows Direct Loading
Workflows know when to load language conventions, subagents, and skills. Follow their instructions.

### 4. Use Subagents for Delegation
When a task needs specialized focus, delegate to a subagent rather than trying to do everything in the main agent.

### 5. Version Control
Commit the entire `.claude/` directory and CLAUDE.md. These are project artifacts.

**Gitignore not needed** - all files are project-specific configuration.

---

## FAQ

### Q: Do I need to manually create any files?
**A:** No. Run `promptosaurus init` and everything is generated.

### Q: Can I edit the generated files?
**A:** Yes, but be aware they'll be regenerated on next build. For project-specific changes, add to `general.md` rather than editing agent files.

### Q: How do I add a new language?
**A:** Language conventions are bundled with Promptosaurus. If your language isn't supported, the workflow will use general conventions.

### Q: What's the difference between a workflow and a skill?
**A:** Workflows are multi-step processes that agents follow. Skills are reusable capabilities that workflows can invoke.

### Q: Can I use multiple agents at once?
**A:** No. Claude should use one agent per task. If you need coordination between tasks, use the orchestrator agent.

### Q: How do I update to the latest version?
**A:** Run `promptosaurus switch claude` to regenerate all files with the latest templates and conventions.

---

## Examples

### Example 1: Implementing a Feature

**User:** "Implement a user authentication feature"

**Claude's Process:**
1. Reads CLAUDE.md
2. Matches "implement" → code-agent
3. Loads `.claude/conventions/core/general.md`
4. Loads `.claude/agents/code-agent.md`
5. Agent file says: Load `.claude/workflows/feature-implementation.md`
6. Workflow says: Detect language → Load `.claude/conventions/languages/python.md`
7. Workflow says: Use skill → Load `.claude/skills/feature-planning/SKILL.md`
8. Follows workflow steps
9. When ready for review, delegates to code-reviewer subagent

**Total loaded:** ~30KB across 6 files

### Example 2: Debugging an Issue

**User:** "The login endpoint is returning 500 errors"

**Claude's Process:**
1. Reads CLAUDE.md
2. Matches "error" → debug-agent
3. Loads `.claude/conventions/core/general.md`
4. Loads `.claude/agents/debug-agent.md`
5. Agent says: Load `.claude/workflows/root-cause.md`
6. When analyzing logs, delegates to log-analyzer subagent
7. When hypothesis formed, delegates to rubber-duck subagent for verification

**Total loaded:** ~25KB across 5 files

---

## Additional Resources

- **Design Documentation:** `docs/design/CLAUDE_ARTIFACT_REDESIGN.md`
- **Status Tracking:** `docs/design/CLAUDE_REDESIGN_STATUS.md`
- **Architecture Overview:** `docs/ARCHITECTURE.md`
- **Troubleshooting:** `docs/TROUBLESHOOTING.md`

---

**Need Help?** Open an issue on GitHub or check the troubleshooting guide.
