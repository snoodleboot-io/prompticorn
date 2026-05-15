# Minimal vs Verbose Token Comparison

**Configuration:** Python Project, Software Engineer Persona  
**Date:** 2026-04-14

## Summary

| Variant | Total Artifacts | Typical Load | Context Used | Remaining |
|---------|----------------|--------------|--------------|-----------|
| **Minimal** | ~187K tokens | ~32K tokens | 16% | 168K tokens |
| **Verbose** | ~326K tokens | ~54K tokens | 27% | 146K tokens |

**Key Insight:** Even verbose variant uses only 27% of Claude's 200K context, leaving 73% for conversation!

---

## Full Artifact Sizes

### If You Load Everything (Not Recommended)

| Component | Minimal | Verbose | Difference |
|-----------|---------|---------|------------|
| 14 Agent files | ~185K tokens | ~323K tokens | +138K (+75%) |
| 5 Skills | ~627 tokens | ~1,097 tokens | +470 (+75%) |
| CLAUDE.md | ~1,250 tokens | ~1,250 tokens | 0 (same) |
| **TOTAL** | **~187K tokens** | **~326K tokens** | **+139K (+74%)** |

**Note:** You would NEVER load everything at once due to lazy loading architecture.

---

## Typical Load (What Actually Happens)

When a user makes a request, Claude loads only what's needed:

### Minimal Variant

```
User Request: "Write a function to validate email addresses"

Claude Loads:
┌─────────────────────────────────────────┬──────────┐
│ CLAUDE.md (routing)                     │  1,250 ⭢ │
│ Core conventions (general.md)           │ 12,500 ⭢ │
│ code-agent.md (matched agent)           │ 13,198 ⭢ │
│ Python convention                       │  3,346 ⭢ │
│ feature-implementation.md (workflow)    │    750 ⭢ │
│ code-reviewer.md (subagent)             │    500 ⭢ │
│ feature-planning skill                  │    125 ⭢ │
└─────────────────────────────────────────┴──────────┘
  TOTAL:                                    31,669 tokens
  
Context Remaining: 168,331 tokens (84%)
```

### Verbose Variant

```
User Request: "Write a function to validate email addresses"

Claude Loads:
┌─────────────────────────────────────────┬──────────┐
│ CLAUDE.md (routing)                     │  1,250 ⭢ │
│ Core conventions (general.md + examples)│ 21,875 ⭢ │
│ code-agent.md (with examples)           │ 23,097 ⭢ │
│ Python convention (extended)            │  5,854 ⭢ │
│ feature-implementation.md (detailed)    │  1,312 ⭢ │
│ code-reviewer.md (with examples)        │    875 ⭢ │
│ feature-planning skill (detailed)       │    219 ⭢ │
└─────────────────────────────────────────┴──────────┘
  TOTAL:                                    54,483 tokens
  
Context Remaining: 145,517 tokens (73%)
```

---

## Per-Component Breakdown

### Agent Files (14 agents)

| Agent | Minimal (tokens) | Verbose (tokens) | Difference |
|-------|------------------|------------------|------------|
| code-agent | 13,198 | 23,097 | +9,899 (+75%) |
| test-agent | 13,198 | 23,097 | +9,899 (+75%) |
| refactor-agent | 13,198 | 23,097 | +9,899 (+75%) |
| review-agent | 13,198 | 23,097 | +9,899 (+75%) |
| debug-agent | 13,198 | 23,097 | +9,899 (+75%) |
| ... (9 more) | ~13,198 each | ~23,097 each | +9,899 each |

**Total for all 14:** ~185K (minimal) vs ~323K (verbose)

### Core Conventions

| File | Minimal | Verbose | Content Difference |
|------|---------|---------|-------------------|
| general.md | ~12,500 tokens | ~21,875 tokens | +Examples, anti-patterns, extended explanations |
| python.md | ~3,346 tokens | ~5,854 tokens | +Code examples, common pitfalls, best practices |

### Workflows

| Workflow | Minimal | Verbose | What's Added |
|----------|---------|---------|--------------|
| feature-implementation | ~750 tokens | ~1,312 tokens | Step-by-step examples, edge case handling |
| code-review | ~750 tokens | ~1,312 tokens | Review checklist examples, common issues |
| test-strategy | ~750 tokens | ~1,312 tokens | Test patterns, coverage strategies |

### Subagents

| Subagent | Minimal | Verbose | What's Added |
|----------|---------|---------|--------------|
| code-reviewer | ~500 tokens | ~875 tokens | Review examples, common bugs |
| test-writer | ~500 tokens | ~875 tokens | Test templates, patterns |
| refactor-strategist | ~500 tokens | ~875 tokens | Refactor patterns, before/after examples |

### Skills

| Skill | Minimal | Verbose | What's Added |
|-------|---------|---------|--------------|
| feature-planning | ~125 tokens | ~219 tokens | Planning templates, examples |
| post-implementation-checklist | ~125 tokens | ~219 tokens | Detailed checklist items |

---

## What Makes Verbose 75% Larger?

### Minimal Variant Includes:
- ✅ Core instructions
- ✅ Required patterns
- ✅ Essential rules
- ❌ No code examples
- ❌ No anti-patterns
- ❌ Minimal explanations

### Verbose Variant Adds:
- ✅ **Code examples** for each pattern (+30%)
- ✅ **Extended explanations** of why rules exist (+20%)
- ✅ **Anti-pattern examples** showing what NOT to do (+15%)
- ✅ **Additional context** and edge cases (+10%)

**Total increase: ~75% more content**

---

## Context Window Analysis

```
Claude 3.5 Sonnet: 200,000 token context window
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MINIMAL (Typical Request):
┣━━━━━━━━━━━━━━━┫ 31,669 tokens (16%)
                 ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ 168,331 tokens free

VERBOSE (Typical Request):
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━┫ 54,483 tokens (27%)
                             ┗━━━━━━━━━━━━━━━━━━━━┛ 145,517 tokens free
```

**Both variants leave plenty of room for conversation!**

---

## Use Case Recommendations

### ✅ Use MINIMAL When:

- **Production use** - daily coding work
- **Experienced developers** - know the patterns already
- **Fast iteration** - need quick responses
- **Mobile/slow connections** - less data transfer
- **Cost-conscious** - fewer tokens = lower costs

**Benefits:**
- 16% context usage (84% free)
- Faster load times
- Less cognitive overhead
- More space for code generation

### 📚 Use VERBOSE When:

- **Onboarding** - new team members learning the codebase
- **Learning mode** - understanding WHY rules exist
- **Code review training** - teaching best practices
- **Documentation** - need examples for reference
- **Complex patterns** - need detailed explanations

**Benefits:**
- Comprehensive examples
- Anti-patterns shown
- Extended explanations
- Better for learning

**Still only 27% context usage!**

---

## Real-World Example

### Minimal: Email Validation Function

**User:** "Write a function to validate email addresses"

**Context Loaded:** 31,669 tokens

**Claude Response Space:** 168,331 tokens available

**Can Generate:** 
- ✅ Complete function implementation (~500 tokens)
- ✅ Unit tests (~800 tokens)
- ✅ Documentation (~200 tokens)
- ✅ Multiple iterations/refinements
- ✅ Full conversation thread
- ✅ Error handling examples

---

### Verbose: Email Validation Function

**User:** "Write a function to validate email addresses"

**Context Loaded:** 54,483 tokens (includes examples, anti-patterns)

**Claude Response Space:** 145,517 tokens available

**Can Generate:**
- ✅ Complete function with best practices
- ✅ Unit tests with edge cases
- ✅ Documentation with examples
- ✅ Explanation of why certain patterns used
- ✅ Common pitfalls avoided
- ✅ Full conversation thread

**Bonus:** Claude has SEEN examples of similar patterns in verbose context, leading to better code quality.

---

## File Size Comparison

### All Files (14 agents, Software Engineer persona)

| Format | Minimal | Verbose | Difference |
|--------|---------|---------|------------|
| **Size (KB)** | 729 KB | 1,272 KB | +543 KB (+74%) |
| **Size (MB)** | 0.71 MB | 1.24 MB | +0.53 MB |
| **Tokens** | ~187K | ~326K | +139K (+74%) |

### Download Time Estimates

**Minimal (729 KB):**
- Fast connection (100 Mbps): ~0.06 seconds
- Average connection (25 Mbps): ~0.23 seconds
- Slow connection (5 Mbps): ~1.2 seconds

**Verbose (1,272 KB):**
- Fast connection (100 Mbps): ~0.10 seconds
- Average connection (25 Mbps): ~0.41 seconds
- Slow connection (5 Mbps): ~2.0 seconds

**Negligible difference for modern connections!**

---

## Cost Analysis (Hypothetical)

If Claude charged per input token (hypothetical):

**Minimal:** 31,669 tokens/request  
**Verbose:** 54,483 tokens/request

**Difference:** 22,814 tokens/request (+72%)

**Example costs** (if $1 per 1M tokens):
- Minimal: $0.032 per request
- Verbose: $0.054 per request
- Difference: $0.022 per request

**For 1,000 requests:**
- Minimal: $32
- Verbose: $54
- Difference: $22 (+69%)

**Note:** Actual Claude pricing varies. This is illustrative only.

---

## Recommendations

### Default Choice: **MINIMAL**

**Why:**
- ✅ 16% context usage (plenty of room)
- ✅ Faster response initialization
- ✅ Lower token costs
- ✅ Sufficient for experienced developers
- ✅ More space for generated code

**When to switch to VERBOSE:**
- New team members onboarding
- Learning new patterns
- Teaching/training sessions
- Need example code references

### Configuration

```bash
# Minimal (default)
prompticorn init
# Select: Minimal variant

# Verbose (for learning)
prompticorn init
# Select: Verbose variant
```

### Switching Between Variants

```bash
# Update existing configuration
prompticorn update
# Change variant: Minimal ↔ Verbose
```

---

## Summary Table

| Metric | Minimal | Verbose | Winner |
|--------|---------|---------|--------|
| **Typical Load** | 31,669 tokens | 54,483 tokens | Minimal |
| **Context Free** | 168,331 tokens (84%) | 145,517 tokens (73%) | Minimal |
| **Load Time** | 0.23s (avg) | 0.41s (avg) | Minimal |
| **Code Examples** | No | Yes | Verbose |
| **Anti-patterns** | No | Yes | Verbose |
| **Explanations** | Basic | Extended | Verbose |
| **Learning Value** | Good | Excellent | Verbose |
| **Production Use** | Optimal | Good | Minimal |
| **Onboarding** | Good | Optimal | Verbose |

**Conclusion:** Both work great! Choose based on your use case. Default to Minimal for daily work, switch to Verbose for learning/onboarding.
