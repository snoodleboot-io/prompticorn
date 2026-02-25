<!-- path: flat/orchestrator-meta.md -->
# orchestrator-meta.md
# Behavior for PR descriptions, retros, and cross-cutting process tasks.

## PR Description

When the user asks to write a PR description:
- Read the git diff or commit log if not provided — run git diff or git log directly
- Generate a description with these sections:
  - What: one paragraph describing what changed, from the reviewer's perspective
  - Why: the problem this solves or goal it achieves
  - How: the approach taken and any non-obvious design decisions
  - Testing: how it was tested, what to check manually
  - Checklist: tests added, docs updated, no hardcoded secrets, breaking changes noted
- Tone: professional and concise
- Write for a reviewer who knows the codebase but has not seen this work
- Ask for ticket ID and branch name if not provided

## Sprint Retrospective

When the user asks to facilitate or summarize a retro:

If facilitating interactively, ask these questions one at a time:
1. What went well this sprint?
2. What was frustrating or slowed the team down?
3. What did you learn about the codebase, team, or problem?
4. What would you do differently if you ran this sprint again?
5. What should you START, STOP, or KEEP doing?
6. What needs a follow-up decision?

After collecting answers, output:
- What Went Well
- What Did Not Work
- Key Learnings
- Action Items (specific, ownable, with owner and due date)
- Decisions Needed

If summarizing from raw notes, apply the same output format.
Rewrite vague action items as concrete ones or flag them as too vague to action.
