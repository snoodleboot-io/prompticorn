# Complete Analysis: Why Architect Wasn't Showing + What to Fix

## The Real Root Cause

**Promptosaurus uses legacy Kilo architecture, but newer Kilo IDE changed requirements.**

### Timeline

1. **Old Kilo:** Custom modes in `.kilocodemodes` worked automatically
2. **Promptosaurus:** Built system around `.kilocodemodes` + `.kilocode/rules-*/`
3. **New Kilo IDE:** Changed to require individual `.md` files in `.kilo/agents/`
4. **Result:** Legacy `.kilocodemodes` no longer supported
5. **Architect:** Hidden because it's a custom mode in legacy format

### Evidence

- Commit e3eb435 (Mar 7, 2026): Fixed custom modes generation for `.kilocodemodes`
- No commits ever updated builder to generate `.kilo/agents/*.md` format
- Kilo docs show `.kilocodemodes` is legacy (marked for VSCode extension migration)
- Kilo currently uses markdown files with YAML frontmatter for agents

## What Needs to Change

### 1. Refactor Builder to New Kilo Format

**Currently generates:**
```
.kilocode/
├── rules/
├── rules-code/
├── rules-architect/
└── .kilocodemodes (legacy manifest)
```

**Should generate:**
```
.kilo/
├── agents/
│   ├── architect.md
│   ├── code.md
│   ├── test.md
│   └── ...
└── rules/ (for CLI)
```

**Each agent file format:**
```markdown
---
description: What this agent does
mode: primary
permission:
  read: "*"
  edit: "docs/**/*.md"
  bash: deny
---

You are a principal architect...
(markdown body = the prompt)
```

### 2. Add Minimal/Verbose Choice at Setup

**User picks during init:**
```
Prompt verbosity? [verbose/minimal]
```

**Stored in config:**
```yaml
# .promptosaurus.yaml
prompts:
  verbosity: "verbose"  # or "minimal"
```

**Result:** Same file structure, different prompt content based on choice

## Implementation

See: `docs/DESIGN_KILO_REFACTOR_AND_MINIMAL_VERBOSE.md`

### Timeline
- Phase 1 (Week 1): Refactor builder for `.kilo/agents/*.md`
- Phase 2 (Week 1-2): Add minimal/verbose choice to setup
- Phase 3 (Week 2): Auto-migration for existing users

### Benefits

✅ **Fixes architect visibility** - Uses modern Kilo format
✅ **Minimal/verbose control** - User chooses at setup
✅ **Same structure** - No confusing parallel directories
✅ **10x token reduction** - Minimal mode for context-constrained users
✅ **Future-proof** - Uses current Kilo patterns

---

## What This Fixes

### Before
- ❌ Architect mode hidden (legacy format not supported)
- ❌ Other custom modes also hidden
- ❌ No user control over prompt verbosity
- ❌ Legacy format deprecated by Kilo

### After
- ✅ All agents visible in Kilo IDE
- ✅ User picks verbosity during setup
- ✅ Modern Kilo architecture
- ✅ Per-agent customization support (future)

---

## Summary

This is **not a bug in promptosaurus** — it's a **platform change from Kilo.**

The builder needs to be updated to generate agents in the new format. Once done:
1. Architect shows up automatically
2. All custom agents work in new Kilo
3. Users control prompt verbosity
4. Everything is modern and maintainable

Design document ready for implementation.
