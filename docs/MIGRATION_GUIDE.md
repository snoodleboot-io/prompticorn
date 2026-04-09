# Phase 2A Migration Guide

**Version:** 2.0.0  
**Date:** April 9, 2026  
**Target Audience:** Existing Promptosaurus users upgrading to Phase 2A

---

## Table of Contents

1. [Overview](#overview)
2. [Backwards Compatibility](#backwards-compatibility)
3. [Why Migrate?](#why-migrate)
4. [Migration Path](#migration-path)
5. [Step-by-Step Migration](#step-by-step-migration)
6. [Builder-Specific Examples](#builder-specific-examples)
7. [Troubleshooting](#troubleshooting)
8. [Rollback Instructions](#rollback-instructions)

---

## Overview

Phase 2A introduces a **unified, tool-agnostic Intermediate Representation (IR)** system for managing AI agent prompts. This guide helps you migrate your existing configurations to take advantage of the new system.

### What Changed

**Before (Phase 1):**
- Tool-specific prompt files in separate locations
- No unified configuration format
- Manual synchronization across tools

**After (Phase 2A):**
- Single source of truth: `agents/` directory with IR models
- Automatic generation for all 5 tools
- Unified configuration structure
- Backward compatible with existing files

### Key Benefits

✅ **Write Once, Build Everywhere** - Define your agent once in IR format  
✅ **Token Efficiency** - Minimal/verbose variants save tokens  
✅ **Consistency** - Same agent across all 5 tools (Kilo, Claude, Cline, Cursor, Copilot)  
✅ **Maintainability** - Single source of truth eliminates sync issues  
✅ **Extensibility** - Easy to add new builders for additional tools  

---

## Backwards Compatibility

### ✅ 100% Backward Compatible

Phase 2A is **fully backward compatible**. No breaking changes:

- ✅ Existing agent configurations continue to work
- ✅ No changes required to existing `.kilo/` structures
- ✅ No changes required to existing tool-specific files
- ✅ Existing CLI commands still work
- ✅ Existing imports still work

### Coexistence Model

You can run old and new systems side-by-side during migration:

```
agents/                    ← NEW: Unified IR (Phase 2A)
  architect/
    minimal/
      prompt.md
      skills.md
      workflow.md
    verbose/
      prompt.md
      skills.md
      workflow.md
  test/
    minimal/
    verbose/

.kilo/                     ← OLD: Still works (Phase 1)
  agents/
    architect.md
    test.md
  rules/
    conventions.md
```

Both can coexist. Gradually migrate at your own pace.

---

## Why Migrate?

### Problems Migration Solves

| Problem | Before | After |
|---------|--------|-------|
| Multiple sources of truth | 5 tool-specific files | 1 IR definition |
| Token waste | Verbose everywhere | Minimal/verbose variants |
| Consistency | Manual sync | Automatic sync |
| Adding tools | Duplicate all configs | Use existing IR |
| Maintenance burden | Update 5 files | Update 1 IR |

### Example: Updating the Architect Agent

**Before (5 separate updates):**
```bash
# Update Kilo
vim .kilo/agents/architect.md

# Update Cline
vim .clinerules  # Search for architect section

# Update Claude
vim claude-agents.json  # Find architect object

# Update Cursor
vim .cursorrules  # Update architect rules

# Update Copilot
vim .github/copilot-instructions.md  # Update section

# Verify consistency across all 5 files (error-prone!)
```

**After (1 IR update, automatic generation):**
```bash
# Update IR
vim agents/architect/verbose/prompt.md

# Regenerate all tools
promptosaurus build

# Done! All 5 tools updated from same source
```

---

## Migration Path

### Recommended Migration Strategy

**Phase 2A supports two migration approaches:**

1. **Gradual Migration** (Recommended)
   - Migrate one agent at a time
   - Keep old system running in parallel
   - Low risk, easy rollback
   - Timeline: At your own pace

2. **Big Bang Migration** (For teams)
   - Migrate all agents at once
   - Requires more coordination
   - Faster overall timeline
   - Higher risk (mitigated by tests)

### Timeline

- **Week 1:** Migrate core agents (architect, test, code)
- **Week 2-3:** Migrate remaining agents
- **Week 4:** Deprecate old system

Or migrate at your own pace - there's no deadline.

---

## Step-by-Step Migration

### Step 1: Install Phase 2A

```bash
# Update to latest version
pip install --upgrade promptosaurus

# Verify installation
promptosaurus --version
# Output: promptosaurus 2.0.0
```

### Step 2: Create IR Directory Structure

```bash
# Create agents directory
mkdir -p agents

# Create first agent directory
mkdir -p agents/architect/{minimal,verbose}
mkdir -p agents/test/{minimal,verbose}
mkdir -p agents/code/{minimal,verbose}
```

### Step 3: Migrate Agent Configuration

For each agent, create three files in the IR format:

**File 1: `agents/{agent}/minimal/prompt.md`**
```markdown
---
name: architect
description: Design system architecture and data models
---

You are an expert software architect...
```

**File 2: `agents/{agent}/minimal/skills.md`** (if applicable)
```markdown
---
skills: [skill1, skill2]
---

## Key Skills

- Skill 1: Description
- Skill 2: Description
```

**File 3: `agents/{agent}/minimal/workflow.md`** (if applicable)
```markdown
---
workflows: [workflow1, workflow2]
---

## Key Workflows

1. Workflow 1: Description
2. Workflow 2: Description
```

**Then create verbose variants:**

Duplicate the minimal files with the same structure, but with more comprehensive content (2-3x longer).

### Step 4: Validate IR

```bash
# Validate all configurations
promptosaurus validate

# Output:
# ✓ 3 agents found
# ✓ All required files present
# ✓ No orphaned files
# ✓ Configuration valid
```

### Step 5: Build All Tools

```bash
# Generate all tool outputs from IR
promptosaurus build

# Output:
# ✓ Built KiloBuilder (1.2ms)
# ✓ Built ClineBuilder (1.1ms)
# ✓ Built ClaudeBuilder (1.3ms)
# ✓ Built CursorBuilder (1.0ms)
# ✓ Built CopilotBuilder (0.9ms)
# ✓ Total: 5 tools in 5.5ms
```

### Step 6: Verify Generated Output

```bash
# Compare generated output with old system
diff -r .kilo/agents/ <(promptosaurus build --output kilo)

# Should be semantically equivalent
# (formatting may differ slightly)
```

### Step 7: Commit Changes

```bash
# Commit IR and generated files
git add agents/ .kilo/ .clinerules .cursorrules etc.
git commit -m "feat: Migrate to Phase 2A unified IR system"
```

---

## Builder-Specific Examples

### Example 1: Migrate Architect Agent (Kilo)

**Step A: Create IR for Kilo's Architect Agent**

```bash
mkdir -p agents/architect/{minimal,verbose}
```

**File: `agents/architect/minimal/prompt.md`**
```markdown
---
name: architect
description: Design system architecture and data models
---

You are an expert software architect with deep knowledge of:

- System design patterns and principles
- Database modeling and optimization
- API design and contract definition
- Deployment topologies and infrastructure

Your role is to design:
- Data models and schemas
- Service boundaries
- API contracts
- Deployment architecture

Focus on scalability, maintainability, and clarity.
```

**File: `agents/architect/verbose/prompt.md`** (Same as above, but with more examples and detail)

**File: `agents/architect/minimal/skills.md`**
```markdown
---
skills: ["data-modeling", "api-design"]
---

## Available Skills

- **data-modeling:** Design database schemas and data relationships
- **api-design:** Define REST/GraphQL contracts and versioning strategies
```

**Step B: Build for Kilo**

```bash
# Build just this agent for Kilo
promptosaurus build --tool kilo --agent architect

# Output: .kilo/agents/architect.md
```

**Step C: Verify Output**

```bash
# Check generated YAML structure
cat .kilo/agents/architect.md

# Should have YAML frontmatter:
# ---
# name: architect
# description: Design system architecture and data models
# tools: [...]
# skills: [...]
# ---
```

---

### Example 2: Migrate Test Agent (Cline)

**File: `agents/test/minimal/prompt.md`**
```markdown
---
name: test
description: Write comprehensive tests with coverage-first approach
---

You are an expert test engineer focused on:

- Test design and coverage
- Unit and integration testing
- Edge case identification
- Mutation testing for quality verification

Write tests that verify behavior, not implementation.
Use property-based testing for generative edge cases.
```

**File: `agents/test/minimal/skills.md`**
```markdown
---
skills: ["test-design", "edge-case-analysis", "mutation-testing"]
---

## Available Skills

- **test-design:** Write comprehensive test suites
- **edge-case-analysis:** Identify and test boundary conditions
- **mutation-testing:** Verify test quality with fault injection
```

**Build for Cline:**

```bash
promptosaurus build --tool cline --agent test

# Output: .clinerules (or agents/test/.clinerules)
```

**Verify Cline Output:**

```bash
# Check for use_skill pattern
grep -n "use_skill" .clinerules

# Should show:
# use_skill test-design
# use_skill edge-case-analysis
# use_skill mutation-testing
```

---

### Example 3: Migrate Code Agent (Claude)

**File: `agents/code/minimal/prompt.md`**
```markdown
---
name: code
description: Implement features, fix bugs, and refactor code
---

You are an expert software engineer focused on:

- Clean code principles
- SOLID design patterns
- Type safety and testing
- Performance and maintainability

Write code that is readable, tested, and maintainable.
```

**File: `agents/code/minimal/skills.md`**
```markdown
---
skills: ["feature-implementation", "bug-fixing", "refactoring"]
---

## Available Skills

- **feature-implementation:** Add new functionality
- **bug-fixing:** Diagnose and fix defects
- **refactoring:** Improve code structure
```

**Build for Claude:**

```bash
# Build JSON format for Claude
promptosaurus build --tool claude --agent code

# Output: claude-agents.json
```

**Verify Claude Output:**

```bash
# Check JSON structure
jq '.tools | length' claude-agents.json

# Should show number of tools defined
```

---

### Example 4: Migrate Security Agent (Cursor)

**File: `agents/security/minimal/prompt.md`**
```markdown
---
name: security
description: Security review for code and infrastructure
---

You are a security engineer focused on:

- Code vulnerabilities
- Infrastructure security
- Secrets management
- OWASP top 10 prevention
```

**Build for Cursor:**

```bash
promptosaurus build --tool cursor --agent security

# Output: .cursorrules
```

---

### Example 5: Migrate Review Agent (Copilot)

**File: `agents/review/minimal/prompt.md`**
```markdown
---
name: review
description: Code review for quality and performance
---

You are a code reviewer focused on:

- Code quality and maintainability
- Performance optimization
- Testing coverage
- API design and consistency
```

**Build for Copilot:**

```bash
promptosaurus build --tool copilot --agent review

# Output: .github/instructions/review.md (with applyTo metadata)
```

**Verify Copilot Output:**

```bash
# Check YAML frontmatter with applyTo
head -20 .github/instructions/review.md | grep -A5 "applyTo"
```

---

## Troubleshooting

### Issue 1: Missing Files Error

**Error:**
```
ValidationError: agents/architect/minimal/prompt.md not found
```

**Solution:**
```bash
# Verify file exists
ls -la agents/architect/minimal/

# Should show: prompt.md, skills.md, workflow.md
# (skills.md and workflow.md are optional)

# Create missing file
touch agents/architect/minimal/prompt.md
```

### Issue 2: Invalid YAML Frontmatter

**Error:**
```
YAMLError: expected '<document start>', but found '<stream start>'
```

**Solution:**
```markdown
# Check file starts with YAML frontmatter
head -1 agents/architect/minimal/prompt.md

# Should show: ---
# If missing, add frontmatter:
---
name: architect
description: Design system architecture
---

Your content here...
```

### Issue 3: Build Output Doesn't Match Old System

**Issue:**
Generated output format differs from old system

**Solution:**
```bash
# Check with verbose mode
promptosaurus build --agent architect --verbose

# Compare line-by-line
diff -u old-architect.md new-architect.md

# Semantic differences are OK (formatting may differ)
# Content and structure should be equivalent
```

### Issue 4: Variant Not Found (Falls Back to Verbose)

**Warning:**
```
agents/architect/minimal/prompt.md not found, using verbose
```

**Solution:**
```bash
# Create minimal variant from verbose
cp agents/architect/verbose/prompt.md agents/architect/minimal/prompt.md

# Edit to remove redundancy
# Minimal should be ~10% size of verbose
```

### Issue 5: Tool-Specific Format Issues

**For Kilo:**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('.kilo/agents/architect.md'))"
```

**For Cline:**
```bash
# Verify use_skill pattern
grep "^use_skill " .clinerules
```

**For Claude:**
```bash
# Validate JSON
jq '.' claude-agents.json > /dev/null && echo "Valid JSON"
```

---

## Rollback Instructions

### If You Need to Go Back

If something goes wrong during migration, rollback is safe and easy:

```bash
# Step 1: Delete IR (goes back to old system)
rm -rf agents/

# Step 2: Restore old tool-specific files from git
git checkout .kilo/ .clinerules .cursorrules .github/copilot-instructions.md

# Step 3: Downgrade package (optional)
pip install promptosaurus==1.9.9

# Done - old system is restored
```

---

## Migration Verification Checklist

After migrating each agent, verify with this checklist:

```bash
# ✓ IR structure exists
[ ] agents/{agent}/minimal/prompt.md exists
[ ] agents/{agent}/verbose/prompt.md exists

# ✓ Generated files exist
[ ] .kilo/agents/{agent}.md exists
[ ] .clinerules has {agent} section
[ ] claude-agents.json has {agent} entry
[ ] .cursorrules has {agent} rules
[ ] .github/instructions/{agent}.md exists

# ✓ Content verification
[ ] All 5 tool outputs generated correctly
[ ] No validation errors when running `promptosaurus validate`
[ ] Performance acceptable (< 1ms per tool)

# ✓ Testing
[ ] Tests pass for generated configuration
[ ] No regressions in tool-specific behavior
[ ] Agent works as expected in IDE/interface
```

---

## Post-Migration Steps

### 1. Team Communication

- Share migration guide with team
- Demo new IR system to team
- Explain benefits (write once, build everywhere)

### 2. Documentation Update

- Update project README with IR example
- Add IR structure to architecture docs
- Document any custom agents or variants

### 3. Process Changes

- Update agent creation workflow
- Add IR to code review guidelines
- Consider IR as source of truth going forward

### 4. Monitor and Feedback

- Collect feedback from team
- Identify any integration issues
- Report issues if found

---

## Common Questions

**Q: Do I need to migrate all agents at once?**  
A: No, migrate gradually at your own pace. Old and new systems can coexist.

**Q: Can I mix old and new formats?**  
A: Yes, partially. Keep using old system while migrating, or run both side-by-side.

**Q: What if I only use one tool (e.g., just Kilo)?**  
A: IR still helps - you define agent once and can easily add support for other tools later.

**Q: How do I handle tool-specific customizations?**  
A: IR is tool-agnostic by design. Tool-specific features go in builder implementations, not IR.

**Q: Can I use IR without the CLI tool?**  
A: Yes, IR is just a file format. You can load and build manually if needed.

**Q: Will this break my existing automation?**  
A: No, old CLI commands still work. New IR system is additive, not replacive.

---

## Support & Resources

- **Getting Started:** See [GETTING_STARTED.md](./GETTING_STARTED.md)
- **Builder API:** See [BUILDER_API_REFERENCE.md](./BUILDER_API_REFERENCE.md)
- **Implementation Guide:** See [BUILDER_IMPLEMENTATION_GUIDE.md](./BUILDER_IMPLEMENTATION_GUIDE.md)
- **Release Notes:** See [PHASE2A_RELEASE_NOTES.md](./PHASE2A_RELEASE_NOTES.md)

---

*Phase 2A Migration is designed to be smooth and non-disruptive. Take your time, test thoroughly, and reach out if you encounter any issues.*
