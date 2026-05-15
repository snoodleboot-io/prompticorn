# Persona-Based Agent Filtering

## Overview

Prompticorn uses a **persona-based filtering system** to reduce cognitive overload by showing only the agents, workflows, and skills relevant to your team's roles.

Instead of generating all 25 primary agents, you select which **personas** (SDLC roles) your team uses, and Prompticorn generates only the agents needed for those roles.

## What Are Personas?

Personas represent common software development roles (SDLC personas). Each persona has a specific focus and set of agents/workflows/skills mapped to it.

**Available Personas:**

| Persona | Focus | Key Agents |
|---------|-------|------------|
| **Software Engineer** _(deprecated, use a specific variant below)_ | Writing, maintaining, and testing application code | code, test, refactor, migration |
| **Backend Software Engineer** | Backend systems, APIs, and server-side development | code, test, refactor, migration |
| **Frontend Software Engineer** | Frontend development, UI, and client-side code | code, test, refactor, migration |
| **Fullstack Software Engineer** | Full-stack development across backend and frontend | code, test, refactor, migration |
| **Architect** | System design, architecture planning, technical decisions | architect, backend, frontend, data |
| **QA/Tester** | Quality assurance, testing strategies, test automation | test, review, qa-tester |
| **DevOps Engineer** | CI/CD, infrastructure, deployment automation | code, devops, observability, incident |
| **Security Engineer** | Security reviews, threat modeling, compliance | security, review, compliance |
| **Product Manager** | Product strategy, requirements, roadmap planning | product, plan, document |
| **Data Engineer** | Data pipelines, warehouses, data quality | data, code (ETL), performance |
| **Data Scientist** | ML model training, evaluation, experimentation | mlai, code (ML), data |
| **Technical Writer** | Documentation, READMEs, user guides | document, explain |

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

  [ ] Software Engineer - Software development, implementation, and coding
  [ ] Architect - System design, architecture planning, and technical decision making
  [ ] QA/Tester - Quality assurance, testing strategies, and automated test suites
  [ ] DevOps Engineer - Automate deployment, infrastructure, CI/CD pipelines
  [... 5 more options ...]

Select one or more roles. Only agents/workflows for selected personas will be generated.
```

**Select all personas that apply to your team.** You can select multiple personas - the system will generate the **union** of all agents needed by your selected personas.

## Examples

### Example 1: Small Startup (Software Engineer Only)

**Selected Personas:**
- Software Engineer

**Generated Agents (~14 agents):**
- Universal agents (5): ask, debug, explain, plan, orchestrator
- Software Engineer agents (9): code, test, refactor, migration, review, backend, frontend, performance, enforcement

**What's Filtered Out:**
- architect, devops, security, mlai, data, product, compliance (not needed for day-to-day coding)

---

### Example 2: Full-Stack Team (Software Engineer + QA/Tester)

**Selected Personas:**
- Software Engineer
- QA/Tester

**Generated Agents (~15 agents):**
- Universal agents (5): ask, debug, explain, plan, orchestrator
- Software Engineer agents (9): code, test, refactor, migration, review, backend, frontend, performance, enforcement
- QA/Tester additional agents (1): qa-tester
- **Note:** test agent is shared by both personas (no duplication)

**Why This Works:**
- Software Engineers write application code
- QA/Testers write test code using the `test` agent (NOT the `code` agent)
- Both personas share the `test` agent
- QA/Tester gets specialized `qa-tester` agent for testing strategies and quality assurance processes

---

### Example 3: Enterprise Team (Software Engineer + DevOps + Security)

**Selected Personas:**
- Software Engineer
- DevOps Engineer
- Security Engineer

**Generated Agents (~18 agents):**
- Universal agents (5): ask, debug, explain, plan, orchestrator
- Software Engineer agents (9): code, test, refactor, migration, review, backend, frontend, performance, enforcement
- DevOps additional agents (1): devops
- Security additional agents (2): security, compliance
- **Note:** code, review, performance agents are shared across personas

**Why This Works:**
- Software Engineers write application code
- DevOps Engineers write Infrastructure-as-Code (IaC) using the `code` agent
- Security Engineers review code and infrastructure using `security` and `review` agents
- All three personas benefit from the `code`, `review`, and `performance` agents

---

## Key Design Decisions

### 1. QA/Tester Does NOT Have `code` Agent

**Why?**  
QA/Testers write **test code**, not **application code**. The `test` agent is specialized for writing tests, while the `code` agent is for application/business logic.

If your QA team also writes application code, select both "Software Engineer" and "QA/Tester" personas.

### 2. DevOps Engineer HAS `code` Agent

**Why?**  
DevOps Engineers write Infrastructure-as-Code (IaC) - Terraform, CloudFormation, Kubernetes manifests, etc. This is code, so the `code` agent is useful for them.

### 3. Data Scientist HAS `code` Agent

**Why?**  
Data Scientists write Python/R code for ML model training, feature engineering, and data processing. The `code` agent helps with general coding, while the `mlai` agent is specialized for ML-specific tasks.

### 4. Multi-Persona Selection Uses UNION Logic

**How It Works:**  
If you select "Software Engineer" + "QA/Tester", you get:
- All agents from Software Engineer
- + All agents from QA/Tester
- + Universal agents (always included)

**No Duplicates:**  
If an agent is in multiple personas (e.g., `test` is in both Software Engineer and QA/Tester), it's only generated once.

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
  - software_engineer
  - qa_tester
```

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

**A:** Yes! Each persona has workflows and skills mapped to it. For example, Software Engineer gets workflows like `code`, `testing`, `refactor`, and skills like `solid-principles`, `debugging-methodology`, etc.

### Q: Are agents from unselected personas completely unavailable?

**A:** Yes. If you select only "Software Engineer", agents like `devops`, `security`, and `mlai` will not be generated. To use them, you must select the corresponding personas.

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

  Active personas: Software Engineer, Data Scientist, Data Engineer
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
