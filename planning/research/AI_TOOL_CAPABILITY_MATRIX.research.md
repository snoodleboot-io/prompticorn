# AI Tool Capability Matrix

## Overview

Comprehensive comparison of how each AI tool implements core agent capabilities. All tools support the same conceptual features (agents, skills, workflows, etc.) but implement them differently.

---

## Capability Matrix

| Capability | Claude | Cline | Copilot Cloud | Copilot CLI | Kilo IDE/CLI | Cursor |
|------------|--------|-------|---|---|---|---|
| **AGENTS** | System prompt + tools array | Agent files (`.md`) or implicit | Agent definitions + custom agents | Same as Cloud | `.kilo/agents/*.md` + `kilo.jsonc` | Implicit in system context |
| **Agent Configuration** | API parameters (`model`, `temperature`, `top_p`) | Markdown YAML frontmatter | Markdown YAML or JSON config | Same as Cloud | Markdown YAML or `kilo.jsonc` JSON | N/A (inferred) |
| **Agent Types** | Single agent per request | Primary + subagent modes | Primary + subagent modes | Same + `@mentions` | Primary + subagent `@mentions` | Single autonomous agent |
| **SKILLS** | `tools[]` array (JSON schema) | `.cline/skills/SKILL.md` (SKILL.md format) | `.github/skills/SKILL.md` (open standard) | Same as Cloud | `.kilo/skills/SKILL.md` (open standard) | Implicit in prompt engineering |
| **Skill Discovery** | Defined in API request | Directory scan at startup (progressive loading) | Directory scan at startup | Same as Cloud | Directory scan at session start | N/A |
| **Skill Activation** | Implicit (Claude chooses tools) | Explicit via `use_skill` tool call | Implicit (agent chooses based on description) | Same as Cloud | Implicit (agent chooses based on description) | Implicit (agent reasoning) |
| **Skill Resources** | Not applicable | Bundled: `docs/`, `scripts/` | Bundled: `scripts/`, templates | Same as Cloud | Bundled: `scripts/`, `references/`, `assets/` | N/A |
| **Skill Standard** | Proprietary (tool definitions) | Cline-specific format | Agent Skills specification (agentskills.io) | Same as Cloud | Agent Skills specification (agentskills.io) | N/A |
| **WORKFLOWS** | Implicit (tool call chains) | Explicit: `.clinerules/workflows/*.md` markdown files | Hook-based: `.github/hooks/*.json` | Explicit: `.kilo/commands/*.md` markdown files | Explicit: `/slash-commands` in `.kilo/commands/` | Implicit (autonomous reasoning) |
| **Workflow Invocation** | N/A (implicit tool chaining) | `/workflow-name` command | `preToolUse`, `postToolUse` hooks | Same as Cloud | `/command-name` slash command | N/A (implicit) |
| **Workflow Steps** | Tool calls (implicit sequence) | Markdown natural language OR XML tool syntax | Bash/PowerShell scripts in hooks | Markdown natural language OR XML tool syntax | Markdown natural language OR XML tool syntax | N/A (implicit) |
| **SUBAGENTS/DELEGATION** | Tool that calls Claude API (user implemented) | Skills can reference other agents | Explicit via `@mentions` or Task tool | Same as Cloud + `@mentions` | Explicit via `@mentions` or Task tool | N/A (single agent) |
| **Subagent Isolation** | Separate API calls = separate context | Implicit in skill invocation | Separate sessions with tailored prompts | Same as Cloud | Separate sessions with isolated context | N/A |
| **RULES/INSTRUCTIONS** | System prompt only | `.clinerules/` markdown files (conditional paths supported) | Custom instructions (natural language) | Same as Cloud | Implicit in agent prompts OR separate rules | `.cursorrules` file (inferred) |
| **Rules Scope** | Global (entire request) | Global + conditional (glob paths like `src/**/*.py`) | Repository-level or organization-level | Same as Cloud | Global + per-agent (implicit in prompt) | Unknown |
| **HOOKS/VALIDATION** | N/A (validation in application code) | Event-based (nascent, not fully documented) | JSON hooks with bash/powershell (preToolUse, postToolUse, etc) | Same as Cloud | N/A (implicit in agent design) | N/A (implicit) |
| **Hook Types** | N/A | Unknown (documentation nascent) | sessionStart, preToolUse (approval/denial!), postToolUse, sessionEnd, errorOccurred, etc. | Same as Cloud | N/A | N/A |
| **PERMISSIONS** | N/A (tool access in API) | Implicit in agent design | Fine-grained per-agent: read, edit, bash, glob, grep, task, etc | Same as Cloud | Per-agent: read, edit, bash, glob, grep, list, task, etc | N/A (inferred) |
| **Permission Model** | Tool definitions in API | Tool access implicit | `permission: {tool: "allow"|"ask"|"deny"}` with glob patterns | Same as Cloud | `permission: {tool: "allow"|"ask"|"deny"}` with glob patterns | N/A |
| **MODEL SELECTION** | Per-request (model parameter) | Not explicitly per-agent | Per-agent `model: provider/model-id` | Same as Cloud | Per-agent `model: provider/model-id` | Unknown (probably global) |
| **STORAGE/FORMAT** | API payload (JSON) | Directory-based: `.cline/skills/`, `.clinerules/`, etc | Directory-based: `.github/skills/`, `.github/hooks/` | Same as Cloud | Directory-based: `.kilo/agents/`, `.kilo/skills/`, `.kilo/commands/` | Unknown (inferred) |
| **Config File** | N/A (API parameters) | Implicit (directory structure) | Implicit (directory structure) | Same as Cloud | `kilo.jsonc` JSON config file | `.cursorrules` file |
| **Global Config** | N/A | `~/.cline/` (user-level) | N/A | `~/.config/copilot/` (inferred) | `~/.config/kilo/` (user-level) | Unknown |
| **State Persistence** | Message history (session-based) | Focus chain file (`.cline_tasks/`) with file watchers | GitHub Actions environment (task-specific) | Local chronicle (session history) | Session management (`.promptosaurus/sessions/`) | Implicit (session context) |
| **Activation/Trigger** | User sends message + tools | User types `/` or `use_skill` tool | Agent sees skill descriptions at startup | User selects agent or `@mentions` subagent | User selects agent or `@mentions` subagent | User describes goal |
| **Multi-Agent Coordination** | Tool that calls Claude API | Not explicitly supported | Task tool invokes other agents | `@mentions` or Task tool | `@mentions` or Task tool | N/A (single agent) |
| **Context Window Management** | Explicit (messages parameter) | Focus chain (progress tracking) | GitHub Actions limits | Session-based (local) | Session-based (.promptosaurus) | Implicit (model context) |
| **Tool Categories** | read, edit, bash, web tools, code execution | read, write, bash, MCP servers, web tools | read, edit, bash, web tools, MCP servers | Same as Cloud | read, glob, grep, edit, write, bash, webfetch, MCP servers | N/A |

---

## Key Insights

### Universal Concepts (All Tools Have)
✅ **Agents** - Defined via system prompt, prompts, or configs  
✅ **Skills** - Capabilities that agents can use  
✅ **Workflows** - Multi-step automation  
✅ **Subagents** - Delegation to specialized agents  
✅ **Rules** - Coding standards and constraints  

### Implementation Patterns

**Storage:**
- **Claude**: API payload (stateless)
- **Cline, Copilot, Kilo**: Directory-based (project + global)
- **Cursor**: Unclear (likely file-based)

**Activation:**
- **Implicit**: Claude, Copilot, Kilo (agent decides)
- **Explicit**: Cline (via `use_skill` tool)
- **Autonomous**: Cursor (agent reasons through)

**Skill Format:**
- **Tool schema**: Claude (JSON)
- **SKILL.md standard**: Cline, Copilot, Kilo (agentskills.io spec)
- **Implicit**: Cursor

**Hooks:**
- **Copilot**: Explicit JSON hooks with bash/powershell (preToolUse powerful for approval/denial)
- **Cline**: Event-based (nascent)
- **Others**: Implicit or N/A

**Permissions:**
- **Fine-grained**: Copilot, Kilo (per-agent rules)
- **Implicit**: Claude, Cline, Cursor

---

## Phase 2A IR Mapping

### Universal IR Models Needed:

```python
PromptosaurusAgent:
  - name: str
  - description: str
  - prompt: str (minimal)
  - prompt_verbose: str (detailed, optional)
  - model: str (optional, provider/model format)
  - skills: list[str]
  - subagents: list[str]
  - permissions: dict (optional)
  
PromptosaurusSkill:
  - name: str
  - description: str
  - instructions: str
  - instructions_verbose: str (optional)
  - resources: dict (bundled files)
  
PromptosaurusWorkflow:
  - name: str
  - description: str
  - steps: list[str]
  - type: "implicit" | "explicit" | "hook-based"
  
PromptosaurusRules:
  - name: str
  - description: str
  - content: str
  - scope: "global" | "conditional"
  - conditions: dict (glob patterns, etc)
```

### Builders Handle Translation:

| Builder | Agent → | Skill → | Workflow → | Rules → |
|---------|---------|---------|-----------|---------|
| **Claude** | System prompt | `tools[]` JSON schema | (implicit tool chains) | System prompt |
| **Cline** | Implicit | `.cline/skills/SKILL.md` | `.clinerules/workflows/*.md` | `.clinerules/*.md` |
| **Copilot** | Custom instructions | `.github/skills/SKILL.md` | `.github/hooks/*.json` (hooks) | Custom instructions |
| **Kilo** | `.kilo/agents/*.md` | `.kilo/skills/SKILL.md` | `.kilo/commands/*.md` | Agent prompts |

---

## Confidence Levels

| Tool | Confidence | Based On |
|------|-----------|----------|
| Claude | ✅ HIGH | API documentation + OpenAI standards |
| Cline | ✅ HIGH | Official docs + source code |
| Copilot Cloud | ✅ HIGH | Official GitHub docs |
| Copilot CLI | ✅ HIGH | Official GitHub docs |
| Kilo IDE/CLI | ✅ HIGH | Official kilo.ai/docs |
| Cursor | 🟡 MEDIUM | Minimal public docs, inferred from behavior |

---

## Summary

**All tools implement the same conceptual capabilities (agents, skills, workflows, subagents, rules).**

The architecture differences are:
1. **Storage**: API payload vs directory-based files
2. **Format**: JSON vs Markdown vs YAML
3. **Activation**: Implicit (Claude, Copilot, Kilo) vs Explicit (Cline)
4. **Standards**: Proprietary vs open standard (agentskills.io)
5. **Hooks**: Explicit (Copilot) vs nascent (Cline) vs implicit (others)
6. **Permissions**: Fine-grained (Copilot, Kilo) vs implicit (others)

**For Phase 2A: Build IR that's tool-agnostic, let builders handle translation.**

