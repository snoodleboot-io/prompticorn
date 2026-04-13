---
name: workflow-orchestration-patterns
description: Design and implement workflow orchestration patterns for coordinating multi-step processes and distributed task execution
type: workflow
category: workflow-patterns
minimal: true
---

# Workflow Orchestration Patterns

## Sequential Orchestration
- Execute tasks one after another
- Wait for completion before proceeding
- Best for: Dependent tasks with clear order

## Parallel Orchestration
- Execute independent tasks simultaneously
- Collect results before proceeding
- Best for: Concurrent independent work

## Conditional Orchestration
- Branch execution based on conditions
- Execute different paths based on outcomes
- Best for: Decision-driven workflows

## Fan-Out / Fan-In Pattern
- Distribute work to multiple workers (fan-out)
- Collect and aggregate results (fan-in)
- Best for: Batch processing at scale

## Compensation Pattern
- Execute forward steps with rollback capability
- Undo previous steps on failure
- Best for: Long-running transactions
