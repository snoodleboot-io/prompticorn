# Promptosaurus Extraction Status Report

## Overview

This report compares the IR (Intermediate Representation) source files against what has been extracted to `promptosaurus/agents/` and what has been built to `.kilo/`.

## Architecture Understanding

### Directory Structure

1. **IR Source (promptosaurus/):**
   - `promptosaurus/agents/` - Agent definitions with subagents
   - `promptosaurus/skills/` - Reusable skill modules
   - `promptosaurus/workflows/` - Workflow definitions

2. **Build Output (.kilo/):**
   - `.kilo/agents/` - Built agent markdown files
   - `.kilo/skills/` - Built skill files
   - `.kilo/workflows/` - Built workflow files
   - `.kilo/commands/` - Built command files

### Relationship Between Components

- **Agents** contain **subagents** which reference **skills** and **workflows**
- **Skills** are atomic, reusable instruction modules
- **Workflows** coordinate multi-step processes
- Build process filters based on `language_skill_mapping.yaml`

---

## 1. Skills Extraction Status

### IR Source Skills (8 total)
Located in: `promptosaurus/skills/`

```
✓ data-model-discovery
✓ feature-planning
✓ incremental-implementation
✓ mermaid-erd-creation
✓ post-implementation-checklist
✓ test-aaa-structure
✓ test-coverage-categories
✓ test-mocking-rules
```

### Built Skills (6 total)
Located in: `.kilo/skills/`

```
✓ feature-planning
✓ incremental-implementation
✓ post-implementation-checklist
✓ test-aaa-structure
✓ test-coverage-categories
✓ test-mocking-rules
```

### Missing from Build (2)

```
✗ data-model-discovery
✗ mermaid-erd-creation
```

**Analysis:**
These skills ARE referenced in `language_skill_mapping.yaml` (lines 32-33 in universal_skills.architecture_skills and lines 162-163 in python/architect). They exist in IR but didn't make it to the build output.

**Which subagents reference them:**
- `promptosaurus/agents/architect/subagents/data-model/` (both minimal and verbose)

**Possible cause:**
Build filtering may be excluding them OR build failed for these specific skills.

---

## 2. Workflows Extraction Status

### IR Source Workflows (21 total)
Located in: `promptosaurus/workflows/`

```
accessibility-workflow
boilerplate-workflow
code-workflow
data-model-workflow
decision-log-workflow
dependency-upgrade-workflow
docs-workflow
feature-workflow
house-style-workflow
log-analysis-workflow
meta-workflow
migration-workflow
performance-workflow
refactor-workflow
review-workflow
root-cause-workflow
scaffold-workflow
strategy-for-applications-workflow
strategy-workflow
task-breakdown-workflow
testing-workflow
```

### Built Workflows (3 actual + 2 docs)
Located in: `.kilo/workflows/`

```
code
refactor
testing
INDEX.md (documentation)
README.md (documentation)
```

### Missing from Build (18)

```
✗ accessibility-workflow
✗ boilerplate-workflow
✗ code-workflow (NOTE: "code" exists but "code-workflow" is missing)
✗ data-model-workflow
✗ decision-log-workflow
✗ dependency-upgrade-workflow
✗ docs-workflow
✗ feature-workflow
✗ house-style-workflow
✗ log-analysis-workflow
✗ meta-workflow
✗ migration-workflow
✗ performance-workflow
✗ refactor-workflow (NOTE: "refactor" exists but "refactor-workflow" is missing)
✗ review-workflow
✗ root-cause-workflow
✗ scaffold-workflow
✗ strategy-for-applications-workflow
✗ strategy-workflow
✗ task-breakdown-workflow
✗ testing-workflow (NOTE: "testing" exists but "testing-workflow" is missing)
```

**Analysis:**
Most workflows are missing from build output. Only 3 made it through.

---

## 3. Workflows → Subagents Mapping

All 21 workflows map to existing subagents:

| Workflow | Subagent Location |
|----------|------------------|
| accessibility-workflow | promptosaurus/agents/review/subagents/accessibility |
| boilerplate-workflow | promptosaurus/agents/code/subagents/boilerplate |
| code-workflow | promptosaurus/agents/review/subagents/code |
| data-model-workflow | promptosaurus/agents/architect/subagents/data-model |
| decision-log-workflow | promptosaurus/agents/ask/subagents/decision-log |
| dependency-upgrade-workflow | promptosaurus/agents/code/subagents/dependency-upgrade |
| docs-workflow | promptosaurus/agents/ask/subagents/docs |
| feature-workflow | promptosaurus/agents/code/subagents/feature |
| house-style-workflow | promptosaurus/agents/code/subagents/house-style |
| log-analysis-workflow | promptosaurus/agents/debug/subagents/log-analysis |
| meta-workflow | promptosaurus/agents/orchestrator/subagents/meta |
| migration-workflow | promptosaurus/agents/code/subagents/migration |
| performance-workflow | promptosaurus/agents/review/subagents/performance |
| refactor-workflow | promptosaurus/agents/code/subagents/refactor |
| review-workflow | promptosaurus/agents/compliance/subagents/review |
| root-cause-workflow | promptosaurus/agents/debug/subagents/root-cause |
| scaffold-workflow | promptosaurus/agents/architect/subagents/scaffold |
| strategy-for-applications-workflow | promptosaurus/agents/document/subagents/strategy-for-applications |
| strategy-workflow | promptosaurus/agents/explain/subagents/strategy |
| task-breakdown-workflow | promptosaurus/agents/architect/subagents/task-breakdown |
| testing-workflow | promptosaurus/agents/ask/subagents/testing |

**Conclusion:** All workflows have corresponding subagents extracted. The extraction to `agents/` is COMPLETE.

---

## 4. Subagents Extraction Status

All agents have subagents extracted:

| Agent | Subagents | Status |
|-------|-----------|--------|
| architect | data-model, scaffold, task-breakdown | ✓ Complete |
| ask | decision-log, docs, testing | ✓ Complete |
| code | boilerplate, dependency-upgrade, feature, house-style, migration, refactor | ✓ Complete |
| compliance | review | ✓ Complete |
| debug | log-analysis, root-cause, rubber-duck | ✓ Complete |
| document | strategy-for-applications | ✓ Complete |
| explain | strategy | ✓ Complete |
| migration | strategy | ✓ Complete |
| orchestrator | devops, meta, pr-description | ✓ Complete |
| refactor | strategy | ✓ Complete |
| review | accessibility, code, performance | ✓ Complete |
| security | review | ✓ Complete |
| test | strategy | ✓ Complete |

**Total:** 13 agents, ~30+ subagents — all extracted

---

## 5. Built Agents (15 total)

Located in: `.kilo/agents/`

```
architect.md
ask.md
code.md
compliance.md
debug.md
document.md
enforcement.md
explain.md
migration.md
orchestrator.md
planning.md
refactor.md
review.md
security.md
test.md
```

**Status:** All agents built successfully

---

## 6. Built Commands (4 total)

Located in: `.kilo/commands/`

```
feature-workflow.md
migration-workflow.md
refactor-workflow.md
review-workflow.md
```

**Analysis:** Only 4 workflows made it to commands. These appear to be the high-priority ones.

---

## Summary

### ✓ COMPLETE

1. **Agents → Subagents extraction:** All 21 workflows extracted to corresponding subagents
2. **Agent build output:** All 15 agents built to `.kilo/agents/`
3. **Subagent structure:** All subagents have minimal/ and verbose/ variants

### ✗ INCOMPLETE

1. **Skills build:**
   - Missing: `data-model-discovery`, `mermaid-erd-creation`
   - 6 out of 8 built (75%)

2. **Workflows build:**
   - Missing: 18 out of 21 workflows
   - Only 3 built (14%)

3. **Commands build:**
   - Only 4 workflow commands generated
   - 17 workflows missing from commands

---

## Recommended Actions

### Priority 1: Fix Skill Build Issues
- Investigate why `data-model-discovery` and `mermaid-erd-creation` aren't building
- These are referenced by architect/data-model subagent
- Check build logs for errors

### Priority 2: Understand Workflow Build Strategy
- Determine if workflows are supposed to be built individually
- Only 3 workflows built vs 21 source workflows
- Clarify: Are workflows embedded in subagents or standalone?

### Priority 3: Verify Language Filtering
- `language_skill_mapping.yaml` references many skills/workflows that don't exist in IR
- Example: "python-type-hints-enforcement", "pytest-best-practices", etc.
- Determine if these are planned but not yet created

---

## Next Steps

1. Run build with verbose logging to see why skills/workflows are filtered
2. Check if there's a language parameter being passed that filters out skills
3. Verify if workflows are meant to be embedded vs standalone builds
