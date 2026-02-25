# architect-task-breakdown.md
# Behavior when the user asks to break down a feature, epic, or PRD into tasks.

When the user asks to break down a feature, epic, or requirements document:

1. Read what the user provided. Only ask for clarification if something is
   genuinely ambiguous and would change how the work is broken down.
   Do not ask questions you can infer from context.

2. Break the work into discrete, independently deliverable tasks.

3. For each task output:
   - Title: verb-first (e.g., "Add rate limiting to /auth endpoint")
   - Description: what and why, not how
   - Acceptance criteria: bulleted, testable statements
   - Dependencies: which tasks must be completed first
   - Size estimate: XS / S / M / L / XL
   - Type: feat / fix / chore / spike

4. Flag any tasks that require architectural decisions before starting.

5. Suggest a logical delivery sequence.

6. Output as a structured list, not a narrative.

Size guide:
- XS: under 1 hour, trivial change
- S: half day, well-understood
- M: 1-2 days, some complexity
- L: 3-5 days, multiple moving parts
- XL: over 1 week — flag and ask the user to break it down further

Spikes have a timebox. If acceptance criteria cannot be written, the task is not ready.