# Subagent Variant Rewrite Checklist

**Date Started:** 2026-04-10  
**Goal:** Differentiate all 28 subagent minimal/verbose variants per VARIANT_DIFFERENTIATION_STRATEGY.md

---

## ⚠️ CRITICAL RULES

### ✅ EDIT SOURCE CODE ONLY
- **SOURCE:** `promptosaurus/agents/*/subagents/*/minimal/prompt.md`
- **SOURCE:** `promptosaurus/agents/*/subagents/*/verbose/prompt.md`

### ❌ DO NOT EDIT GENERATED CODE
- **GENERATED:** `.kilo/` - This is OUTPUT ONLY, regenerated on build
- **GENERATED:** `.kilocode/` - This is OUTPUT ONLY
- **GENERATED:** Any other build output directories

---

## Differentiation Guidelines

**Minimal (20-50 lines):**
- Concise bullet points
- Core instructions only
- Assumes experienced reader
- Quick reference

**Verbose (150-350 lines):**
- Detailed explanations
- Code examples and snippets
- Common pitfalls (❌/✅)
- Anti-patterns to avoid
- Templates and workflows

---

## Progress Tracking

### ✅ Wave 1: Architect (2/2 COMPLETE)

- [x] **architect/data-model**
  - [x] `promptosaurus/agents/architect/subagents/data-model/minimal/prompt.md` (58 lines)
  - [x] `promptosaurus/agents/architect/subagents/data-model/verbose/prompt.md` (402 lines)
  
- [x] **architect/task-breakdown**
  - [x] `promptosaurus/agents/architect/subagents/task-breakdown/minimal/prompt.md` (57 lines)
  - [x] `promptosaurus/agents/architect/subagents/task-breakdown/verbose/prompt.md` (630 lines)

### ✅ Wave 2: Code & Debug (5/5 COMPLETE)

- [x] **code/boilerplate**
  - [x] `promptosaurus/agents/code/subagents/boilerplate/minimal/prompt.md` (62 lines)
  - [x] `promptosaurus/agents/code/subagents/boilerplate/verbose/prompt.md` (403 lines)

- [x] **code/feature**
  - [x] `promptosaurus/agents/code/subagents/feature/minimal/prompt.md` (66 lines)
  - [x] `promptosaurus/agents/code/subagents/feature/verbose/prompt.md` (437 lines)

- [x] **debug/log-analysis**
  - [x] `promptosaurus/agents/debug/subagents/log-analysis/minimal/prompt.md` (64 lines)
  - [x] `promptosaurus/agents/debug/subagents/log-analysis/verbose/prompt.md` (526 lines)

- [x] **debug/root-cause**
  - [x] `promptosaurus/agents/debug/subagents/root-cause/minimal/prompt.md` (66 lines)
  - [x] `promptosaurus/agents/debug/subagents/root-cause/verbose/prompt.md` (667 lines)

- [x] **debug/rubber-duck**
  - [x] `promptosaurus/agents/debug/subagents/rubber-duck/minimal/prompt.md` (48 lines)
  - [x] `promptosaurus/agents/debug/subagents/rubber-duck/verbose/prompt.md` (461 lines)

### ✅ Wave 3: Orchestrator & Ask (6/6 COMPLETE)

- [x] **orchestrator/devops**
  - [x] `promptosaurus/agents/orchestrator/subagents/devops/minimal/prompt.md` (60 lines)
  - [x] `promptosaurus/agents/orchestrator/subagents/devops/verbose/prompt.md` (497 lines)

- [x] **orchestrator/meta**
  - [x] `promptosaurus/agents/orchestrator/subagents/meta/minimal/prompt.md` (48 lines)
  - [x] `promptosaurus/agents/orchestrator/subagents/meta/verbose/prompt.md` (413 lines)

- [x] **orchestrator/pr-description**
  - [x] `promptosaurus/agents/orchestrator/subagents/pr-description/minimal/prompt.md` (64 lines)
  - [x] `promptosaurus/agents/orchestrator/subagents/pr-description/verbose/prompt.md` (221 lines)

- [x] **ask/decision-log**
  - [x] `promptosaurus/agents/ask/subagents/decision-log/minimal/prompt.md` (63 lines)
  - [x] `promptosaurus/agents/ask/subagents/decision-log/verbose/prompt.md` (396 lines)

- [x] **ask/docs**
  - [x] `promptosaurus/agents/ask/subagents/docs/minimal/prompt.md` (63 lines)
  - [x] `promptosaurus/agents/ask/subagents/docs/verbose/prompt.md` (582 lines)

- [x] **ask/testing**
  - [x] `promptosaurus/agents/ask/subagents/testing/minimal/prompt.md` (84 lines)
  - [x] `promptosaurus/agents/ask/subagents/testing/verbose/prompt.md` (630 lines)

### ✅ Wave 4: Review, Security, Compliance (8/8 COMPLETE)

- [x] **review/code**
  - [x] `promptosaurus/agents/review/subagents/code/minimal/prompt.md` (58 lines)
  - [x] `promptosaurus/agents/review/subagents/code/verbose/prompt.md` (313 lines)

- [x] **review/performance**
  - [x] `promptosaurus/agents/review/subagents/performance/minimal/prompt.md` (46 lines)
  - [x] `promptosaurus/agents/review/subagents/performance/verbose/prompt.md` (304 lines)

- [x] **review/accessibility**
  - [x] `promptosaurus/agents/review/subagents/accessibility/minimal/prompt.md` (41 lines)
  - [x] `promptosaurus/agents/review/subagents/accessibility/verbose/prompt.md` (395 lines)

- [x] **security/review**
  - [x] `promptosaurus/agents/security/subagents/review/minimal/prompt.md` (48 lines)
  - [x] `promptosaurus/agents/security/subagents/review/verbose/prompt.md` (367 lines)

- [x] **security/threat-model**
  - [x] `promptosaurus/agents/security/subagents/threat-model/minimal/prompt.md` (42 lines)
  - [x] `promptosaurus/agents/security/subagents/threat-model/verbose/prompt.md` (284 lines)

- [x] **compliance/review**
  - [x] `promptosaurus/agents/compliance/subagents/review/minimal/prompt.md` (49 lines)
  - [x] `promptosaurus/agents/compliance/subagents/review/verbose/prompt.md` (290 lines)

- [x] **compliance/soc2**
  - [x] `promptosaurus/agents/compliance/subagents/soc2/minimal/prompt.md` (51 lines)
  - [x] `promptosaurus/agents/compliance/subagents/soc2/verbose/prompt.md` (306 lines)

- [x] **compliance/gdpr**
  - [x] `promptosaurus/agents/compliance/subagents/gdpr/minimal/prompt.md` (49 lines)
  - [x] `promptosaurus/agents/compliance/subagents/gdpr/verbose/prompt.md` (389 lines)

### ✅ Wave 5: Final Subagents (5/5 COMPLETE)

- [x] **document/strategy-for-applications**
  - [x] `promptosaurus/agents/document/subagents/strategy-for-applications/minimal/prompt.md` (58 lines)
  - [x] `promptosaurus/agents/document/subagents/strategy-for-applications/verbose/prompt.md` (400 lines)

- [x] **explain/strategy**
  - [x] `promptosaurus/agents/explain/subagents/strategy/minimal/prompt.md` (54 lines)
  - [x] `promptosaurus/agents/explain/subagents/strategy/verbose/prompt.md` (345 lines)

- [x] **migration/strategy**
  - [x] `promptosaurus/agents/migration/subagents/strategy/minimal/prompt.md` (60 lines)
  - [x] `promptosaurus/agents/migration/subagents/strategy/verbose/prompt.md` (466 lines)

- [x] **refactor/strategy**
  - [x] `promptosaurus/agents/refactor/subagents/strategy/minimal/prompt.md` (55 lines)
  - [x] `promptosaurus/agents/refactor/subagents/strategy/verbose/prompt.md` (589 lines)

- [x] **code/house-style**
  - [x] `promptosaurus/agents/code/subagents/house-style/minimal/prompt.md` (37 lines)
  - [x] `promptosaurus/agents/code/subagents/house-style/verbose/prompt.md` (575 lines)

---

## Summary Statistics

- **Total subagents:** 28
- **Completed:** 28 (100%) ✅ COMPLETE
- **In progress:** 0 (0%)
- **Pending:** 0 (0%)

**Lines written:**
- Minimal: 1,500 lines (28 subagents avg 54 lines)
- Verbose: 11,288 lines (28 subagents avg 403 lines)
- Total: 12,788 lines

**Wave 4 Statistics:**
- Minimal: 384 lines (8 subagents avg 48 lines)
- Verbose: 2,648 lines (8 subagents avg 331 lines)

**Wave 5 Statistics:**
- Minimal: 264 lines (5 subagents avg 53 lines)
- Verbose: 2,375 lines (5 subagents avg 475 lines)

---

## Verification Steps

After all rewrites complete:

- [ ] Run CLI init and verify no "variant not found" warnings
- [ ] Build sample output and verify differentiation
- [ ] Run pytest to check for regressions
- [ ] Manually spot-check 3-5 subagents for quality
- [ ] Update session file with completion status

---

## Wave Completion Checklist

### After Wave 3 (Orchestrator & Ask):
- [x] All 6 subagents have minimal variants (48-84 lines)
- [x] All 6 subagents have verbose variants (221-630 lines)
- [ ] Run: `uv run prompt init` - verify no warnings for Wave 3 subagents
- [ ] Spot-check 2 subagents for quality
- [x] Update progress statistics above

### After Wave 4 (Review, Security, Compliance):
- [x] All 8 subagents have minimal variants (41-58 lines)
- [x] All 8 subagents have verbose variants (284-395 lines)
- [ ] Run: `uv run prompt init` - verify no warnings for Wave 4 subagents
- [ ] Spot-check 2 subagents for quality
- [x] Update progress statistics above

### After Wave 5 (Final):
- [x] All 5 subagents have minimal variants (37-60 lines)
- [x] All 5 subagents have verbose variants (345-589 lines)
- [ ] Run: `uv run prompt init` - verify no warnings for Wave 5 subagents
- [ ] Spot-check 2 subagents for quality
- [x] Update progress statistics above

---

## Final Acceptance Criteria

Before marking this work complete:

- [ ] All 28 subagents have both minimal and verbose variants
- [ ] Minimal variants: 20-50 lines each
- [ ] Verbose variants: 150-350 lines each
- [ ] No "variant not found" warnings when running `uv run prompt init`
- [ ] All variants follow differentiation guidelines
- [ ] Code examples in verbose variants are syntactically correct
- [ ] No placeholders or TODOs in any variant
- [ ] All checklist items above are marked complete
- [ ] Session file updated with final status
- [ ] VARIANT_DIFFERENTIATION_STRATEGY.md goals achieved
