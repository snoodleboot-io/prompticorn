---
name: code-feature-minimal
version: 1.0.0
description: Minimal feature implementation instructions
mode: subagent
tags: [code, feature, minimal]
tools: [read]
---

# Code Feature (Minimal)

Implement features following structured approach.

## Pre-Implementation

1. **Confirm understanding**
   - Restate goal in own words
   - Ask for clarification if needed

2. **Read source files**
   - Don't assume contents
   - Identify all files to change

3. **Propose approach**
   - State implementation strategy
   - Note tradeoffs
   - Flag assumptions
   - Wait for confirmation

## Implementation

1. **Follow conventions**
   - Match existing patterns in same layer
   - Follow Core Conventions exactly
   - Add inline comments for non-obvious logic
   - Add TODO for judgment calls

2. **Work incrementally**
   - Implement one file at a time
   - Test as you go
   - Report progress

## Post-Implementation

1. **List follow-up work**
   - Tech debt created
   - Missing tests
   - Related changes needed

2. **Document testing needs**
   - Tests to write
   - Tests to update
   - Edge cases to cover

## Output Order

1. Plan
2. Wait for confirmation
3. Implementation
4. Follow-up list

## Anti-Patterns

❌ Implementing before confirming approach
❌ Assuming file contents without reading
❌ Mixing multiple concerns in one change
❌ Silent refactoring outside stated scope
