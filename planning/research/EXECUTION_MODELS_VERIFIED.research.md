# Verified Execution Models for AI Tools

**Last Updated:** 2026-04-09  
**Status:** RESEARCH COMPLETE FROM OFFICIAL DOCUMENTATION  
**Source:** cursor.com, docs.cline.bot, docs.github.com, source code analysis

---

## 1. Claude (Anthropic)

**Status:** ✅ HIGH CONFIDENCE  
**Source:** API documentation, standard tool calling pattern

### Execution Model

```
1. User sends: message + system_prompt + tools[] + parameters
2. Claude analyzes request
3. Claude returns: text response OR tool_use blocks
4. Client executes tools
5. Client sends: tool_results to Claude
6. Loop: Claude decides next action or end
```

### Agent/Skill/Workflow Execution

- **Agents:** Defined via system prompt + tools
- **Skills:** Implemented as individual Tool objects in the tools array
- **Workflows:** Implicit - Claude chains tools based on reasoning
- **State:** Message history maintains context across turns

### IR Mapping

- `PrompticornAgent` → System prompt + tool descriptions (JSON schema)
- `PrompticornSkill` → Tool object with name, description, input_schema
- `PrompticornWorkflow` → Implicit ordering (Claude decides sequence)

### Example Flow

```
PrompticornAgent:
  prompt: "You are a Python expert..."
  skills: ["test-writing", "refactoring"]
  
↓ ClaudeBuilder translates to:
{
  "system": "You are a Python expert...",
  "tools": [
    {
      "name": "test-writing",
      "description": "...",
      "input_schema": {...}
    },
    {
      "name": "refactoring",
      "description": "...",
      "input_schema": {...}
    }
  ]
}

↓ Claude output:
{
  "type": "tool_use",
  "id": "call_xyz",
  "name": "test-writing",
  "input": {...}
}
```

---

## 2. Cline

**Status:** ✅ HIGH CONFIDENCE  
**Source:** docs.cline.bot + source code analysis

### Customization Systems

Cline has 5 systems for customization:

| System | Purpose | When Active | Storage |
|--------|---------|------------|---------|
| **Rules** | Always-on guidance (coding standards, constraints) | Always (contextually) | `.clinerules/` + `~/Documents/Cline/Rules/` |
| **Skills** | Domain expertise loaded on-demand | When triggered (use_skill tool) | `.cline/skills/` + `~/.cline/skills/` |
| **Workflows** | Multi-step automation (release process, setup) | Invoked with `/workflow.md` | `.clinerules/workflows/` + `~/Documents/Cline/Workflows/` |
| **Hooks** | Custom logic at key moments (validation, enforcement) | Automatically on events | `.clinerules/hooks/` + `~/Documents/Cline/Hooks/` |
| **.clineignore** | File access control | Always | `.clineignore` in project root |

### Rules

- **Storage:** `.clinerules/` (all .md and .txt files combined)
- **When loaded:** Always in system context
- **Purpose:** Coding standards, architectural constraints, project conventions
- **Scope:** Global or conditional (via glob patterns in YAML frontmatter)
- **Example:** ".clinerules/coding.md", ".clinerules/frontend.md" (conditional)

### Skills

- **Storage:** `.cline/skills/{skill-name}/SKILL.md`
- **Progressive loading:**
  - Metadata (~100 tokens): Loaded at startup (name + description only)
  - Instructions (< 5k tokens): Loaded when skill triggered via `use_skill` tool
  - Resources: Loaded on-demand when referenced
- **Activation:** AI calls `use_skill("skill-name")` tool
- **File structure:**
  ```
  my-skill/
  ├── SKILL.md           # Required: YAML frontmatter + instructions
  ├── docs/              # Optional: supporting documentation
  │   └── advanced.md
  └── scripts/           # Optional: utility scripts
      └── helper.sh
  ```
- **SKILL.md format:**
  ```yaml
  ---
  name: my-skill
  description: What this skill does and when to use it
  ---
  # Detailed instructions for Cline to follow
  ```
- **Resource files:** Cline reads docs/ files via read_file tool, executes scripts/ directly

### Workflows

- **Storage:** `.clinerules/workflows/{name}.md`
- **Invocation:** Type `/` in chat → select workflow from autocomplete
- **Execution:** Steps executed sequentially with user approval
- **Step types:**
  - Natural language: "Run tests and fix failures" (Cline interprets)
  - XML tool calls: Precise control with `<execute_command>`, `<read_file>`, `<ask_followup_question>`
  - CLI tools: npm, git, docker, curl, etc.
  - MCP tools: Via `<use_mcp_tool>` syntax
- **Example:**
  ```markdown
  # Release Prep
  
  ## Step 1: Check for clean working directory
  <execute_command>
    <command>git status --porcelain</command>
  </execute_command>
  
  ## Step 2: Run tests
  <execute_command>
    <command>npm run test</command>
  </execute_command>
  
  If tests fail, stop and report.
  ```

### Hooks

- **Purpose:** Validate, enforce, monitor Cline behavior at key moments
- **Storage:** `.clinerules/hooks/` (not yet widely documented, but in overview)
- **Trigger points:** Not fully documented in current version
- **Use cases:** Security, validation, automation triggers

### IR Mapping

For ClineBuilder:

- `PrompticornAgent`:
  - `prompt` → System instructions + Rules
  - `skills` → Skill directory references
  - `workflows` → Workflow references
  
- `PrompticornSkill`:
  - `name` → Skill directory name
  - `description` → Triggers skill activation
  - `instructions` → SKILL.md body
  - `resources` → docs/, scripts/ directories
  
- `PrompticornWorkflow`:
  - `steps` → Workflow steps (natural language or XML)
  - Files written to: `.clinerules/workflows/{name}.md`

### Example Cline Project Structure

```
project/
├── .cline/
│   └── skills/
│       ├── aws-deploy/
│       │   ├── SKILL.md
│       │   └── scripts/deploy.sh
│       └── pr-review/
│           └── SKILL.md
├── .clinerules/
│   ├── coding.md          # Coding standards
│   ├── frontend.md        # Conditional: "src/components/**"
│   ├── backend.md         # Conditional: "src/api/**"
│   ├── workflows/
│   │   ├── release-prep.md
│   │   └── setup-db.md
│   └── hooks/             # Hooks (nascent)
├── .clineignore
└── src/
```

---

## 3. GitHub Copilot

**Status:** ✅ HIGH CONFIDENCE  
**Source:** docs.github.com (cloud agent, CLI, skills, hooks)

### Two Agents

**Copilot Cloud Agent (GitHub.com-based)**
- Runs in GitHub Actions environment (ephemeral)
- Can research, plan, code, test
- Creates pull requests autonomously
- Accessed via GitHub issues, chat, or VS Code
- Customizable with: Custom instructions, Skills, Hooks, MCP servers

**Copilot CLI (Terminal-based)**
- Interactive terminal agent
- Supports: Autopilot mode, /fleet (parallel tasks), /research
- Similar customization: Skills, Hooks, MCP servers, Custom agents

### Skills (Shared across both)

- **Storage:** `.github/skills/`, `.claude/skills/`, `.agents/skills/`
- **Format:** `SKILL.md` with YAML frontmatter (open standard)
- **File structure:**
  ```
  .github/skills/github-actions-debugging/
  ├── SKILL.md           # Required: name + description + instructions
  └── scripts/           # Optional: supporting scripts
      └── debug-action.sh
  ```
- **SKILL.md:**
  ```yaml
  ---
  name: github-actions-failure-debugging
  description: Guide for debugging failing GitHub Actions workflows.
  allowed-tools: shell     # Pre-approve shell tool
  license: MIT             # Optional
  ---
  
  # Detailed instructions
  When asked to debug a GitHub Actions failure, follow this process...
  ```
- **Activation:** Copilot sees skill descriptions at startup, loads full SKILL.md when triggered
- **Tool pre-approval:** `allowed-tools` field (shell, bash) to skip confirmation prompts
- **Personal vs Project skills:**
  - Project: `.github/skills/`, `.claude/skills/`, `.agents/skills/` (shared with team)
  - Personal: `~/.copilot/skills/`, `~/.claude/skills/`, `~/.agents/skills/` (personal only)
  - When conflicted: Project takes precedence (except Skills where personal takes precedence)

### Hooks (Copilot Agent-specific)

- **Storage:** `.github/hooks/*.json` (JSON configuration files)
- **Execution:** Custom shell commands at key moments
- **Hook types:**
  - `sessionStart`: Initialize environments, log sessions
  - `userPromptSubmitted`: Log user requests for audit
  - `preToolUse`: **Most powerful** - approve/deny tool execution (security gate!)
  - `postToolUse`: Log results, track usage
  - `agentStop`: Cleanup when agent finishes
  - `subagentStop`: Cleanup for subagents
  - `errorOccurred`: Error logging, notifications
  - `sessionEnd`: Cleanup, archive reports
  
- **Format:**
  ```json
  {
    "version": 1,
    "hooks": {
      "preToolUse": [
        {
          "type": "command",
          "bash": "scripts/security-check.sh",
          "powershell": "scripts/security-check.ps1",
          "cwd": "scripts",
          "timeoutSec": 15,
          "env": {"LOG_LEVEL": "INFO"}
        }
      ],
      "postToolUse": [
        {
          "type": "command",
          "bash": "scripts/log-tool.sh",
          "timeoutSec": 10
        }
      ]
    }
  }
  ```
- **Hook script receives:** JSON input with context about tool being used
- **Hook script can:** Approve/deny, validate, log, enforce policies
- **Synchronous execution:** Blocks agent until hook completes (max 30s timeout)

### Custom Instructions

- **Storage:** Repository-level or organization-level
- **Purpose:** Short natural-language statements about project/team preferences
- **Files:** One or more markdown files in `.github/copilot-instructions/` or similar

### Custom Agents

- **Purpose:** Specialized versions of Copilot for different tasks
- **Examples:** Frontend specialist, documentation expert, testing agent
- **Customization via:** Skills, Hooks, Custom instructions, MCP servers

### Model Context Protocol (MCP)

- **Purpose:** Give Copilot access to additional tools and data sources
- **Examples:** GitHub API, Slack, databases, custom tools

### IR Mapping

For CopilotBuilder (both cloud agent and CLI):

- `PrompticornAgent`:
  - `prompt` → Custom instructions file
  - `skills` → Skill references
  
- `PrompticornSkill`:
  - `name` → Skill directory name
  - `description` → Trigger for skill activation
  - `instructions` → SKILL.md body
  - `resources` → Scripts in skill directory
  - Files written to: `.github/skills/{name}/SKILL.md`
  
- `PrompticornWorkflow` (via Hooks):
  - `steps` → Hook definitions with bash/powershell
  - Files written to: `.github/hooks/*.json`

### Example Copilot Project Structure

```
project/
├── .github/
│   ├── skills/
│   │   ├── webapp-testing/
│   │   │   ├── SKILL.md
│   │   │   └── scripts/
│   │   │       └── test-runner.sh
│   │   └── github-actions-debugging/
│   │       └── SKILL.md
│   ├── hooks/
│   │   ├── security-check.json
│   │   └── workflow-automation.json
│   └── copilot-instructions/
│       ├── coding-standards.md
│       └── team-conventions.md
└── src/
```

---

## 4. Copilot CLI (Terminal-Based)

**Status:** ✅ HIGH CONFIDENCE  
**Source:** docs.github.com/en/copilot/concepts/agents/copilot-cli

### Execution Model

```
Interactive terminal agent with autonomous modes:

1. User enters prompt in CLI
2. Agent thinks/plans or works autonomously
3. Can work in multiple modes:
   - Interactive: Asks for approval at each step
   - Autopilot: Works without approval until task complete
   - /fleet: Parallel task execution
   - /research: Dedicated research mode
4. Session persists in local chronicle (session history)
```

### Key Commands

- **Default mode:** Interactive, agent proposes actions
- **Autopilot mode:** Agent works autonomously, no approval needed
- **/fleet:** Break complex request into tasks, run in parallel
- **/research:** Deep research on a topic
- **/chronicle:** Review session history, insights

### Customization

Same as Copilot Cloud Agent:
- Skills (`.github/skills/`, `~/.copilot/skills/`)
- Hooks (`.github/hooks/*.json`)
- Custom instructions
- Plugins (reusable agents, skills, hooks)
- MCP servers

### IR Mapping

Same as CopilotBuilder (cloud agent) - Skills and Hooks identical format.

---

## 5. Cursor

**Status:** 🟡 MEDIUM CONFIDENCE  
**Source:** cursor.com/docs, cursor.com/learn (minimal public docs)

### Limitations

- **No public source code** - Inferred from limited documentation
- **Minimal documentation** on agent customization
- **Likely similar to:** VS Code Copilot agent

### Inferred Execution Model

```
Autonomous agent with implicit reasoning:

1. User provides goal/context
2. Agent decides steps autonomously
3. Agent has access to: codebase, tools, context
4. Agent executes tools without prompting
5. Loop until goal complete or user stops
```

### Likely Customization (Inferred)

- **Rules:** Possibly `.cursorrules` file (known to exist)
- **Instructions:** Custom instructions similar to Copilot
- **Agents:** Likely support for custom agents
- **Skills:** Unknown if supported

### IR Mapping (Speculative)

For CursorBuilder:
- `PrompticornAgent` → Custom instructions or system prompts
- `PrompticornSkill` → Possibly `.cursorrules` or instruction sections
- `PrompticornWorkflow` → Implicit in agent reasoning

**⚠️ NOTE:** Cursor needs deeper public documentation research before finalization.

---

## 6. Kilo IDE

**Status:** 🟡 MEDIUM CONFIDENCE  
**Source:** Local source code (.kilocodemodes, .kilocode/), Kilo docs (limited)

### Execution Model

```
Mode-based agent system with session management:

1. User selects agent/mode in IDE
2. Kilo loads mode definition from .kilocodemodes (YAML)
3. Kilo loads system prompt from .kilocode/rules/system.md
4. Kilo loads mode-specific prompt from .kilocode/rules-{mode}/*.md
5. Kilo initializes session (.prompticorn/sessions/*.md)
6. IDE invokes Claude with assembled prompt
7. Claude returns tool calls
8. IDE executes, updates session
9. Session persists for mode switching
```

### Agent Definition (.kilocodemodes YAML)

```yaml
customModes:
  - slug: architect
    name: 🏗️ Architect
    description: System design, architecture planning
    roleDefinition: Detailed role description
    whenToUse: When to use this mode
    groups:           # Permissions
      - read
      - edit
      - command
```

### Prompt Loading

- **System:** `.kilocode/rules/system.md` (always loaded)
- **Conventions:** `.kilocode/rules/conventions.md` (language-specific)
- **Mode-specific:** `.kilocode/rules-{mode}/*.md` (all files in directory)
- **Skill rules:** `.kilocode/rules-{mode}/` (to be extracted to `.kilocode/skills/`)

### Session Management

- **Storage:** `.prompticorn/sessions/session_*.md` (YAML frontmatter + markdown)
- **Tracks:**
  - Mode history (sequence of modes used)
  - Actions taken (timestamped list)
  - Context summary (current state)
- **Persistence:** Survives IDE restarts, enables mode switching with context

### Workflows

- **Implicit in sessions:** Mode sequences (e.g., Architect → Code → Test → Review)
- **Explicit in future:** Planned `.kilo/workflows/` support

### IR Mapping

For KiloBuilder:

- `PrompticornAgent`:
  - `name` → Agent slug in .kilocodemodes
  - `prompt` → .kilocode/rules-{mode}/instructions.md (minimal)
  - `prompt_verbose` → .kilocode/rules-{mode}/instructions-verbose.md (detailed)
  - Files written to: `.kilocode/rules-{agent}/` directory structure
  
- `PrompticornSkill`:
  - Files written to: `.kilocode/skills/{skill}/SKILL.md`
  
- `PrompticornWorkflow`:
  - Implicit via session mode history (future explicit support)

### Example Kilo Project Structure

```
project/
├── .kilocodemodes          # Agent definitions (YAML)
├── .kilocode/
│   ├── rules/              # Core (system, conventions)
│   │   ├── system.md
│   │   └── conventions.md
│   ├── rules-architect/    # Architect mode instructions
│   │   ├── instructions.md
│   │   └── instructions-verbose.md
│   ├── rules-code/         # Code mode instructions
│   ├── rules-test/         # Test mode instructions
│   ├── skills/             # Future: extracted skills
│   │   ├── feature-impl/
│   │   │   └── SKILL.md
│   │   └── test-writing/
│   │       └── SKILL.md
│   └── workflows/          # Future: explicit workflows
└── .prompticorn/
    └── sessions/           # Session management
        └── session_*.md
```

---

## 7. Kilo CLI

**Status:** 🟠 LOW CONFIDENCE  
**Source:** Limited public documentation

### Inferred Execution Model

```
Step-based workflow orchestration:

1. User invokes: kilo run workflow-name
2. CLI loads workflow definition (YAML/Markdown)
3. For each step:
   a. Invoke AI with step context
   b. Execute returned tools
   c. Continue to next step
4. State persisted between steps
```

### Inferred Customization

- **Workflows:** YAML or Markdown files defining step sequences
- **Steps:** Can be skills, commands, AI prompts
- **Orchestration:** Linear step execution with conditional logic
- **Skills:** Reusable step definitions

### IR Mapping (Speculative)

For KiloCliBuilder:
- `PrompticornAgent` → CLI command/entry point definition
- `PrompticornSkill` → Step definition/reusable procedure
- `PrompticornWorkflow` → Workflow YAML with step sequence

**⚠️ NOTE:** Requires source code analysis of Kilo CLI for verification.

---

## Tool Comparison Matrix

| Feature | Claude | Cline | Copilot Cloud | Copilot CLI | Cursor | Kilo IDE | Kilo CLI |
|---------|--------|-------|-----------------|------------|--------|----------|----------|
| **Primary Model** | Tool calling | Rules + Skills + Workflows + Hooks | Skills + Hooks + Instructions | Skills + Hooks + Autopilot | Unknown | Mode + Session | Steps |
| **Skill Storage** | Tool schema (JSON) | `.cline/skills/` | `.github/skills/` | `.github/skills/` | Unknown | `.kilocode/skills/` (future) | YAML/Markdown |
| **Skill Activation** | Implicit (Claude picks) | `use_skill` tool | Auto on match | Auto on match | Unknown | Via system prompt | Step invocation |
| **Hooks/Validation** | None | (nascent) | JSON-based with bash | JSON-based with bash | Unknown | (future) | Unknown |
| **Workflows** | Implicit (tool chains) | Markdown steps | Hook orchestration | /fleet parallel tasks | Unknown | Session-based | Explicit steps |
| **Session/State** | Message history | Focus chain file | GitHub Actions env | Local chronicle | Unknown | .prompticorn/sessions/ | Workflow state |
| **Rules/Conventions** | System prompt | `.clinerules/` markdown | Custom instructions | Custom instructions | `.cursorrules` (inferred) | `.kilocode/rules-*` | Unknown |
| **Confidence** | ✅ HIGH | ✅ HIGH | ✅ HIGH | ✅ HIGH | 🟡 MEDIUM | 🟡 MEDIUM | 🟠 LOW |

---

## Key Insights for Phase 2 IR Design

### 1. Two Skill Activation Patterns

**Pattern A: Implicit Activation (Claude, Copilot)**
- Skills listed at startup
- AI decides when to use them
- No explicit tool calls needed
- **For:** Claude, Copilot variants

**Pattern B: Explicit Activation (Cline)**
- Skill metadata always loaded
- AI calls `use_skill` tool to activate
- Full instructions loaded on demand
- **For:** Cline

### 2. Hook Patterns

**Pattern A: Cline (nascent, not documented)**
- Purpose unclear from available docs
- Likely event-based

**Pattern B: Copilot (JSON + bash/powershell)**
- Pre-defined hook points (preToolUse, postToolUse, etc)
- Can approve/deny tool execution
- Synchronous, blocking execution
- **For:** Copilot variants

### 3. Rules/Conventions

- **Cline:** Markdown files in `.clinerules/` (always loaded, can be conditional)
- **Copilot:** Custom instructions (natural language, location varies)
- **Kilo:** Markdown files in `.kilocode/rules-*` (loaded per mode)
- **Cursor:** `.cursorrules` (inferred, minimal docs)

### 4. Workflow Types

| Tool | Workflow Type | Execution |
|------|---------------|-----------|
| Claude | Implicit | AI chains tools |
| Cline | Explicit markdown | Sequential steps with approval |
| Copilot Cloud | Hook-based | Shell commands at events |
| Copilot CLI | Explicit + /fleet | Sequential + parallel (/fleet) |
| Kilo | Session modes | Mode-based with context persistence |

### 5. State/Persistence

| Tool | State Mechanism | Persistence |
|------|-----------------|-------------|
| Claude | Message history | In-session only |
| Cline | Focus chain (file) + file watchers | Persistent file |
| Copilot Cloud | GitHub Actions environment | Task-specific |
| Copilot CLI | Local chronicle | Session history |
| Kilo | Session file (.prompticorn) | Persistent file |

---

## Recommendations for Phase 2A IR Design

1. **Dual skill activation support:**
   - Implicit field for Claude/Copilot (tool schema)
   - Explicit field for Cline (use_skill tool reference)

2. **Multi-hook model:**
   - Cline-style hooks (event-based, nascent)
   - Copilot-style hooks (JSON with bash/powershell)

3. **Rules inheritance:**
   - Always-loaded rules (global system, conventions)
   - Conditional rules (path-based activation)

4. **Workflow flexibility:**
   - Implicit workflows (tool chaining)
   - Explicit workflows (step sequences)
   - Hook workflows (event-based)

5. **Session tracking (optional Phase 2B):**
   - File-based session persistence (Kilo, Cline model)
   - For tools that support stateful execution

---

## Research Summary

| Tool | Research Status | Confidence | Next Steps |
|------|-----------------|-----------|-----------|
| Claude | ✅ Complete | ✅ HIGH | Implementation ready |
| Cline | ✅ Complete | ✅ HIGH | Implementation ready |
| Copilot Cloud | ✅ Complete | ✅ HIGH | Implementation ready |
| Copilot CLI | ✅ Complete | ✅ HIGH | Implementation ready |
| Kilo IDE | ✅ Complete | 🟡 MEDIUM | Verify with Kilo team |
| Cursor | ⏳ Partial | 🟡 MEDIUM | Needs public docs expansion |
| Kilo CLI | ⏳ Partial | 🟠 LOW | Needs source code analysis |

