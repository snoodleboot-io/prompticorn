# Skills & Workflows Mapping - Change Summary

## Current State vs Proposed State

| Agent | Current Skills | Proposed Skills | Change | Current Workflows | Proposed Workflows | Change |
|-------|----------------|-----------------|--------|-------------------|--------------------| -------|
| architect | 36 | 8 | -28 | 66 | 6 | -60 |
| ask | 36 | 5 | -31 | 66 | 3 | -63 |
| backend | 36 | 6 | -30 | 66 | 5 | -61 |
| code | 36 | 7 | -29 | 66 | 6 | -60 |
| compliance | 36 | 3 | -33 | 66 | 3 | -63 |
| data | 36 | 5 | -31 | 66 | 4 | -62 |
| debug | 36 | 3 | -33 | 66 | 3 | -63 |
| devops | 36 | 3 | -33 | 66 | 5 | -61 |
| document | 36 | 4 | -32 | 66 | 3 | -63 |
| enforcement | 36 | 3 | -33 | 66 | 3 | -63 |
| explain | 36 | 3 | -33 | 66 | 2 | -64 |
| frontend | 36 | 4 | -32 | 66 | 4 | -62 |
| incident | 36 | 4 | -32 | 66 | 3 | -63 |
| migration | 36 | 4 | -32 | 66 | 4 | -62 |
| mlai | 36 | 15 | -21 | 66 | 11 | -55 |
| observability | 36 | 4 | -32 | 66 | 5 | -61 |
| orchestrator | 36 | 4 | -32 | 66 | 4 | -62 |
| performance | 36 | 4 | -32 | 66 | 3 | -63 |
| planning | 36 | 5 | -31 | 66 | 5 | -61 |
| product | 36 | 4 | -32 | 66 | 7 | -59 |
| qa-tester | 36 | 6 | -30 | 66 | 3 | -63 |
| refactor | 36 | 5 | -31 | 66 | 3 | -63 |
| review | 36 | 5 | -31 | 66 | 4 | -62 |
| security | 36 | 4 | -32 | 66 | 7 | -59 |
| test | 36 | 6 | -30 | 66 | 3 | -63 |

---

## Key Changes

### Current State (INCORRECT):
- ❌ ALL 25 agents have ALL 36 skills
- ❌ ALL 25 agents have ALL 66 workflows
- **Problem**: No specialization, every agent can do everything

### Proposed State (CORRECT):
- ✅ Each agent has only relevant skills (3-15 skills per agent)
- ✅ Each agent has only relevant workflows (2-11 workflows per agent)
- **Benefit**: Clear specialization, agents focused on their domain

---

## Implementation Notes

To implement these changes, you need to:

1. **Update agent source definitions** in `promptosaurus/agents/{agent}/`
2. **Regenerate agent files** using the builder
3. **Verify** that each agent only lists its assigned skills and workflows

The mappings are defined in:
- `skill_mappings.json` - Which skills each agent should have
- `workflow_mappings.json` - Which workflows each agent should have
