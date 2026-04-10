# Workflow Handling Analysis

**Last Updated:** 2026-04-10  
**Status:** Analysis for implementation decision

---

## 1. How Each Tool Handles Workflows (Tool Requirements)

### Kilo
**Format:** Slash commands  
**Location:** `.kilo/commands/{command-name}.md`  
**Usage:** User invokes via `/command-name` syntax  
**Content:** Command definition with instructions  

**Example:**
```markdown
# In agent file:
## Workflows
See `/create-feature`, `/refactor-module` commands

# Separate command file: .kilo/commands/create-feature.md
1. Plan the feature
2. Write tests
3. Implement code
4. Review
```

**Key Point:** Workflows are SEPARATE files as slash commands, not embedded in agent files.

---

### Cline
**Format:** Markdown files (optional)  
**Location:** `.clinerules/workflows/` OR embedded in `.clinerules`  
**Usage:** Invoked when relevant context appears  
**Content:** Step-by-step instructions  

**Example:**
```markdown
# In .clinerules:
When implementing features:
1. Use test-first-implementation skill
2. Follow the feature-implementation workflow
3. Run tests before committing

# OR in .clinerules/workflows/feature-implementation.md:
## Feature Implementation Workflow
1. Analyze requirements
2. Create tests
3. Implement
4. Verify
```

**Key Point:** Workflows can be embedded OR separate files. Typically embedded in .clinerules.

---

### Claude Code
**Format:** workflow.md with YAML frontmatter  
**Location:** `.claude/skills/{skill-name}/workflow.md`  
**Usage:** Associated with skills, invoked automatically or manually  
**Content:** Full workflow with steps and instructions  

**Example:**
```markdown
# In .claude/skills/test-first-implementation/workflow.md:
---
name: test-first-implementation
steps:
  - Analyze requirements
  - Create test file
  - Run tests (should fail)
  - Implement code
  - Verify coverage
---

## Step 1: Analyze Requirements
Detailed instructions...

## Step 2: Create Test File
Detailed instructions...
```

**Key Point:** Workflows are INSIDE skill directories, paired with skills.

---

### GitHub Copilot
**Format:** No explicit workflow support  
**Location:** N/A (embedded in instructions)  
**Usage:** Written as part of agent instructions  
**Content:** Prose or bullet points  

**Example:**
```markdown
# In .github/copilot-instructions.md:
When implementing features:
1. Write tests first
2. Implement minimal code to pass tests
3. Refactor for clarity
4. Document the changes
```

**Key Point:** No separate workflow files. Everything is embedded in main instructions.

---

### Cursor
**Format:** Embedded in rules or skills  
**Location:** `.cursor/rules/{name}.md` OR in skill files  
**Usage:** Part of rules/skills, applied contextually  
**Content:** Step-by-step within rules  

**Example:**
```markdown
# In .cursor/rules/feature-implementation.md:
When implementing features:

**Workflow:**
1. Analyze requirements
2. Design approach
3. Implement with tests
4. Review and refactor

Apply this workflow whenever...
```

**Key Point:** Workflows embedded in rules or skills, not separate files.

---

## 2. How We're Currently Handling Workflows (Our Implementation)

### Current State: **Just Listing Names** ❌

All builders currently do the same thing:

```python
# KiloBuilder
def _format_workflows(self, workflows: list[str]) -> str:
    lines = []
    for workflow in workflows:
        lines.append(f"- {workflow}")  # Just the name!
    return "\n".join(lines)

# ClineBuilder
def _format_workflows_section(self, workflow_names: list[str]) -> str:
    lines = ["## Workflows", ""]
    for workflow in workflow_names:
        lines.append(f"- {workflow}")  # Just the name!
    return "\n".join(lines)

# ClaudeBuilder, CopilotBuilder, CursorBuilder - same pattern
```

**Output Example (All Builders):**
```markdown
## Workflows
- feature-workflow
- data-model-workflow
```

### What We HAVE But Don't Use: workflow.md Files ✅

We have 50+ workflow.md files in the IR:

```
promptosaurus/agents/code/subagents/feature/minimal/workflow.md
```

**Content:**
```yaml
---
name: feature-workflow
description: Step-by-step process for feature
steps:
- 'Before writing any code:'
- 'After confirmation:'
- 'After implementation:'
---

## Steps

### Step 1: Before writing any code:
Detailed instructions for this step.

### Step 2: After confirmation:
Detailed instructions for this step.
```

**Problem:** Builders are NOT loading or using this content! They just list the name.

---

## 3. The Gap: What We Should Be Doing

### Tool Requirements Summary

| Tool | Workflow Location | Format | Should We Generate? |
|------|------------------|--------|---------------------|
| **Kilo** | `.kilo/commands/{name}.md` | Slash command files | ✅ YES - separate files |
| **Cline** | Embedded in `.clinerules` | Markdown sections | ✅ YES - embed in output |
| **Claude Code** | `.claude/skills/{skill}/workflow.md` | Separate workflow files | ✅ YES - separate files |
| **Copilot** | Embedded in instructions | Prose/bullets | ✅ YES - embed in output |
| **Cursor** | Embedded in rules | Markdown sections | ✅ YES - embed in output |

### What We Need To Implement

#### Option 1: Load and Embed Workflow Content (Recommended)

**For Cline, Copilot, Cursor:** Embed workflow content in agent output
```python
def _format_workflows_section(self, workflow_names: list[str], agent_name: str, variant: str) -> str:
    """Load workflow content and embed in output."""
    lines = ["## Workflows", ""]
    
    for workflow_name in workflow_names:
        # Load workflow.md from IR
        workflow_content = self._load_workflow_content(agent_name, workflow_name, variant)
        
        if workflow_content:
            lines.append(f"### {workflow_name}")
            lines.append("")
            lines.append(workflow_content)
            lines.append("")
    
    return "\n".join(lines)
```

**For Kilo:** Write separate command files
```python
def _write_workflow_commands(self, output: Path, agent_name: str, workflows: list[str], variant: str):
    """Write workflow files as Kilo slash commands."""
    commands_dir = output / ".kilo" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    
    for workflow_name in workflows:
        workflow_content = self._load_workflow_content(agent_name, workflow_name, variant)
        command_file = commands_dir / f"{workflow_name}.md"
        command_file.write_text(workflow_content)
```

**For Claude Code:** Write to skill directory
```python
def _write_skill_workflows(self, output: Path, skill_name: str, workflow_content: str):
    """Write workflow.md inside skill directory."""
    workflow_dir = output / ".claude" / "skills" / skill_name
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_file = workflow_dir / "workflow.md"
    workflow_file.write_text(workflow_content)
```

#### Option 2: Keep Current Approach (Not Recommended)

Just list workflow names and let tools figure it out.

**Problem:** Tools won't know what the workflows actually contain!

---

## 4. Recommended Implementation Plan

### Phase 1: Add Workflow Loader
```python
# promptosaurus/ir/loaders/workflow_loader.py - already exists!
# Just need to use it in builders
```

### Phase 2: Update Each Builder

**KiloBuilder:**
- Write workflow content to `.kilo/commands/{workflow-name}.md`
- Format as slash command files

**ClineBuilder:**
- Embed workflow content in `.clinerules` output
- Include full step-by-step instructions

**ClaudeBuilder:**
- Write workflow.md files to `.claude/skills/{skill-name}/workflow.md`
- Associate with skills

**CopilotBuilder:**
- Embed workflow content in main instructions
- Format as numbered lists

**CursorBuilder:**
- Embed workflow content in rules output
- Include with skill references

### Phase 3: Test & Verify
- Verify workflow files are generated correctly
- Test with each tool to ensure workflows are recognized
- Update tests to check for workflow content (not just names)

---

## 5. Current vs. Desired Output

### Current Output (All Builders) ❌
```markdown
## Workflows
- feature-workflow
- data-model-workflow
```

### Desired Output

**Kilo** - Separate files:
```markdown
# .kilo/commands/feature-workflow.md
---
name: feature-workflow
description: Step-by-step feature implementation
---

## Steps

### 1. Before writing code
- Restate the goal
- Read relevant files
- Propose approach
```

**Cline/Copilot/Cursor** - Embedded:
```markdown
## Workflows

### feature-workflow
Step-by-step feature implementation

**Steps:**
1. Before writing code:
   - Restate the goal
   - Read relevant files
   - Propose approach

2. After confirmation:
   - Implement following conventions
   - Add inline comments
   - One file at a time
```

**Claude Code** - In skill directory:
```markdown
# .claude/skills/feature-planning/workflow.md
---
name: feature-workflow
steps:
  - Before writing code
  - After confirmation
  - After implementation
---

## Step 1: Before Writing Code
Detailed instructions...
```

---

## 6. Decision Required

**Question:** Should we implement proper workflow handling now, or defer?

**Option A: Implement Now** (Recommended)
- ✅ Workflows become actually useful
- ✅ Matches tool expectations
- ✅ We already have workflow.md files
- ⏱️ ~2-3 hours work

**Option B: Defer**
- Current output is incomplete
- Tools won't know what workflows contain
- Less useful for users
- BUT: Can be added later without breaking changes

---

## Summary

**Gap:** We have workflow.md files in IR, but builders only output names, not content.

**Tools Expect:**
- **Kilo:** Separate `.kilo/commands/{name}.md` files
- **Cline/Copilot/Cursor:** Embedded workflow content
- **Claude Code:** Workflow files in skill directories

**Recommendation:** Implement proper workflow handling. We have the data (workflow.md files), we just need to use it.
