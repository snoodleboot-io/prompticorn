# Phase 1 Execution Guide

**Master Document:** `planning/current/PHASE1_TASK_CHECKLIST.md`

---

## How to Execute Phase 1

### The Execution Pattern (REQUIRED)

This pattern MUST be followed for every task:

1. **Read the task** from the checklist
2. **Create the file(s)**
3. **Check off the box** - Change `- [ ]` to `- [x]` in `PHASE1_TASK_CHECKLIST.md`
4. **Commit changes** - Include checklist update in the commit
5. **Update session** - Record progress in session file

### Example Workflow

```
Task: Create promptosaurus/agents/data/prompt.md

Step 1: Create the file
        (implement file content following existing patterns)

Step 2: Check off in checklist
        OLD: - [ ] Create `promptosaurus/agents/data/prompt.md` (agent definition)
        NEW: - [x] Create `promptosaurus/agents/data/prompt.md` (agent definition)

Step 3: Commit with checklist update
        git add promptosaurus/agents/data/prompt.md planning/current/PHASE1_TASK_CHECKLIST.md
        git commit -m "feat: Create data agent scaffolding
        
        - Created agents/data/prompt.md
        - Checked off checklist item"

Step 4: Update session with progress
        Open .promptosaurus/sessions/session_20260410_phase1_implementation.md
        Add new action entry with completed task
```

---

## Weekly Breakdown

### WEEK 1: Agent & Subagent Scaffolding
**Duration:** Days 1-5  
**Deliverables:** 31 files (3 agents + 28 subagent files)  
**Checklist Location:** `PHASE1_TASK_CHECKLIST.md` lines 51-223  

**Daily Targets:**
- **Day 1-2:** 3 agent files (agents/data, agents/observability, agents/incident)
- **Day 2-3:** 10 files (5 data subagents × 2 variants)
- **Day 3-4:** 10 files (5 observability subagents × 2 variants)
- **Day 4-5:** 8 files (4 incident subagents × 2 variants)

**Daily Execution:**
1. Open checklist to that day's section
2. Create all files for that day
3. Check off each `- [ ]` box
4. Commit all files + updated checklist
5. Update session with day's progress

**Example Day 1-2 Commit:**
```bash
git commit -m "feat: Create Phase 1 agent scaffolding (data, observability, incident)

- Created agents/data/prompt.md
- Created agents/observability/prompt.md
- Created agents/incident/prompt.md
- Updated PHASE1_TASK_CHECKLIST.md with completed items
- All 3 agent files follow core-conventions patterns"
```

### WEEK 2: Workflows Creation
**Duration:** Days 6-9  
**Deliverables:** 16 files (8 workflows × 2 variants)  
**Checklist Location:** `PHASE1_TASK_CHECKLIST.md` lines 224-353  

**Daily Targets:**
- **Day 6-7:** 6 files (3 data workflows × 2 variants)
- **Day 7-8:** 6 files (3 observability workflows × 2 variants)
- **Day 8-9:** 4 files (2 incident workflows × 2 variants)

### WEEK 3: Skills & Language Integration
**Duration:** Days 10-14  
**Deliverables:** 22 files (11 skills × 2 variants) + language mapping  
**Checklist Location:** `PHASE1_TASK_CHECKLIST.md` lines 354-519  

**Daily Targets:**
- **Day 10-11:** 10 files (5 data skills × 2 variants)
- **Day 11-12:** 8 files (4 observability skills × 2 variants)
- **Day 12-13:** 4 files (2 incident skills × 2 variants)
- **Day 13-14:** language_skill_mapping.yaml + verification

---

## File Naming Convention (Quick Reference)

All files must follow this structure exactly:

```
Agents:
  promptosaurus/agents/{name}/prompt.md
  
Subagents (with variants):
  promptosaurus/agents/{agent}/subagents/{name}/minimal/prompt.md
  promptosaurus/agents/{agent}/subagents/{name}/verbose/prompt.md
  
Workflows (with variants):
  promptosaurus/workflows/{name}/minimal/workflow.md
  promptosaurus/workflows/{name}/verbose/workflow.md
  
Skills (with variants):
  promptosaurus/skills/{name}/minimal/SKILL.md
  promptosaurus/skills/{name}/verbose/SKILL.md
```

---

## Content Guidelines (Quick Reference)

### Agent Files
- Overview of agent responsibilities
- List of capabilities and subagents
- When to use this agent
- Integration with Kilo system
- Follow existing agent pattern (e.g., code/prompt.md)

### Subagent Files (Minimal)
- 20-50 lines
- Concise bullet points
- Quick reference format
- Core capability explanation

### Subagent Files (Verbose)
- 150-350 lines
- Detailed with examples
- Anti-patterns and gotchas
- Real-world use cases
- Best practices and patterns

### Workflow Files
- Purpose and when to use
- Step-by-step process
- Inputs and outputs
- Error handling
- Integration points
- Follow existing workflow pattern

### Skill Files
- What the skill teaches
- When to apply it
- Examples and code snippets
- Common mistakes
- Advanced patterns

---

## Progress Tracking

### Visual Checklist Format

The checklist uses this format:

```markdown
- [ ] Task not yet started
- [x] Task completed and checked off
- [ ] Task with more detail
      - Additional context
      - Status: Not started
```

### How to Check Off

**OLD (not done):**
```markdown
- [ ] Create `promptosaurus/agents/data/prompt.md` (agent definition)
  - File: `promptosaurus/agents/data/prompt.md`
  - Content: Agent overview, responsibilities, capabilities
  - Status: Not started
```

**NEW (completed):**
```markdown
- [x] Create `promptosaurus/agents/data/prompt.md` (agent definition)
  - File: `promptosaurus/agents/data/prompt.md`
  - Content: Agent overview, responsibilities, capabilities
  - Status: COMPLETED
```

### Weekly Progress Grid

Check these grids during execution:

**Week 1 Progress:**
```
Agents/subagents: 0/31 ⬜  →  15/31 🟨  →  31/31 ✅
Files committed: 0 ⬜  →  20 🟨  →  31 ✅
```

**Week 2 Progress:**
```
Workflows: 0/16 ⬜  →  8/16 🟨  →  16/16 ✅
Files committed: 0 ⬜  →  12 🟨  →  16 ✅
```

**Week 3 Progress:**
```
Skills: 0/22 ⬜  →  15/22 🟨  →  22/22 ✅
Languages: 0/4 ⬜  →  2/4 🟨  →  4/4 ✅
```

---

## Commit Message Convention

### Day-end Commits

Format:
```
feat: Complete Phase 1 [Week X], Day [N]: [What was created]

- Item 1 created
- Item 2 created
- Item 3 created
- Updated PHASE1_TASK_CHECKLIST.md with completed tasks
- Total files: X (Y committed this session)

Status: [N/31 agents complete] [description of what's next]
```

### Example:
```
feat: Complete Phase 1 Week 1, Day 1-2: Agent scaffolding (data, observability, incident)

- Created agents/data/prompt.md
- Created agents/observability/prompt.md
- Created agents/incident/prompt.md
- Updated PHASE1_TASK_CHECKLIST.md with completed items
- All 3 agent files follow core-conventions patterns
- Total files: 3/31 completed

Status: 3/31 agents complete. Next: Data subagents (5 subagents, 10 files)
```

---

## Session File Updates

After each day's work, update the session file with:

```markdown
### 2026-04-11 14:30 - code mode
- **Task:** Phase 1 Week 1, Day 1-2 - Create agents scaffolding
- **Files created:**
  - promptosaurus/agents/data/prompt.md
  - promptosaurus/agents/observability/prompt.md
  - promptosaurus/agents/incident/prompt.md
- **Checklist updated:** 3 items checked off (lines 51-68)
- **Files committed:** 3 agent files + updated checklist
- **Status:** 3/31 Week 1 deliverables complete
- **Commit:** abc123def
```

---

## Verification at Each Checkpoint

### End of Day Verification
- [ ] All files created for that day exist
- [ ] All boxes checked in the checklist
- [ ] All files committed to git
- [ ] Session file updated with progress
- [ ] Commit message is clear and detailed

### End of Week Verification
- [ ] All files for that week exist
- [ ] All checklist items for week are checked
- [ ] Week summary section checked
- [ ] Total files match expected count
- [ ] Session updated with week summary

### End of Phase Verification
- [ ] All 69 files created and committed
- [ ] All checklist items checked
- [ ] Build succeeds with no errors
- [ ] `.kilo/` output contains all new agents, workflows, skills
- [ ] PR created with complete summary
- [ ] Session updated with Phase 1 completion

---

## Quick Commands

### Check Status
```bash
# Show current branch
git branch --show-current

# Show commits this session
git log --oneline | head -10

# Show files created
git status
```

### Track Checklist Progress
```bash
# Count checked items in Week 1
grep -c "^- \[x\]" planning/current/PHASE1_TASK_CHECKLIST.md | head -50

# Show all checked items
grep "^- \[x\]" planning/current/PHASE1_TASK_CHECKLIST.md
```

### Update and Commit
```bash
# Stage checklist and new files
git add planning/current/PHASE1_TASK_CHECKLIST.md promptosaurus/agents/

# Commit with message
git commit -m "feat: [description]"

# Verify
git status
```

---

## CRITICAL REMINDERS

🔴 **MUST CHECK OFF EACH TASK AS YOU COMPLETE IT**

- Change `- [ ]` to `- [x]` in the checklist
- Include checklist update in every commit
- This is the master tracking document
- Do not skip this step

🔴 **COMMIT FREQUENTLY**

- Commit at the end of each day
- Include checklist updates in commits
- Write clear commit messages
- Keep git history clean and traceable

🔴 **UPDATE SESSION FILE DAILY**

- Record what was completed
- Note any issues or blockers
- Update progress tracking
- This enables continuity if interrupted

---

## Ready to Start?

When you are ready:

1. Open `planning/current/PHASE1_TASK_CHECKLIST.md`
2. Start with Week 1, Days 1-2
3. Create the 3 agent files
4. Check off each item in the checklist
5. Commit with updated checklist
6. Report progress

**You now have everything needed to execute Phase 1 systematically and track every step.**
