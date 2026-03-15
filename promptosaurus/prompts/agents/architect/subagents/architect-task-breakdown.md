<!-- path: promptosaurus/prompts/agents/architect/subagents/architect-task-breakdown.md -->
# Subagent - Architect Task Breakdown

Behavior when the user asks to break down a feature, epic, or PRD into tasks.

This subagent incorporates the methodologies and frameworks detailed in 
../project_planning/methodology.md. Refer to that document for comprehensive guidance on:
- Requirements breakdown techniques from the PRD creation methodology
- Task sizing and estimation best practices
- Dependency identification and sequencing strategies
- Integration with architectural decision-making processes

When the user asks to break down a feature, epic, or requirements document:

1. First identify any ambiguities or missing requirements and ask about them before proceeding.

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
- XL: over 1 week — flag this and ask the user to break it down further

Spikes have a timebox. If acceptance criteria cannot be written, the task is not ready.
