# Persona-Based Agent Filtering

## Overview

prompticorn uses a **persona-based filtering system** to reduce cognitive overload by showing only the agents, workflows, and skills relevant to your team's roles.

Instead of generating all 25 primary agents (plus their subagents), you select which
**personas** (SDLC roles) your team uses, and prompticorn generates only the agents,
workflows, and skills needed for those roles.

## What Are Personas?

Personas represent common software development roles (SDLC personas). Each persona has a specific focus and set of agents/workflows/skills mapped to it.

Personas are defined in `prompticorn/personas/personas.yaml`. There are **12 persona
definitions** (3 software-engineer specializations plus a deprecated `software_engineer`
alias). The "Primary Agents" column lists each persona's primary agents from the YAML;
secondary (cross-cutting) agents and the 5 universal agents are added on top.

**Available Personas:**

| Persona | Focus | Primary Agents |
|---------|-------|----------------|
| **Software Engineer (Fullstack)** _(deprecated alias — use Fullstack Software Engineer)_ | Complete applications from UI to API to database | code, test, refactor, migration |
| **Backend Software Engineer** | Scalable backend systems, APIs, and data persistence layers | code, test, refactor, migration |
| **Frontend Software Engineer** | Performant, accessible UIs for web and mobile | code, test, refactor, migration |
| **Fullstack Software Engineer** | Full-stack development across backend and frontend | code, test, refactor, migration |
| **Architect** | System design, architecture planning, technical decisions | architect, backend, frontend, data |
| **QA / Tester** | Quality assurance, testing strategy, test automation | test, review |
| **DevOps Engineer** | Infrastructure as code, deployment, operations, CI/CD | code, devops, observability, incident |
| **Security Engineer** | Security hardening, threat modeling, and compliance | security, compliance |
| **Product Manager** | Requirements, prioritization, and roadmap planning | product |
| **Data Engineer** | Data pipelines, data quality, and data infrastructure | code, data |
| **Data Scientist** | ML, model development, and optimization | code, mlai |
| **Technical Writer** | Documentation and technical communication | document |

> Secondary agents per persona (from `personas.yaml`): for example, QA/Tester also pulls
> in `performance` and `enforcement`; Security Engineer also pulls in `incident`, `review`,
> and `enforcement`; Data Scientist also pulls in `data`, `test`, `performance`, `devops`,
> and `observability`. See `prompticorn/personas/personas.yaml` for the full lists.

## Universal Agents

Some agents are **always available** regardless of which personas you select:

- **ask** - General Q&A and research
- **debug** - Troubleshooting and error resolution  
- **explain** - Code walkthroughs and onboarding
- **plan** - Strategic planning and work planning
- **orchestrator** - Multi-step workflow coordination

These agents are fundamental and useful across all roles.

## How to Select Personas

During `prompticorn init`, you'll see this step:

```
Step 3.5: Select Personas
──────────────────────────────────────────────────────────

Which personas (SDLC roles) will be working on this codebase?

  [ ] Backend Software Engineer - Backend systems, APIs, and data persistence
  [ ] Frontend Software Engineer - Performant, accessible web/mobile UIs
  [ ] Fullstack Software Engineer - Complete apps from UI to API to database
  [ ] Architect - System design, architecture planning, technical decisions
  [ ] QA / Tester - Quality assurance, testing strategy, test automation
  [ ] DevOps Engineer - Infrastructure as code, deployment, CI/CD
  [ ] Security Engineer - Security hardening, threat modeling, compliance
  [ ] Product Manager - Requirements, prioritization, roadmap planning
  [ ] Data Engineer - Data pipelines, data quality, data infrastructure
  [ ] Data Scientist - ML, model development, optimization
  [ ] Technical Writer - Documentation and technical communication

Select one or more roles. Only agents/workflows for selected personas will be generated.
```

**Select all personas that apply to your team.** You can select multiple personas - the system will generate the **union** of all agents needed by your selected personas.

## Examples

### Example 1: Small Startup (Fullstack Software Engineer Only)

**Selected Personas:**
- Fullstack Software Engineer

**Generated Agents (~14 agents):**
- Universal agents (5): ask, debug, explain, plan, orchestrator
- Fullstack SWE primary (4): code, test, refactor, migration
- Fullstack SWE secondary (5): review, backend, frontend, performance, enforcement

**What's Filtered Out:**
- architect, devops, security, compliance, mlai, data, observability, incident, product, document (not needed for day-to-day coding)

---

### Example 2: Product Team (Fullstack Software Engineer + QA/Tester)

**Selected Personas:**
- Fullstack Software Engineer
- QA / Tester

**Generated Agents (~15 agents):**
- Universal agents (5): ask, debug, explain, plan, orchestrator
- Fullstack SWE agents (9): code, test, refactor, migration, review, backend, frontend, performance, enforcement
- QA/Tester adds (0 new primary): test and review are shared; qa-tester is the standalone agent, with performance and enforcement as shared secondaries
- **Note:** `test`, `review`, `performance`, and `enforcement` are shared across both personas (no duplication)

**Why This Works:**
- Fullstack engineers write application code with the `code` agent
- QA/Testers center on the `test` and `review` agents rather than `code`
- The `qa-tester` agent provides specialized testing-strategy and quality-assurance subagents (unit, integration, e2e, load)

---

### Example 3: Enterprise Team (Fullstack Software Engineer + DevOps + Security)

**Selected Personas:**
- Fullstack Software Engineer
- DevOps Engineer
- Security Engineer

**Generated Agents (~18 agents):**
- Universal agents (5): ask, debug, explain, plan, orchestrator
- Fullstack SWE agents (9): code, test, refactor, migration, review, backend, frontend, performance, enforcement
- DevOps adds: devops, observability, incident (code is shared)
- Security adds: security, compliance (review, incident, enforcement are shared secondaries)
- **Note:** `code`, `review`, `performance`, `enforcement`, and `incident` are shared across personas

**Why This Works:**
- Fullstack engineers write application code
- DevOps Engineers write Infrastructure-as-Code (IaC) using the `code` agent
- Security Engineers review code and infrastructure using `security`, `compliance`, and `review` agents
- All three personas benefit from shared cross-cutting agents

---

## Key Design Decisions

### 1. QA/Tester Does NOT Have `code` Agent

**Why?**  
QA/Testers write **test code**, not **application code**. The `test` agent is specialized for writing tests, while the `code` agent is for application/business logic.

If your QA team also writes application code, select both a software-engineer persona (e.g. "Fullstack Software Engineer") and "QA / Tester".

### 2. DevOps Engineer HAS `code` Agent

**Why?**  
DevOps Engineers write Infrastructure-as-Code (IaC) - Terraform, CloudFormation, Kubernetes manifests, etc. This is code, so the `code` agent is useful for them.

### 3. Data Scientist HAS `code` Agent

**Why?**  
Data Scientists write Python/R code for ML model training, feature engineering, and data processing. The `code` agent helps with general coding, while the `mlai` agent is specialized for ML-specific tasks.

### 4. Multi-Persona Selection Uses UNION Logic

**How It Works:**  
If you select "Fullstack Software Engineer" + "QA / Tester", you get:
- All agents from Fullstack Software Engineer
- + All agents from QA / Tester
- + Universal agents (always included)

**No Duplicates:**  
If an agent is in multiple personas (e.g., `test` and `review` are in both Fullstack Software Engineer and QA / Tester), it's only generated once.

---

## Configuration File

Your selected personas are stored in `.prompticorn/.prompticorn.yaml`:

```yaml
version: "1.0"
repository:
  type: single-language
spec:
  language: python
  ...
variant: minimal
active_personas:
  - fullstack_software_engineer
  - qa_tester
```

> Persona keys use snake_case as defined in `prompticorn/personas/personas.yaml` (for
> example `backend_software_engineer`, `frontend_software_engineer`,
> `fullstack_software_engineer`, `qa_tester`, `devops_engineer`, `security_engineer`,
> `product_manager`, `data_engineer`, `data_scientist`, `technical_writer`). The
> `software_engineer` key remains as a deprecated alias for `fullstack_software_engineer`.

## Changing Personas Later

**Option 1: Re-initialize**
```bash
# Back up your existing config
cp .prompticorn/.prompticorn.yaml .prompticorn/.prompticorn.yaml.backup

# Re-run init (will regenerate agents based on new persona selection)
prompticorn init
```

**Option 2: Manual Edit**
```bash
# Edit .prompticorn/.prompticorn.yaml
# Change the active_personas list
# Then regenerate agents:
prompticorn init
```

---

## Frequently Asked Questions

### Q: What if I select all personas?

**A:** You'll get all ~25 primary agents. This defeats the purpose of persona filtering but is allowed if your team truly uses all roles.

### Q: What if I select no personas?

**A:** You'll only get the 5 universal agents (ask, debug, explain, plan, orchestrator). Not recommended unless you have a very specific use case.

### Q: Can I add custom personas?

**A:** Not currently. Personas are defined in `prompticorn/personas/personas.yaml`. Custom personas may be supported in a future release.

### Q: Do personas affect workflows and skills too?

**A:** Yes! Each persona has workflows and skills mapped to it (in `personas.yaml`, with
agent-level detail in `prompticorn/configurations/agent_skill_mapping.yaml`). For example,
the software-engineer personas get workflows like `code`, `testing`, and `refactor`, and
skills like `incremental-implementation`, `code-review-practices`, `testing-strategies`,
and `debugging-methodology`.

### Q: Are agents from unselected personas completely unavailable?

**A:** Yes. If you select only a software-engineer persona, agents like `devops`, `security`, and `mlai` will not be generated. To use them, you must select the corresponding personas.

---

## Changing Personas

If your team's roles change over time, you can swap which personas are active:

### Using the swap command

```bash
prompticorn swap
```

This interactive command will:
1. Show all available personas with your current selections marked
2. Let you change which personas are active (multi-select)
3. Show a diff of what changed (added/removed personas)
4. Remove old AI assistant configurations
5. Regenerate configurations with only the newly selected personas
6. Save the updated configuration

**Example output:**

```
Persona Changes
────────────────────────────────────────────────────────────
  Removed: DevOps Engineer
  Added: Data Scientist, Data Engineer

Removing old artifacts...
    Removed directory: .kilo/

Regenerating kilo-ide configuration...
    ✓ .kilo/agents/data.md
    ✓ .kilo/agents/mlai.md
    ...

Personas swapped successfully!

  Active personas: Fullstack Software Engineer, Data Scientist, Data Engineer
```

**When to use swap:**
- Your team adds or removes roles (e.g., hired a DevOps engineer)
- Project focus shifts (e.g., adding ML/data science work)
- Reducing scope (e.g., removing unused personas to declutter)

---


## Reference

For the complete agent-to-persona mapping matrix and design rationale, see:
- **ADR-001:** `planning/current/adrs/ADR-001-persona-based-filtering.md`
- **Personas YAML:** `prompticorn/personas/personas.yaml`

---

## Summary

**Benefits of Persona Filtering:**
- ✅ Reduces cognitive overload (14 agents vs 25 agents for a typical developer)
- ✅ Focuses on relevant agents for your team's roles
- ✅ Maintains flexibility (select multiple personas for multi-role teams)
- ✅ Universal agents ensure core functionality is always available

**Best Practice:**
Select the personas that match your team's actual roles. Most small teams will select 1-3 personas, which provides a focused set of ~14-18 agents instead of all 25.
