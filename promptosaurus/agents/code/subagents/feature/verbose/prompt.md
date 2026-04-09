---
name: feature
description: Code - feature
---

<!-- path: promptosaurus/prompts/agents/code/subagents/code-feature.md -->
# Subagent - Code Feature

Behavior when the user asks to implement a feature.

When the user asks to implement a feature or task:

1. Before writing any code:
   - Restate the goal in your own words to confirm understanding
   - Read the relevant source files — do not assume their contents
   - Identify all files that will need to change
   - Propose the implementation approach with tradeoffs noted
   - Flag any assumptions you are making
   - Wait for the user to confirm before proceeding

2. After confirmation:
   - Implement following Core Conventions exactly
   - Match the patterns used in existing code in the same layer
   - Add inline comments for non-obvious logic
   - Add a TODO comment for any judgment call the user should review
   - Implement one file at a time

3. After implementation:
   - List any follow-up work created (tech debt, missing tests, related changes)
   - List the tests that should be written or updated

Output order: plan → confirmation → implementation → follow-up list.

## Core System Reference

This behavior operates within the Core System framework defined in the base instructions.

