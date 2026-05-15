# Execution Models for Phase 2 AI Tool Integration

## Overview

This document details HOW each of the 6 AI tools executes agents, skills, and workflows based on source code analysis and inference. These execution models are CRITICAL for finalizing the Intermediate Representation (IR) design and builders in Phase 2A.

## 1. Claude (Direct Tool Calling Loop)

**Status:** ✅ HIGH CONFIDENCE (Verified via API documentation)

### Execution Model

Claude uses a **turn-based tool calling loop**:

```
1. User sends message + system prompt (with tools)
2. Claude analyzes → decides what tool to call
3. Claude returns: tool_use block with name + input
4. Client executes tool, captures output
5. Client sends: tool_result block to Claude
6. Claude continues → loop back to step 2 or respond to user
```

### How Agents Work

- **System prompt** contains tool definitions (skills, capabilities)
- **Tools** are invoked by Claude based on analysis
- **Context** accumulates in message history
- **Workflows** = sequence of tool calls decided by Claude

### How Skills Invoke Other Skills

- Skills are **separate tools** in the system prompt
- Skill A can call Skill B by having Claude invoke Skill B tool
- Skills are **stateless** - no inherent chaining mechanism
- Orchestration is **implicit** via Claude's reasoning

### IR Mapping

For Claude builders:
- `PrompticornAgent` → Tool definition with `name` + `description` + `input_schema`
- `PrompticornSkill` → Tool definition (nested in agent)
- `PrompticornWorkflow` → Multiple tools; workflow = sequence Claude decides to invoke
- Builder output: OpenAI/Anthropic `Tool` objects with JSON schemas

---

## 2. Cline (Task-Based with Focus Chain Progress Tracking)

**Status:** ✅ HIGH CONFIDENCE (Verified from source code)

### Execution Model

Cline uses an **extended tool calling loop with progress tracking**:

```
1. User initiates task → Cline creates task context
2. AI receives system prompt with tools
3. AI analyzes → tool_use block
4. Cline executes tool
5. AI provides task_progress update (optional, focus chain)
6. Cline updates focus chain markdown file
7. Loop back to step 3 until task marked complete
```

### Focus Chain (Progress Tracking)

- **Focus Chain List:** Markdown file with todo items (- [ ], - [x])
- **File:** `.cline_tasks/{taskId}.md`
- **File Watcher:** Monitors file for user edits in real-time
- **AI Feedback:** Every N API calls, remind AI to update progress
- **Bidirectional:** User can edit file → Cline notifies AI of changes
- **Parameters:**
  - `task_progress`: AI returns updated todo list as string
  - `apiRequestCount`: Tracks calls since last update
  - `todoListWasUpdatedByUser`: Signals user edits to AI

### How Skills Work

- Skills stored in: `.agents/skills/{skill-name}/SKILL.md`
- Skill activation: AI uses `use_skill` tool
- Flow: `use_skill("skill_name")` → Cline loads skill file → applies instructions to context
- Skills are **discovered at startup** from directory
- Skill metadata: name, description, path
- Skill content: Full instructions (loaded on-demand)

### How Workflows Work

- **Workflow storage:** `.clinerules/workflows/` directory
- **Workflow structure:** Markdown files defining steps/sequences
- **Workflow execution:** Not autonomous - user-triggered or suggested by AI
- **Workflow format:** Toggles + conditional instructions
- **Chaining:** AI decides workflow step sequence; not hardcoded

### IR Mapping

For Cline builders:
- `PrompticornAgent` → Agent definition + tools + focus chain settings
- `PrompticornSkill` → Skill markdown file + metadata
- `PrompticornWorkflow` → Workflow markdown + step toggles
- Builder output:
  - Agent: System prompt with tools + focus chain instructions
  - Skill: `.agents/skills/{name}/SKILL.md` file
  - Workflow: `.clinerules/workflows/{name}.md` file

### Key Integration Points

1. **Task Progress Tracking:**
   - Include `task_progress` parameter in every system prompt
   - Remind AI to update progress every N calls (configurable)
   - Display progress to user in real-time

2. **Skill Discovery:**
   - Cline scans `.agents/skills/` at startup
   - Builder must write skill files to this directory
   - Metadata discovery: name, description from file

3. **Workflow Toggles:**
   - Workflows have on/off toggles per workspace
   - Builder must synchronize toggles with file system
   - Include enabled workflows in system prompt

---

## 3. Kilo IDE (Integrated Agent + Mode System)

**Status:** 🟡 MEDIUM CONFIDENCE (Code examined, needs deeper integration understanding)

### Execution Model

Kilo uses an **agent loading + session management** model:

```
1. User selects agent/mode in IDE
2. Kilo loads agent definition from .kilo/
3. Kilo initializes session context (.prompticorn/sessions/)
4. IDE invokes Claude with loaded agent system prompt
5. Claude returns tool calls
6. Kilo executes tools → updates session
7. Session persists across mode switches
```

### Agent Loading

- Agents defined in: `.kilo/agents/` directory
- Agent definition: YAML + markdown instructions
- Agent discovery: IDE scans `.kilo/agents/` at startup
- Session management: `.prompticorn/sessions/session_*.md` files
- Session tracking: Persists context across mode switches

### How Agents Work

- **Entry point:** User selects agent mode in IDE
- **System prompt:** Loaded from `.kilo/agents/{agent}/instructions.md`
- **Session context:** Includes mode history, actions taken, current state
- **Tool calls:** IDE provides context tools (file read/write, git, bash)

### How Skills Work

- Skills embedded in agent instructions (not separated)
- Skills referenced via: `See skills.md for task breakdown` (chat reference)
- No explicit skill tool like Cline
- Skills are **documentation + patterns** in rule files

### How Workflows Work

- Workflows defined via session management + mode switching
- Multi-mode workflows: Architect → Code → Test → Review
- Workflow state: Persisted in session files
- Transitions: User switches modes, session updated

### IR Mapping

For KiloBuilder:
- `PrompticornAgent` → `.kilo/agents/{name}/` directory
- `PrompticornSkill` → Extract from `.kilo/rules-{mode}/` → write to `.kilo/skills/`
- `PrompticornWorkflow` → Session-based workflow definitions
- Builder output:
  - Agent: Directory structure + instructions.md + metadata.yaml
  - Skill: `.kilo/skills/{name}/` directory
  - Workflow: Implicit in session mode history + agent chain

### Key Integration Points

1. **Session Management:**
   - Create `.prompticorn/sessions/session_{date}_{id}.md`
   - Track mode history, actions, context summary
   - Persist across IDE restarts

2. **Agent Registry:**
   - Agents registered in `.kilo/agents/` directory
   - IDE discovers agents at startup
   - Agent selection loads system prompt

3. **Multi-Mode Workflows:**
   - Session transitions between modes
   - Each mode has separate instructions
   - Context flows through session file

---

## 4. Copilot (Hook-Based Orchestration)

**Status:** 🟡 MEDIUM CONFIDENCE (Inferred from agent API)

### Execution Model

Copilot likely uses **hook-based lifecycle events**:

```
1. User invokes copilot agent
2. Agent initialization → onInit hook
3. Claude receives system prompt
4. Tool calls → onBeforeTool hook
5. Tool executes
6. Tool result → onAfterTool hook
7. Next iteration or completion → onComplete hook
```

### How Agents Work

- Agent definition: Configuration + hook definitions
- Hooks: Entry points for custom behavior
- Context: Shared across hooks during agent lifetime

### How Skills Work

- Skills likely: Separate agent definitions
- Skill chaining: Via hook orchestration
- Hook flow: onBeforeTool (check if skill needed) → invoke skill

### How Workflows Work

- Workflows: Sequence of hook calls
- Orchestration: Copilot runtime manages sequence
- State: Implicit in hook context

### IR Mapping

For CopilotBuilder:
- `PrompticornAgent` → Hook-based agent definition
- `PrompticornSkill` → Skill agent + hook references
- `PrompticornWorkflow` → Hook sequence definition
- Builder output: Hook configuration objects

**Note:** Needs deeper research - inferred from VS Code Copilot Agent API patterns.

---

## 5. Cursor (Autonomous Agent Mode)

**Status:** 🟠 LOW CONFIDENCE (Marketing docs only, no source code)

### Inferred Execution Model

Cursor appears to use **autonomous agent mode with implicit reasoning**:

```
1. User describes goal
2. Cursor agent receives description + context
3. Agent reasons about steps
4. Agent executes tools autonomously
5. Agent may ask clarifying questions
6. Repeat until goal complete or user stops
```

### How Agents Work

- Agents are **defined through instructions** (like Copilot)
- Agent receives goal → determines steps autonomously
- Context: Large - includes workspace files, git history

### How Skills Work

- Unclear - likely similar to Copilot
- Possibly: Separate instruction sets for specific domains

### How Workflows Work

- Workflows: Implicit in agent reasoning
- No explicit workflow definitions found
- Orchestration: Agent decides sequence

### IR Mapping

For CursorBuilder:
- `PrompticornAgent` → Instruction set + context configuration
- `PrompticornSkill` → Domain-specific instruction set
- `PrompticornWorkflow` → Goal-based orchestration (implicit)
- Builder output: Instruction configuration

**Note:** Requires investigation of Cursor's actual agent API - inferred from behavior patterns.

---

## 6. Kilo CLI (Step-Based Orchestration)

**Status:** 🟠 LOW CONFIDENCE (Not yet researched)

### Inferred Execution Model

Kilo CLI likely uses **step-based task execution**:

```
1. User runs: kilo run workflow-name
2. CLI loads workflow definition
3. For each step in workflow:
   a. Invoke AI with step context
   b. Execute returned tools
   c. Continue to next step
4. Persist state between steps
```

### How Agents Work

- Agents: CLI entry points with step definitions
- Execution: Sequential step invocation
- Context: Passed between steps via state file

### How Skills Work

- Skills: Reusable steps in workflows
- Invocation: Via step definition
- Chaining: Steps reference other steps/skills

### How Workflows Work

- Workflows: Explicit step sequences
- Orchestration: CLI runtime manages sequence
- State: Persisted between steps

### IR Mapping

For KiloCliBuilder:
- `PrompticornAgent` → CLI command definition
- `PrompticornSkill` → Step definition
- `PrompticornWorkflow` → Workflow file with step sequence
- Builder output: Workflow YAML + step definitions

**Note:** Requires source code research - currently inferred only.

---

## Execution Model Comparison Matrix

| Aspect | Claude | Cline | Kilo IDE | Copilot | Cursor | Kilo CLI |
|--------|--------|-------|----------|---------|--------|----------|
| **Primary Loop** | Tool calling | Tool + progress | Agent loading | Hooks | Autonomous | Steps |
| **Skill Mechanism** | Tools | use_skill tool | Embedded docs | Hooks? | Instructions? | Steps |
| **Workflow Type** | Implicit (AI decides) | Toggles + AI | Mode-switching | Hook sequence | Implicit (AI) | Explicit (YAML) |
| **State Persistence** | Message history | Focus chain + file watchers | Session file | Hook context | Implicit | Workflow state |
| **Skill Discovery** | Defined upfront | Directory scan | Rule files | API config | Implicit | YAML/config |
| **Multi-Step Support** | ✅ Via tool loops | ✅ Via task_progress | ✅ Via modes | ✅ Via hooks | ✅ Implicit | ✅ Explicit |
| **Confidence Level** | ✅ HIGH | ✅ HIGH | 🟡 MEDIUM | 🟠 LOW | 🟠 LOW | 🟠 LOW |

---

## IR Design Implications

### For Pydantic IR Models

1. **All tools use system prompts** → `PrompticornAgent.prompt` and `prompt_verbose`
2. **Skills vary significantly** → Builders handle translation to tool-specific format
3. **Workflows are differently structured** → Use builder mixins (`SupportsWorkflows`)
4. **Progress tracking varies** → Only Cline has explicit progress model
5. **State persistence differs** → Session file (Kilo) vs focus chain (Cline) vs message history (Claude)

### For Builder Implementation

1. **PrompticornBuilder (base ABC)**
   - `build_agent()` → system prompt + tool definitions
   - `validate_agent()` → check for tool name conflicts, etc.

2. **Mixin Interfaces**
   - `SupportsSkills` → build/validate skills
   - `SupportsWorkflows` → build/validate workflows
   - `SupportsProgressTracking` → optional (Cline only)

3. **Tool-Specific Details**
   - ClineBuilder: Writes skill files, handles focus chain, workflow toggles
   - KiloBuilder: Writes agent directories, manages session templates
   - ClaudeBuilder: Generates Tool JSON schemas
   - CopilotBuilder: Generates hook definitions
   - CursorBuilder: Generates instruction configurations

### Next Research Steps

1. **Kilo CLI** - Source code analysis for step-based execution model
2. **Copilot Agent API** - Deep dive into hook lifecycle
3. **Cursor** - Find public API docs or source examples
4. **Kilo Integration** - Verify session management with actual Kilo code
5. **Cline Workflow Chaining** - Document how workflows reference each other

---

## References

### Source Code Analyzed

- **Cline:**
  - `src/core/task/focus-chain/index.ts` - Focus chain management
  - `src/shared/focus-chain-utils.ts` - Focus chain utilities
  - `src/core/context/instructions/user-instructions/workflows.ts` - Workflow toggles

### Previous ARDs

- `docs/ard/PHASE2_REGISTRY_ARCHITECTURE.md`
- `docs/ard/PHASE2A_IR_MODELS_AND_BUILDERS.md`

