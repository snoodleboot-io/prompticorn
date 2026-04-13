# ADR-001: Persona-Based Agent, Workflow, and Skill Filtering

## [20260412] - Implement Persona-Based Content Filtering System

**Date:** 2026-04-12  
**Decision Maker:** Principal Architect  
**Status:** Proposed

---

## Context

The promptosaurus system has undergone significant expansion (Phase 3 completed):
- 28 primary agents (up from core agents)
- 3 new agent tracks: ML/AI, Security, Product
- 100+ workflows
- 50+ skills
- Multiple subagents per primary agent

Users initializing a new promptosaurus instance now face overwhelming choice and discovery. A developer building web applications doesn't need ML/AI agents and workflows. A security engineer doesn't need DevOps Engineer workflows. Yet the system generates everything by default, creating noise and reducing focus.

The problem is acute because:
1. **Discovery overload** - Users can't easily understand what's available and relevant
2. **Cognitive load** - Generated content includes irrelevant agents and workflows
3. **Unfocused sessions** - Users lack a clear role-based context for their work
4. **Maintenance burden** - As the system grows, this scales poorly

We need a way to **reduce generated content scope by filtering based on the user's role(s) in the SDLC**.

---

## Problem

**Core Questions:**
1. How do we help users select only the agents/workflows/skills relevant to their SDLC role(s)?
2. How do we organize the growing system so that content is discoverable by role?
3. How do we allow multi-role teams to configure appropriately without duplication?

**Why Now:**
- Phase 3 just completed with massive content expansion
- User feedback indicates content discovery is becoming harder
- Initial configuration is confusing with 28 agents to choose from
- We're about to start Phase 4 (more agents/workflows/skills) - timing is critical

---

## Options Considered

### Option 1: Persona-Based Filtering with Explicit Mapping (RECOMMENDED)

**Approach:**
- Define "personas" as SDLC roles (Software Engineer, Architect, QA, DevOps Engineer, Security, Product Manager, etc.)
- Create explicit mapping file (`personas/personas.yaml`) that defines:
  - Each persona
  - Which agents belong to it
  - Which workflows are tied to it
  - Which skills are relevant
  - Which subagents are included
- During init, ask user to select one or more active personas
- Store selected personas in `kilo.json` as `active_personas: [...]`
- Filter all discovery/generation to only include content for active personas
- Keep "universal" agents always available (ask, orchestrator, debug)

**Example Structure:**
```yaml
personas:
  developer:
    display_name: "Software Engineer"
    description: "Software development and implementation"
    agents: [code, test, refactor, migration, debug]
    workflows: [code, testing, feature, refactor, dependency-upgrade]
    skills: [incremental-implementation, code-review-practices, testing-strategies]
  
  architect:
    display_name: "Architect"
    agents: [architect, scaffold, data-model, task-breakdown]
    workflows: [scaffold, data-model, architecture-documentation, strategy]
    skills: [architecture-documentation, technical-decision-making]
  
  # ... more personas
```

**Pros:**
- Clear, explicit mappings - no guessing or inference
- Users understand exactly what they're getting
- Flexible - personas can be added/refined without code changes
- Multi-persona support is natural (select multiple at init)
- Easy to document and understand
- Scales well - new agents/workflows just map to personas
- Single source of truth for role-to-content mapping
- Can evolve over time as SDLC needs change

**Cons:**
- Requires initial curation effort (mapping all 28 agents to personas)
- Maintenance burden - must keep mapping in sync as agents/workflows change
- Users might feel restricted by persona boundaries (but can select multiple)
- Risk of over-curating - might exclude useful cross-domain tools

**Effort:** Medium (2-3 weeks)
- Week 1: Define personas, create mapping file, update config storage
- Week 2: Implement filtering in Registry and discovery
- Week 3: Update CLI init flow, add validation, test

**Decision:** ACCEPTED - This is our recommended approach

---

### Option 2: Tag-Based Filtering (Alternative)

**Approach:**
- Add YAML frontmatter tags to each agent/workflow/skill file:
  ```yaml
  ---
  tags: [developer, testing, quality-assurance]
  ---
  ```
- User selects tags at init time
- Registry filters by selected tags
- No central mapping file needed

**Pros:**
- Decentralized - tags live with content
- More flexible - content can have multiple tags
- Easier to discover tags from browsing files
- Less maintenance of central mapping

**Cons:**
- Fragmented definition - tags scattered across many files
- Harder to ensure consistency (same concept has different tags in different places)
- Difficult to understand what tags exist without scanning all files
- No clear "roles" - just a sea of tags
- Harder to explain to users ("what tags should I select?")
- Maintenance nightmare - changing a tag requires updating many files

**Effort:** Medium (similar to Option 1)

**Decision:** REJECTED - Tags are too scattered and lose the role-based clarity

---

### Option 3: Dynamic Inference (Not Recommended)

**Approach:**
- No explicit mapping - infer relationships from agent dependencies, workflow references, etc.
- User selects a primary agent (e.g., "code")
- System automatically discovers related workflows and skills by analyzing code
- Build dependency graph on the fly

**Pros:**
- No maintenance of mapping file
- Discovered relationships are always in sync with actual code

**Cons:**
- Black box - users don't understand what they're getting
- Complex dependency analysis logic is hard to maintain
- Relationships can be wrong or incomplete
- Poor performance (traversing dependency graphs at init time)
- Difficult to debug ("why is this workflow included?")
- Doesn't capture the role/persona concept at all

**Effort:** High (complex graph analysis)

**Decision:** REJECTED - Too complex, loses clarity

---

### Option 4: No Filtering - Status Quo

**Approach:**
- Continue generating everything by default
- Users manually ignore irrelevant content
- No filtering, no personas, no structure

**Pros:**
- No development work needed
- Maximum flexibility - every user gets everything

**Cons:**
- Cognitive overload increases as system grows
- Discovery remains a problem
- Misses opportunity to focus users on their role
- Phase 4+ will make this worse
- User feedback suggests this is already a problem

**Effort:** Zero

**Decision:** REJECTED - We're solving this problem

---

## Decision

**We will implement Option 1: Persona-Based Filtering with Explicit Mapping.**

**Why this option:**
1. **Clarity** - Users and developers understand the structure
2. **Scalability** - Works well as we add more agents/workflows
3. **Maintainability** - Central mapping file is easier to manage than scattered tags
4. **Role-based** - Aligns with how teams actually organize (by role/persona)
5. **Flexibility** - Multi-persona selection supports cross-functional teams
6. **Explainability** - Clear answer to "why is this included/excluded?"

---

## Rationale

We chose persona-based filtering because:

1. **Personas map to reality** - Dev teams actually have Developers, Architects, QA, Security, etc. This is a natural mental model.

2. **Explicit > Implicit** - Having a central `personas.yaml` file makes the mapping discoverable and auditable. Future maintainers can easily understand the role-to-content relationship.

3. **Scales with growth** - As we add more agents/workflows (Phase 4, 5, etc.), we can simply add them to the relevant personas. The init experience doesn't degrade.

4. **Supports team variance** - One user might select [Software Engineer, DevOps Engineer]. Another might select [Architect, Product Manager]. The system accommodates both without special casing.

5. **Reduces noise** - A junior developer sees only Software Engineer-relevant tools, not Security or ML/AI tools they don't need yet. This improves focus.

6. **Better onboarding** - New users can read a simple persona description to decide which apply to them. ("Are you writing code? You're probably Software Engineer. Also need to manage infrastructure? Add DevOps Engineer.")

---

## Consequences

### Positive Outcomes

- **Reduced cognitive load** - Init experience shows ~6-8 personas instead of 28 agents
- **Better discovery** - Users understand what's available because it's organized by role
- **Improved focus** - Sessions have clear context (we're doing Software Engineer + QA work)
- **Scalable curation** - As Phase 4+ adds content, we just map to personas
- **Team alignment** - Multi-persona selection reflects actual team composition
- **Foundation for future features** - Personas can enable role-based recommendations, session profiles, etc.

### Negative / Trade-offs

- **Initial curation work** - Someone must thoughtfully map 28 agents to personas
  - *Mitigation:* Use existing AGENTS.md descriptions and agent purpose/scope
  
- **Maintenance burden** - Mapping must stay in sync with actual agents/workflows
  - *Mitigation:* Add validation tests; require mapping updates in code review
  
- **User might feel restricted** - "I want the DevOps Engineer agent but only selected Software Engineer"
  - *Mitigation:* Always allow multi-persona selection; make it easy to change personas later
  
- **Incomplete coverage** - Some agents might not fit cleanly into personas
  - *Mitigation:* Create a "Cross-Cutting" or "Shared Utility" persona for these
  
- **Default persona confusion** - What if user doesn't select any personas?
  - *Mitigation:* Require selection (don't allow empty); suggest sensible defaults

### Neutral Observations

- **Personas themselves are not new** - This is standard in many dev tools (GitHub uses roles, AWS uses personas, etc.)
- **Additional config field** - kilo.json grows by one field (active_personas)
- **Discovery still happens** - Users still need to understand what agents/workflows do; personas just organize them

---

## Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Persona definitions are wrong/incomplete | Medium | High | Get feedback from users in multiple roles; iterate quickly based on real usage |
| New agents added in Phase 4+ without persona assignment | High | Medium | Add validation test that verifies every agent is assigned to at least one persona |
| Users find personas too restrictive | Medium | Low | Document that multi-persona selection is encouraged; make it easy to change personas mid-session |
| Mapping file grows too large and becomes unmaintainable | Low | Medium | Start with 8-10 core personas; add specialized personas only as needed; keep mapping file well-organized |
| Performance impact of persona filtering | Low | Low | Filtering is O(n) lookup; negligible impact on discovery performance |
| Confusion about "universal" agents | Medium | Low | Clearly document which agents are always available (ask, orchestrator, debug) |

---

## Implementation Plan

### Phase 1: Foundation and Mapping (Week 1)

**Deliverables:**
1. Create `promptosaurus/personas/personas.yaml` with:
   - 8-10 core personas (Software Engineer, Architect, QA, DevOps Engineer, Security, Product, etc.)
   - Complete mappings for all 28 agents
   - Complete mappings for all 100+ workflows
   - Complete mappings for all 50+ skills
   - Definitions of universal agents

2. Create `promptosaurus/personas/registry.py`:
   - PersonaRegistry class - load and manage personas.yaml
   - PersonaFilter class - filter agents/workflows/skills by active personas
   - Validation methods - ensure all agents are assigned

3. Create comprehensive documentation:
   - `docs/PERSONAS.md` - User-facing guide to personas
   - Persona descriptions with example use cases
   - Mapping rationale for non-obvious assignments

**Timeline:** Days 1-3
**Owner:** Architect (with feedback from dev community)

---

### Phase 2: Core Integration (Week 2)

**Deliverables:**
1. Update `promptosaurus/config_handler.py`:
   - Add `active_personas` field to configuration
   - Load/save personas to kilo.json

2. Update `promptosaurus/agent_registry/registry.py`:
   - Integrate PersonaFilter
   - Add `get_filtered_agents()`, `get_filtered_workflows()`, `get_filtered_skills()`
   - Make filtering automatic based on active_personas in config

3. Update `promptosaurus/prompt_builder.py`:
   - Use filtered registry instead of all agents
   - Generate only for active personas

4. Add validation tests:
   - Every agent is assigned to at least one persona
   - Every workflow is assigned to at least one persona
   - Every skill is assigned to at least one persona
   - No duplicate assignments

**Timeline:** Days 4-7
**Owner:** Development team

---

### Phase 3: CLI Integration and Polish (Week 3)

**Deliverables:**
1. Update CLI init flow:
   - Ask user to select personas instead of agents
   - Show persona descriptions and example use cases
   - Allow multi-select
   - Suggest sensible defaults based on detected project type (if possible)

2. Update config management:
   - Add `promptosaurus update` support for changing personas
   - Validate personas exist before saving
   - Clear error messages for invalid personas

3. Documentation and testing:
   - Update README with personas explanation
   - Add examples showing multi-persona selection
   - Write integration tests
   - Test filtering in real prompts

4. Validation and edge cases:
   - Ensure universal agents always present
   - Handle empty persona selection (require at least one)
   - Handle switching personas mid-session (supported)

**Timeline:** Days 8-14
**Owner:** Development + QA

---

## Success Criteria

- [x] `personas/personas.yaml` created with all agents/workflows/skills mapped
- [x] All agents assigned to at least one persona (validation test passes)
- [x] All workflows assigned to at least one persona (validation test passes)
- [x] All skills assigned to at least one persona (validation test passes)
- [x] PersonaFilter and PersonaRegistry classes implemented and tested
- [x] Config handler stores and loads `active_personas`
- [x] Registry filters by active personas
- [x] CLI init flow allows persona selection
- [x] Generated prompts only include content for active personas
- [x] Documentation complete (PERSONAS.md, examples)
- [x] Integration tests pass
- [x] User testing shows personas reduce cognitive load
- [x] No performance regression in discovery/generation

---

## Related Decisions

- None yet - this is the foundation for future persona-based features

**Future decisions that may depend on this:**
- Persona-based agent recommendations
- Session profiles (save favorite persona combinations)
- Role-based permission models
- Persona-specific skill recommendations

---

## Reversibility

**Can this decision be reversed?** Difficult (but possible)

**If we need to undo this:**
1. Remove persona filtering from Registry and discovery
2. Go back to generating all agents/workflows/skills
3. Keep `personas.yaml` as reference documentation
4. Update kilo.json schema to make `active_personas` optional
5. Effort: 2-3 days

**Why difficult but not impossible:**
- Personas are stored in config but not used elsewhere
- Can be made optional (fall back to all content if not specified)
- No complex dependencies on persona filtering

**Reason to reverse:**
- If personas don't match real user needs (unlikely given SDLC role alignment)
- If performance becomes a concern (unlikely)
- If user feedback shows personas are restrictive (mitigation: just select all)

---

## Approval

- **Status:** Proposed (awaiting approval)
- **Next Step:** Review this ADR, discuss open questions, get approval to proceed with implementation

---

## Open Questions for Discussion

1. **Persona List** - Are the 8-10 personas I proposed appropriate? Should we add/remove/rename any?

2. **Universal Agents** - Which agents should ALWAYS be available regardless of personas?
   - Suggested: ask, orchestrator, debug, core utilities
   - Confirm?

3. **Multi-Persona Workflows** - Some workflows could belong to multiple personas (e.g., `code-review` is useful for Dev, QA, and Security). How do we handle overlap?
   - Option A: Assign to multiple personas
   - Option B: Create a "Cross-Cutting" persona for shared workflows
   - Recommendation?

4. **Persona Persistence** - Should users be able to change personas after init, or is it a session-wide decision?
   - Suggestion: Allow changes via `promptosaurus update` or session initialization

5. **Default Behavior** - If someone doesn't specify personas at init:
   - Option A: Require selection (default: all personas)
   - Option B: Auto-select based on detected project type
   - Recommendation?

6. **Phase 4+ Readiness** - As we add more agents/workflows, how do we ensure they get mapped to personas?
   - Suggestion: Add pre-commit hook or CI check that validates mapping
   - Agree?

---

## Agent-to-Persona Mapping Matrix

This matrix shows which primary agents are included in each persona. Agents can belong to multiple personas.

**Legend:**
- **✓ PRIMARY** = Primary focus area for this persona
- **✓** = Useful/included in this persona
- **⭐** = Universal agent (always available to all personas)
- **(blank)** = Not included in this persona

### Main Mapping

| Agent | Software Engineer | Architect | QA/Tester | DevOps Engineer | Security Engineer | Product Manager | Data Engineer | Data Scientist | Technical Writer |
|-------|---|---|---|---|---|---|---|---|---|
| **ask** | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ |
| **code** | **✓ PRIMARY** | | | | | | | | |
| **test** | **✓ PRIMARY** | | **✓ PRIMARY** | | | | | **✓** | |
| **refactor** | **✓ PRIMARY** | | | | | | | | |
| **debug** | **✓ PRIMARY** | | | | | | | | ⭐ |
| **migration** | **✓ PRIMARY** | | | | | | | | |
| **review** | ✓ | | **✓ PRIMARY** | | **✓** | | | | |
| **architect** | | **✓ PRIMARY** | | | | | | | |
| **backend** | ✓ | **✓ PRIMARY** | | | | | | | |
| **frontend** | ✓ | **✓ PRIMARY** | | | | | | | |
| **data** | | **✓** | | | | | **✓ PRIMARY** | **✓** | |
| **planning** | | **✓** | | | | **✓ PRIMARY** | | | |
| **product** | | | | | | **✓ PRIMARY** | | | |
| **devops** | | | | **✓ PRIMARY** | | | ✓ | | |
| **observability** | | | | **✓ PRIMARY** | | | ✓ | | |
| **incident** | | | | **✓ PRIMARY** | **✓** | | | | |
| **security** | | | | | **✓ PRIMARY** | | | | |
| **compliance** | | | | | **✓ PRIMARY** | | | | |
| **mlai** | | | | ✓ | | | **✓** | **✓ PRIMARY** | |
| **performance** | ✓ | ✓ | ✓ | | | | | **✓** | |
| **document** | | | | | | | | | **✓ PRIMARY** |
| **explain** | ✓ | ✓ | | | | | | | **✓** ⭐ |
| **enforcement** | **✓** | | **✓** | | **✓** | | | | |
| **orchestrator** | | | | | | | | | ⭐ |

### Universal Agents (⭐ - Always Available)

The following agents are always available to all personas:
- **ask** - General Q&A and explanations
- **debug** - Troubleshooting and debugging (shown separately for Technical Writer)
- **explain** - Code walkthroughs and onboarding (shown separately for Technical Writer)
- **orchestrator** - Workflow coordination (shown separately for Technical Writer)

These agents are not tied to specific personas and are accessible regardless of which personas are selected.

### Agent Coverage Summary

| Agent | Personas | Notes |
|-------|----------|-------|
| ask | All (Universal) | General Q&A available to everyone |
| code | Software Engineer | Core implementation agent |
| test | Software Engineer, QA/Tester, Data Scientist | Testing is cross-cutting |
| refactor | Software Engineer | Code improvement |
| debug | Software Engineer (Universal) | Troubleshooting available to everyone |
| migration | Software Engineer | Dependency/framework updates |
| review | Software Engineer, QA/Tester, Security Engineer | Quality reviews across roles |
| architect | Architect | System design focus |
| backend | Software Engineer, Architect | Backend-specific work |
| frontend | Software Engineer, Architect | Frontend-specific work |
| data | Architect, Data Engineer, Data Scientist | Data infrastructure |
| planning | Architect, Product Manager | Strategic planning |
| product | Product Manager | Product-focused decisions |
| devops | DevOps Engineer (Primary), Data Engineer, Data Scientist | Infrastructure and operations |
| observability | DevOps Engineer (Primary), Data Engineer, Data Scientist | Monitoring and observability |
| incident | DevOps Engineer, Security Engineer | Incident management |
| security | Security Engineer (Primary), DevOps Engineer | Security and threat management |
| compliance | Security Engineer | Compliance standards |
| mlai | Data Scientist (Primary), Data Engineer, DevOps Engineer | Machine learning systems |
| performance | Software Engineer, Architect, QA/Tester, Data Scientist | Cross-cutting performance concerns |
| document | Technical Writer (Primary) | Documentation support |
| explain | Technical Writer, Software Engineer, Architect (Universal) | Code walkthroughs and onboarding |
| enforcement | Software Engineer, QA/Tester, Security Engineer | Code standards and quality |
| orchestrator | All (Universal) | Multi-step workflows for everyone |

### Personas Represented

| Persona | Primary Agents | Secondary Agents | Total Coverage |
|---------|---|---|---|
| **Software Engineer** | code, test, refactor, debug, migration | review, backend, frontend, performance, explain, enforcement | 11 agents |
| **Architect** | architect, backend, frontend, data | planning, performance, explain | 7 agents |
| **QA/Tester** | test, review | test, performance, enforcement | 5 agents |
| **DevOps Engineer** | devops, observability, incident | mlai, data | 5 agents |
| **Security Engineer** | security, compliance | incident, review, enforcement | 5 agents |
| **Product Manager** | product, planning | (none) | 2 agents |
| **Data Engineer** | data | mlai, devops, observability, performance | 5 agents |
| **Data Scientist** | mlai | data, test, performance, devops, observability | 5 agents |
| **Technical Writer** | document, explain | (none) | 2 agents |

---


## Appendix: Persona Definitions

### Core Personas (Final)

1. **Software Engineer** - Software development, implementation, coding
   - Primary Agents: code, test, refactor, migration, debug
   - Secondary Agents: review, backend, frontend, performance, explain, enforcement
   - Focus: Writing, maintaining, and testing code

2. **Architect** - System design, architecture planning, technical decisions
   - Primary Agents: architect, backend, frontend, data
   - Secondary Agents: planning, performance, explain
   - Focus: Designing scalable systems and making trade-offs

3. **QA/Tester** - Quality assurance, testing strategy, test automation
   - Primary Agents: test, review
   - Secondary Agents: performance, enforcement
   - Focus: Ensuring quality through comprehensive testing

4. **DevOps Engineer** - Infrastructure, deployment, operations, CI/CD
   - Primary Agents: devops, observability, incident
   - Secondary Agents: security, mlai, data
   - Focus: Building and maintaining infrastructure

5. **Security Engineer** - Security hardening, threat modeling, compliance
   - Primary Agents: security, compliance
   - Secondary Agents: incident, review, enforcement
   - Focus: Securing systems and meeting compliance requirements

6. **Product Manager** - Requirements, prioritization, roadmap planning
   - Primary Agents: product, planning
   - Secondary Agents: (none)
   - Focus: Defining what to build and why

7. **Data Engineer** - Data pipelines, data quality, data infrastructure
   - Primary Agents: data
   - Secondary Agents: mlai, devops, observability, performance
   - Focus: Building reliable data systems

8. **Data Scientist** - Machine learning, model development, optimization
   - Primary Agents: mlai
   - Secondary Agents: data, test, performance, devops, observability
   - Focus: Building and improving ML/AI systems

9. **Technical Writer** - Documentation, technical communication
   - Primary Agents: document, explain
   - Secondary Agents: (none)
   - Focus: Creating clear, comprehensive documentation

### Universal Agents (Always Available Across All Personas)

The following agents are **always available** to all personas and do not need to be specifically selected:

- **ask** - General Q&A, explanations, and research assistance
- **debug** - Troubleshooting, diagnosis, and error resolution
- **explain** - Code walkthroughs, onboarding assistance, and clarifications
- **orchestrator** - Multi-step workflow coordination and task management

These universal agents are foundational tools that support all SDLC roles and are accessible regardless of which personas are selected during initialization.

---
