# Kilo: Updated Execution Model (Official Docs)

**Source:** https://kilo.ai/docs/customize (Official Kilo Code Documentation)  
**Status:** ✅ HIGH CONFIDENCE - From official kilo.ai documentation  
**Date:** 2026-04-09

---

## Kilo IDE/CLI Architecture

Kilo now has **unified customization** across IDE (VS Code) and CLI based on **agents** instead of "modes". The architecture includes:

### 1. Custom Agents (Previously "Modes")

**Storage:**
- Project: `.kilo/agents/*.md` or `kilo.jsonc` config
- Global: `~/.config/kilo/agents/*.md` or `~/.config/kilo/kilo.jsonc`

**Format:** Markdown with YAML frontmatter

```markdown
---
description: Specialized for writing technical documentation
mode: primary
color: "#10B981"
model: anthropic/claude-sonnet-4-20250514
temperature: 0.3
permission:
  edit:
    "*.md": "allow"
    "*": "deny"
  bash: deny
---

You are a technical documentation specialist...
```

**Properties:**
- `name`: Agent name (from filename or config key)
- `description`: What the agent does, when to use
- `mode`: `primary` (user-selectable), `subagent` (invoked by other agents), `all` (both)
- `model`: Pin specific model (`provider/model` format)
- `prompt`: System prompt (markdown body or inline)
- `permission`: Tool access control (read, edit, bash, etc.)
- `temperature`/`top_p`: Sampling parameters
- `steps`: Max agentic iterations
- `color`: UI color in agent picker
- `hidden`/`disable`: UI visibility control

**Built-in Agents:** code, plan, debug, ask, orchestrator, explore, general

**Overriding Built-in Agents:**
```json
{
  "agent": {
    "code": {
      "model": "openai/gpt-4o",
      "temperature": 0.2,
      "permission": {
        "edit": {
          "*.py": "allow",
          "*": "deny"
        }
      }
    }
  }
}
```

### 2. Custom Subagents

**Purpose:** Specialized agents invoked by primary agents or manually via `@agent-name`

**Characteristics:**
- Isolated context (separate session)
- Tailored prompts and tool access
- Run in their own conversation history
- Results flow back to parent agent

**Built-in Subagents:**
- `general` - General-purpose research and multi-step tasks (full access)
- `explore` - Fast read-only codebase exploration

**Usage:**
```
@code-reviewer review the authentication module for security issues
```

**Configuration:** Same as primary agents but with `mode: subagent`

### 3. Workflows (Slash Commands)

**Storage:** `.kilo/commands/*.md` or global `~/.config/kilo/commands/`

**Invocation:** `/command-name` in chat

**Format:** Markdown with optional YAML frontmatter

```markdown
---
description: Submit a pull request with full checks
agent: code
---

# Submit PR Workflow

You are helping submit a pull request. Follow these steps:

1. Check for TODO comments using `grep`
2. Run tests with `bash` (npm test)
3. Stage and commit with descriptive message
4. Push branch and create PR with `gh pr create`
```

**Frontmatter Options:**
- `description`: Shown in command picker
- `agent`: Which agent to use
- `model`: Model override
- `subtask`: Run as sub-agent session if true

**Capabilities:** Can use all tools
- read, glob, grep, edit, write, bash
- webfetch
- MCP server tools

### 4. Skills (Agent Skills Specification)

**Specification:** Implements open standard from [agentskills.io](https://agentskills.io/)

**Storage Locations:**
- Project generic: `.kilo/skills/`
- Project compat: `.claude/skills/`, `.agents/skills/`
- Global: `~/.kilo/skills/`
- Remote: URLs in config

**File Format:** `SKILL.md` with YAML frontmatter

```markdown
---
name: api-design
description: REST API design best practices and conventions
license: MIT
---

# API Design Guidelines

When designing REST APIs, follow these conventions:

## URL Structure
- Use plural nouns for resources: `/users`, `/orders`
- Use kebab-case: `/order-items`
```

**Frontmatter (Required):**
- `name`: Skill identifier (max 64 chars, lowercase, hyphens)
- `description`: When to use this skill (max 1024 chars)

**Frontmatter (Optional):**
- `license`: License type or file reference
- `compatibility`: Environment requirements
- `metadata`: Key-value custom metadata

**How It Works:**
1. **Discovery:** Skills scanned at session start (metadata only: name, description, path)
2. **Prompt Injection:** Skill metadata included in system prompt
3. **Agent Decides:** Agent evaluates request against skill descriptions
4. **On-Demand Loading:** When skill matches, full SKILL.md loaded into context
5. **Bundled Resources:** Optional `scripts/`, `references/`, `assets/` directories

**Name Matching:** Must match parent directory name exactly
```
✅ Correct:
skills/frontend-design/SKILL.md  # name: frontend-design

❌ Incorrect:
skills/frontend-design/SKILL.md  # name: my-skill (mismatch)
```

**Optional Bundled Resources:**
```
my-skill/
├── SKILL.md              # Required: instructions + metadata
├── scripts/              # Optional: executable code
├── references/           # Optional: documentation
└── assets/               # Optional: templates, resources
```

**Marketplace:** [github.com/Kilo-Org/kilo-marketplace](https://github.com/Kilo-Org/kilo-marketplace)

### 5. Custom Rules

(Listed in docs, not detailed yet - likely similar to Cline)

### 6. Custom Instructions

(Listed in docs, not detailed yet)

### 7. agents.md (Project Context)

(Listed in docs, not detailed yet)

---

## Kilo Execution Model

```
1. User selects primary agent or types `/` for workflow or `@` for subagent
2. Kilo loads agent configuration:
   - Prompt (custom + rules + instructions)
   - Skills (metadata)
   - Permissions
   - Model
3. Kilo invokes AI with:
   - System prompt (agent prompt + skills metadata)
   - Tools available based on permissions
   - Previous context if continuing
4. Agent responds, makes tool calls, or invokes subagent
5. For subagent invocation:
   - Agent calls `task` tool with subagent name
   - Subagent runs in isolated session
   - Results return to parent agent
6. Loop until task complete
```

---

## Configuration Precedence

Lowest to highest priority:

1. Built-in agent defaults
2. Global config (`~/.config/kilo/kilo.jsonc`)
3. Project config (`kilo.jsonc`)
4. `.kilo/agents/*.md` files (project)
5. Global `.kilo/agents/*.md` files
6. Environment variable overrides

Properties **merge** (not replace), so you can override just model without redefining entire agent.

---

## IR Mapping for Phase 2A

### KiloBuilder Should Generate:

**1. Agent Definitions** (`.kilo/agents/{name}.md`)
```
PromptosaurusAgent →
  .kilo/agents/{agent.slug}.md
  
File content:
---
description: {agent.description}
mode: primary|subagent|all
model: {optional model override}
color: {optional color}
permission: {tool permissions}
---
{agent.prompt}
```

**2. Subagents** (same as agents, mode=subagent)
```
PromptosaurusSubagent →
  .kilo/agents/{name}.md (mode: subagent)
```

**3. Workflows** (`.kilo/commands/{name}.md`)
```
PromptosaurusWorkflow →
  .kilo/commands/{workflow.name}.md
  
File content:
---
description: {workflow.description}
agent: {recommended agent}
---
{workflow.steps as markdown}
```

**4. Skills** (`.kilo/skills/{name}/SKILL.md`)
```
PromptosaurusSkill →
  .kilo/skills/{skill.name}/SKILL.md
  
File content:
---
name: {skill.name}
description: {skill.description}
---
{skill.instructions}
```

**5. Config** (`kilo.jsonc`)
```json
{
  "agent": {
    "agent-name": {
      "description": "...",
      "mode": "primary",
      "model": "anthropic/claude-sonnet-4-20250514",
      "permission": {...}
    }
  }
}
```

---

## Key Differences from Old `.kilocodemodes`

| Feature | Old (YAML modes) | New (Agents) |
|---------|-----------------|--------------|
| **Storage** | `.kilocodemodes` (single file) | `.kilo/agents/*.md` + `kilo.jsonc` |
| **Format** | YAML with `slug` | Markdown + YAML or JSON config |
| **Subagents** | Not supported | Full subagent system |
| **Skills** | Not integrated | Full Agent Skills support |
| **Workflows** | Not integrated | Slash commands in `.kilo/commands/` |
| **Permissions** | `groups: [read, edit, bash]` | Fine-grained permission rules |
| **Model Control** | Global only | Per-agent model selection |
| **Temperature** | Not available | Per-agent temperature/top_p |
| **Nested Agents** | Not supported | Primary + subagent modes |

---

## Migration Path

Kilo auto-migrates old `.kilocodemodes` to new agent format:
- `slug` → agent name (filename)
- `roleDefinition` + `customInstructions` → `prompt`
- `groups` → `permission` rules
- `whenToUse`/`description` → `description`
- Mode set to `primary`

Default slugs skipped (they map to built-in agents).

---

## Comparison: Kilo vs Cline vs Copilot

| Feature | Kilo | Cline | Copilot |
|---------|------|-------|---------|
| **Agents/Modes** | Yes (`.kilo/agents/`) | Yes (implicit) | Yes (skills + instructions) |
| **Subagents** | Yes (explicit `@` or task tool) | No explicit | No explicit |
| **Skills** | Yes (Agent Skills spec) | Yes (`.cline/skills/`) | Yes (Agent Skills spec) |
| **Workflows** | Yes (`.kilo/commands/`) | Yes (`.clinerules/workflows/`) | Via hooks |
| **Skill Activation** | Implicit (auto-match) | Explicit (`use_skill` tool) | Implicit (auto-match) |
| **Rules/Instructions** | Implicit in agents | `.clinerules/` + conditional | Custom instructions |
| **Permissions** | Per-agent fine-grained | Implicit in agent design | Pre-approval fields |
| **Storage** | `.kilo/` directory | `.cline/`, `.clinerules/` | `.github/skills/` |
| **Standard** | Agent Skills (agentskills.io) | Cline-specific | Agent Skills (agentskills.io) |
| **Config File** | `kilo.jsonc` | Implicit | None (CLI flags) |

---

## Kilo Confidence Upgrade

**Previous:** 🟡 MEDIUM (verified locally)  
**Now:** ✅ **HIGH** (verified from official kilo.ai/docs)

Kilo has:
- ✅ Agent system with full config control
- ✅ Subagent support (like Copilot)
- ✅ Skills support (Agent Skills spec, like Copilot)
- ✅ Workflows (like Cline)
- ✅ Permission control (like Copilot)
- ✅ Model selection per-agent
- ✅ Both IDE (VS Code) and CLI support

---

## Summary

Kilo is **more sophisticated than previously documented** in the local `.kilocodemodes` structure. It's evolved to:
- Support Agent Skills specification (open standard)
- Implement subagents (delegated specialized agents)
- Provide fine-grained permission control
- Support workflows as slash commands
- Allow per-agent model selection
- Support both global and project-specific configuration

For Phase 2A IR, **Kilo should be treated equally with Cline and Copilot** as a first-class tool.

