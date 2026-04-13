# Prompt Template Source Code Updates - Design Document

**Date:** 2026-04-12  
**Purpose:** Update AI prompt templates to reference new directory structure  
**Status:** Design Complete - Ready for Implementation

---

## Overview

After migrating directory structure (docs/ → docs/ + planning/ + _temp/), the AI prompt templates (the actual source code that tells agents where to create files) need updating.

**New Structure:**
- `docs/` → User-facing documentation only
- `planning/` → Development planning (PRDs, ADRs, execution plans)
- `_temp/` → Ephemeral working files

---

## Part 1: Agent Permissions (CRITICAL)

### Issue
Architect and Planning agents have edit permissions limited to `docs/` only. They cannot create files in `planning/`.

### File: `promptosaurus/agents/architect/prompt.md`

**Current (Lines 8-10):**
```yaml
edit:
  (docs/.*\.md$|\.promptosaurus/sessions/.*\.md$): allow
  '*': deny
```

**Proposed:**
```yaml
edit:
  (docs/.*\.md$|planning/.*\.md$|\.promptosaurus/sessions/.*\.md$): allow
  '*': deny
```

**Rationale:**
- Architect needs to create ADRs in `planning/current/adrs/`
- Architect needs to update design docs in `docs/design/`
- Keep both permissions to allow finalizing docs/ when ready

---

### File: `promptosaurus/agents/planning/prompt.md`

**Current (Lines 8-10):**
```yaml
edit:
  (docs/.*\.md$|\.promptosaurus/sessions/.*\.md$): allow
  '*': deny
```

**Proposed:**
```yaml
edit:
  (docs/.*\.md$|planning/.*\.md$|\.promptosaurus/sessions/.*\.md$): allow
  '*': deny
```

**Rationale:**
- Planning agent creates PRDs in `planning/current/prds/`
- Planning agent creates ADRs in `planning/current/adrs/`
- Planning agent updates execution plans in `planning/current/execution-plans/`
- Keep docs/ for finalizing user-facing documentation

---

## Part 2: Agent Instructions

### File: `promptosaurus/agents/planning/prompt.md`

**Current (Line 14):**
```
You cannot modify code files, but you can create and modify PRD and ARD 
documents in the docs/ directory.
```

**Proposed:**
```
You cannot modify code files, but you can create and modify PRD and ARD 
documents in the planning/ directory. Place active work in planning/current/, 
move completed work to planning/complete/, and put future ideas in 
planning/backlog/. Finalize important decisions in docs/ when they become 
stable user-facing documentation.
```

**Rationale:**
- Clarifies where planning documents belong
- Explains lifecycle (current → complete → backlog)
- Distinguishes planning (internal) from docs (user-facing)

---

## Part 3: Decision Log Template

### File: `promptosaurus/agents/core/decision-log-template.md`

**Current (Lines 8-11):**
```markdown
Decision logs can be kept in:
1. **Session files** - For decisions within a single branch/work session
2. **Separate document** - `docs/DECISIONS.md` for project-wide decisions
3. **ADR format** - Architecture Decision Records in `docs/adr/` directory
```

**Proposed:**
```markdown
Decision logs can be kept in:
1. **Session files** - For decisions within a single branch/work session
2. **Planning ADRs** - Architecture Decision Records in `planning/current/adrs/`
3. **Final docs** - Important decisions in `docs/decisions/` (finalized, stable)
```

**Current (Lines 260-262):**
```markdown
### In Separate Document
For project-wide decisions:
- File: `docs/DECISIONS.md` (high-level) 
- OR `docs/adr/` (individual ADR files for major decisions)
```

**Proposed:**
```markdown
### In Planning Directory
For development planning decisions:
- Active work: `planning/current/adrs/ADR-NNN-title.md`
- Completed work: `planning/complete/adrs/ADR-NNN-title.md`
- Future exploration: `planning/backlog/adrs/DRAFT_ADR-NNN-title.md`

### In Docs Directory (Finalized Only)
For stable, user-facing architectural decisions:
- Finalized decisions: `docs/decisions/ADR-NNN-title.md`
```

**Rationale:**
- ADRs created during planning go to `planning/current/adrs/`
- When work completes, move to `planning/complete/adrs/`
- Only finalize to `docs/` when decision is stable and user-facing

---

## Part 4: Decision Log Subagents

### File: `promptosaurus/agents/ask/subagents/decision-log/minimal/prompt.md`

**Current:**
```
- Store: `docs/decisions/ADR-NNN-title.md`
```

**Proposed:**
```
- Active work: `planning/current/adrs/ADR-NNN-title.md`
- Completed: `planning/complete/adrs/ADR-NNN-title.md`
- Finalized (user-facing): `docs/decisions/ADR-NNN-title.md`
```

---

### File: `promptosaurus/agents/ask/subagents/decision-log/verbose/prompt.md`

**Current:**
```
**Location:** `docs/decisions/` or `docs/adr/`
```

**Proposed:**
```
**Location:** 
- Planning (active): `planning/current/adrs/`
- Planning (complete): `planning/complete/adrs/`
- Documentation (finalized): `docs/decisions/`
```

---

## Part 5: Decision Log Workflow

### File: `promptosaurus/workflows/decision-log-workflow/minimal/workflow.md`

**Current:**
```
Store in `docs/decisions/` or `docs/adr/`:
```

**Proposed:**
```
Store in `planning/current/adrs/` for active decisions:
```

---

### File: `promptosaurus/workflows/decision-log-workflow/verbose/workflow.md`

**Current (Lines 100-108):**
```markdown
**Directory structure:**
```
docs/
├── decisions/           # OR docs/adr/
│   ├── ADR-001-use-postgresql.md
│   ├── ADR-002-implement-caching.md
│   ├── ADR-003-migrate-to-kubernetes.md
│   └── README.md       # Index of all ADRs
```
```

**Proposed:**
```markdown
**Directory structure:**
```
planning/
├── current/
│   └── adrs/                        # Active decisions
│       ├── ADR-001-use-postgresql.md
│       ├── ADR-002-implement-caching.md
│       └── README.md
├── complete/
│   └── adrs/                        # Finished work
│       ├── ADR-003-migrate-to-kubernetes.md
│       └── README.md
└── backlog/
    └── adrs/                        # Future exploration
        ├── DRAFT_ADR-004-graphql-migration.md
        └── README.md

docs/
└── decisions/                       # Finalized, user-facing
    ├── ADR-001-database-architecture.md
    └── README.md
```
```

**Additional changes in verbose workflow (~10 references):**
- Line 102: `docs/decisions/` → `planning/current/adrs/`
- Line 237: `**Maintain a README.md in docs/decisions/:**` → `**Maintain a README.md in planning/current/adrs/:**`
- Lines 240-245: Update all paths in example commands

---

## Part 6: Scaffold Workflow

### File: `promptosaurus/workflows/scaffold-workflow/minimal/workflow.md`

**Current:**
```
├── docs/                 # Documentation
```

**No change needed** - `docs/` is correct for user documentation in scaffold

---

### File: `promptosaurus/workflows/scaffold-workflow/verbose/workflow.md`

**Current (Line 137):**
```bash
mkdir -p docs/{architecture,guides,api}
```

**No change to existing** - Scaffold creates `docs/` for user documentation (correct)

**But ADD:**
```bash
mkdir -p planning/{current,complete,backlog}/{adrs,execution-plans,features,prds}
mkdir -p planning/research
mkdir -p _temp
```

**Rationale:**
- Scaffold should create BOTH `docs/` (user-facing) and `planning/` (development)
- This ensures new projects have proper structure from start

---

## Part 7: Document Subagent

### File: `promptosaurus/agents/document/subagents/strategy-for-applications/verbose/prompt.md`

**Current:**
```
See [docs/decisions/](docs/decisions/) for ADRs.
```

**Proposed:**
```
See [planning/current/adrs/](planning/current/adrs/) for active decisions or
[docs/decisions/](docs/decisions/) for finalized architectural decisions.
```

---

## Part 8: Session Examples

### File: `promptosaurus/agents/core/session.md`

**Current (Lines 159-161):**
```markdown
- **File:** `docs/AUTH_DESIGN.md` created with full design
- **File:** `docs/AUTH_SEQUENCE.md`
- `docs/AUTH_DESIGN.md` - Full design specification
```

**Proposed:**
```markdown
- **File:** `planning/current/execution-plans/AUTH_DESIGN.md` created
- **File:** `docs/design/AUTH_ARCHITECTURE.md` (finalized design)
- `planning/current/execution-plans/AUTH_DESIGN.md` - Execution plan
```

**Rationale:**
- Planning documents go to `planning/current/`
- Final architecture goes to `docs/design/`
- Session examples should reflect new structure

---

## Summary: Files to Update

### CRITICAL (Agent Permissions - Required)
1. `promptosaurus/agents/architect/prompt.md` - Add `planning/.*\.md$` to edit permissions
2. `promptosaurus/agents/planning/prompt.md` - Add `planning/.*\.md$` to edit permissions

### HIGH PRIORITY (Instructions & Templates)
3. `promptosaurus/agents/planning/prompt.md` - Update instructions text
4. `promptosaurus/agents/core/decision-log-template.md` - Update ADR storage locations
5. `promptosaurus/agents/core/session.md` - Update example paths

### MEDIUM PRIORITY (Subagents)
6. `promptosaurus/agents/ask/subagents/decision-log/minimal/prompt.md` - Update ADR paths
7. `promptosaurus/agents/ask/subagents/decision-log/verbose/prompt.md` - Update ADR paths
8. `promptosaurus/agents/document/subagents/strategy-for-applications/verbose/prompt.md` - Update reference

### WORKFLOWS
9. `promptosaurus/workflows/decision-log-workflow/minimal/workflow.md` - Update storage path
10. `promptosaurus/workflows/decision-log-workflow/verbose/workflow.md` - Update all paths (~10 references)
11. `promptosaurus/workflows/scaffold-workflow/verbose/workflow.md` - Add planning/ creation

**Total:** 11 files

---

## Validation Plan

After implementing changes:

1. **Test architect agent:**
   - Verify can create files in `planning/current/adrs/`
   - Verify still has access to `docs/design/`
   - Verify cannot edit source code

2. **Test planning agent:**
   - Verify can create files in `planning/current/prds/`
   - Verify can create files in `planning/current/adrs/`
   - Verify cannot edit source code

3. **Test decision-log workflow:**
   - Verify creates ADRs in `planning/current/adrs/`
   - Verify README.md references are correct

4. **Test scaffold workflow:**
   - Verify creates `docs/` directory
   - Verify creates `planning/` directory structure
   - Verify creates `_temp/` directory

5. **Verify permissions:**
   - Agents still denied from editing source code
   - Agents still denied from editing other file types

---

## Implementation Order

1. **Phase 1: Permissions** (Breaks without this)
   - Update architect permissions
   - Update planning permissions
   - Test immediately

2. **Phase 2: Core Templates** (High impact)
   - Update decision-log-template.md
   - Update session.md examples
   - Update planning agent instructions

3. **Phase 3: Workflows** (User-facing)
   - Update decision-log workflows
   - Update scaffold workflow

4. **Phase 4: Subagents** (Lower priority)
   - Update decision-log subagents
   - Update document subagent

---

## Risk Assessment

**Low Risk:**
- Changes are additive (adding `planning/` permissions, not removing `docs/`)
- Agents can still write to `docs/` if needed
- Backward compatible with existing behavior

**Medium Risk:**
- If permissions regex is wrong, agents may be unable to create files
- Mitigation: Test immediately after permission changes

**No Risk:**
- Documentation/example changes don't affect functionality
- Users will see updated guidance but old behavior still works

---

## Success Criteria

- [ ] Architect can create ADRs in `planning/current/adrs/`
- [ ] Planning can create PRDs in `planning/current/prds/`
- [ ] Decision-log workflow creates files in correct location
- [ ] Scaffold workflow creates both `docs/` and `planning/`
- [ ] All agents still denied from editing source code
- [ ] No regression in existing functionality

---

## ADDITIONAL FIX: Orchestrator Permissions

**Date:** 2026-04-12  
**Issue:** Orchestrator had `'*': allow` for edit permissions

### Problem

The orchestrator is a meta-agent that coordinates workflows. It should delegate to specialized agents, not edit files directly.

**Before:**
```yaml
permissions:
  read:
    '*': allow
  edit:
    '*': allow    # ❌ WRONG - orchestrator shouldn't edit directly
  bash: allow
```

**After:**
```yaml
permissions:
  read:
    '*': allow
  edit:
    '*': deny     # ✅ CORRECT - delegates to other agents
  bash: allow
```

### Rationale

Orchestrator's role:
1. Read context to understand situation
2. Break down complex tasks
3. **Delegate** to specialized agents (code, architect, test, planning, etc.)
4. Use bash for coordination (verify, run tests, check status)
5. Synthesize results

It should NOT:
- Edit source code (delegates to `code` agent)
- Edit architecture docs (delegates to `architect` agent)
- Edit planning docs (delegates to `planning` agent)
- Edit tests (delegates to `test` agent)

### Updated File

- `promptosaurus/agents/orchestrator/prompt.md`
  - Changed: `edit: '*': allow` → `edit: '*': deny`
  - Added: Explicit delegation instructions in description

### Permission Model (Verified Correct)

| Agent Type | Edit Permissions | Rationale |
|------------|------------------|-----------|
| **Code agents** (backend, frontend, code, etc.) | `'*': allow` | Write source code |
| **Orchestrator** | `'*': deny` | Delegates, doesn't edit |
| **Review/audit** (compliance, debug, enforcement) | Reports only | Write audit reports |
| **Documentation** (architect, planning, document) | Docs + planning | Documentation work |
| **Read-only** (ask, explain) | Sessions only | Track context |


---

## Dynamic Agent List for Orchestrator

**Issue:** Orchestrator instructions should list ALL primary agents dynamically, not hardcode a subset.

### Current State

- 17 primary agents exist (architect, ask, backend, code, compliance, data, debug, devops, document, enforcement, explain, frontend, incident, migration, mlai, observability, orchestrator, performance, planning, product, qa-tester)
- This list will grow as new agents are added
- Hardcoding the list in orchestrator prompt.md becomes stale

### Solution

Use template variable `{{PRIMARY_AGENTS_LIST}}` in orchestrator prompt that gets populated during build.

**File: `promptosaurus/agents/orchestrator/prompt.md`**

```markdown
**Available primary agents for delegation:**
{{PRIMARY_AGENTS_LIST}}
```

### Implementation Required

Create new template handler: `promptosaurus/builders/template_handlers/primary_agents_handler.py`

```python
"""Template handler for PRIMARY_AGENTS_LIST variable."""

from typing import Any
from promptosaurus.agent_registry.discovery import RegistryDiscovery
from promptosaurus.builders.template_handlers.template_handler import TemplateVariableHandler


class PrimaryAgentsHandler(TemplateVariableHandler):
    """Handles {{PRIMARY_AGENTS_LIST}} template variable.
    
    Discovers all primary agents and formats them as a bulleted list
    for inclusion in orchestrator instructions.
    """
    
    def can_handle(self, variable_name: str) -> bool:
        """Check if this handler can process the variable."""
        return variable_name == "PRIMARY_AGENTS_LIST"
    
    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        """Generate formatted list of all primary agents.
        
        Returns:
            Formatted markdown list of primary agents with descriptions
        """
        from promptosaurus.registry import registry
        
        # Get all agents
        all_agents = registry.get_all_agents()
        
        # Filter to primary agents only (mode: 'primary' or 'all')
        primary_agents = [
            agent for agent in all_agents.values()
            if agent.mode in ('primary', 'all')
        ]
        
        # Sort alphabetically
        primary_agents.sort(key=lambda a: a.name)
        
        # Format as bulleted list
        lines = []
        for agent in primary_agents:
            lines.append(f"- **{agent.name}**: {agent.description}")
        
        return "\n".join(lines)
```

**Register in builder:** `promptosaurus/builders/builder.py`

```python
from promptosaurus.builders.template_handlers.primary_agents_handler import PrimaryAgentsHandler

# In Builder.__init__():
self._template_handler_registry.register_handler(PrimaryAgentsHandler())
```

### Expected Output

When built, orchestrator prompt will contain:

```markdown
**Available primary agents for delegation:**
- **architect**: System design, architecture planning, and technical decision making
- **ask**: General questions and exploratory analysis
- **backend**: Backend development and API implementation
- **code**: General code implementation and modifications
- **compliance**: Compliance and regulatory review
- **data**: Data engineering and pipeline development
- **debug**: Debugging and troubleshooting
- **devops**: Infrastructure and deployment automation
- **document**: Documentation generation and maintenance
- **enforcement**: Code standards enforcement and review
- **explain**: Code explanation and onboarding
- **frontend**: Frontend development and UI implementation
- **incident**: Incident response and management
- **migration**: Code migration and refactoring
- **mlai**: Machine learning and AI development
- **observability**: Monitoring, logging, and observability
- **orchestrator**: Coordinate multi-step workflows
- **performance**: Performance optimization and profiling
- **planning**: Product planning and requirements
- **product**: Product management and feature planning
- **qa-tester**: Quality assurance and testing
```

### Benefits

✅ Always up-to-date with current agents
✅ Automatically includes new agents when added
✅ No manual maintenance required
✅ Clear descriptions help orchestrator choose right agent

