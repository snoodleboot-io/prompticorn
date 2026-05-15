# AI Tool Execution Models - Research Document

**Status:** In Progress (being researched)  
**Purpose:** Understand how each tool EXECUTES workflows, chains operations, and invokes skills/tools

---

## KILO (IDE/CLI) - EXECUTION MODEL

### Agent Structure
- **File Format:** Individual `.md` files with YAML frontmatter
- **Location:** `.kilo/agents/{agent-name}.md`
- **Content:** 
  ```yaml
  ---
  description: "What agent does"
  mode: "primary" | "subagent"
  permission: {read, write, execute, etc}
  ---
  
  Role definition and instructions...
  ```

### How Kilo Executes Agents
- **Entry Point:** User selects agent mode in Kilo IDE/CLI
- **Load Mechanism:** Kilo loads `.kilo/agents/{mode}.md`
- **Execution:** Agent instructions are system prompt to Claude
- **State Management:** `.prompticorn/sessions/session_*.md` tracks mode/context

### How Kilo Chains Operations
**Question to Answer:** How do workflows invoke each other?
- Are commands in `.kilo/commands/` just step lists?
- Do they invoke agents/skills by name reference?
- Are there execution orchestration files?
- How does `/submit-pr` command chain multiple steps?

### How Kilo References Skills
**Question to Answer:** 
- Skills are shared in `.kilo/skills/`
- How does an agent USE a skill? (description matching? explicit reference?)
- Can a skill invoke another skill?
- How are tool references resolved?

---

## GITHUB COPILOT - EXECUTION MODEL

### Agent Structure
- **Format:** Agent API (TypeScript/JSON based)
- **Definition:** System prompt + tools + hooks
- **Skills Model:** Per-agent (each agent has its own set of skills)

### How Copilot Executes Workflows
**Hooks System:**
- `onPreToolUse`: Before tool execution
- `onPostToolUse`: After tool execution
- Lifecycle hooks: `onSessionStart`, `onSessionEnd`
- Error handling hook: `onErrorOccurred`

**Questions to Answer:**
- How does multi-step workflow execute? (Are hooks called sequentially?)
- Can hooks invoke other agents? (Sub-agent orchestration?)
- How are tool results chained between steps?
- What's the execution loop structure?

### How Copilot Chains Skills
**Questions to Answer:**
- Are skills per-agent and static (attached at agent creation)?
- Can a skill invoke another skill? (nested tool calls?)
- How are skill dependencies expressed?
- What's the tool calling mechanism? (Claude native tool_use?)

### Custom Agents
**Questions to Answer:**
- How are custom agents created/configured?
- Can custom agents call built-in agents? (orchestration?)
- What's the skill attachment mechanism? (static list? dynamic resolution?)

---

## CLAUDE (API) - EXECUTION MODEL

### Agent Structure
- **Format:** API parameters (no "agent" concept per se, but system prompts + tools)
- **Definition:** 
  ```python
  {
    "model": "claude-opus-4-5",
    "system": "...",  # System prompt (agent definition)
    "tools": [...],   # Tools/skills as JSON schemas
    "messages": [...]  # Conversation
  }
  ```

### How Claude Executes Workflows
**Tool Calling Loop:**
1. Claude receives system prompt + tools + initial message
2. Claude returns response (may include `tool_use` blocks)
3. For each `tool_use` block:
   - Extract tool name + input
   - Execute tool (external implementation)
   - Return results as `user` message
4. Loop until Claude doesn't return `tool_use` (terminal response)

**Questions to Answer:**
- Is this the actual loop? Or is there Agents API on top?
- How does multi-step workflow work? (sequential tool calls? parallel?)
- How are tool results tracked/maintained in context?
- What's the max turns/depth for tool calling loop?

### How Claude Handles Skills
**Questions to Answer:**
- Are skills represented as tools in `tools` list?
- How are tool schemas defined? (JSON schema format?)
- Can a tool invoke another tool? (from Claude's perspective, chained within tool implementation?)
- How are tool results structured/returned?

### Multi-Step Workflows
**Questions to Answer:**
- Is multi-step orchestration Claude's responsibility or caller's?
- Can we embed workflow logic in system prompt? ("first do X, then do Y")
- What's the stateless vs stateful model? (re-provide context each turn? maintain session?)

---

## CURSOR - EXECUTION MODEL

### Agent Structure
- **Format:** Cloud agent + Rules
- **Rules:** Global project-level customizations
- **Agents:** Autonomous agents that work on tasks

### How Cursor Executes Workflows
**Autonomous Agent Model:**
- Agent researches repo
- Agent creates implementation plan
- Agent makes code changes iteratively
- User reviews and can iterate

**Questions to Answer:**
- Is workflow execution implicit (agent handles it)?
- How does agent decide orchestration/order of steps?
- Where does "multi-step" control live? (in agent prompt? in agent code?)
- Can one agent invoke another agent?

### How Cursor Handles Skills
**Questions to Answer:**
- Cursor doesn't have explicit "skills" - what's the equivalent?
- Are capabilities baked into agent configuration/rules?
- How are domain-specific patterns expressed? (security-focused agent? perf-focused agent?)
- Can rules invoke other rules?

### Rules Capability
**Questions to Answer:**
- What can rules actually DO? (modify prompt? control behavior? execute code?)
- Can rules be agent-specific or only global?
- How do rules affect agent execution?
- Are rules a fallback for "skills" support?

---

## CLINE - EXECUTION MODEL

### Agent Structure
- **Format:** Directory-based (`.agents/skills/` + `.clinerules/`)
- **Skills:** Bundled in `.agents/skills/{skill-name}/`
- **Rules:** Project-level in `.clinerules/`

### How Cline Executes Workflows
**Questions to Answer:**
- How are skills invoked/chained?
- Is there explicit orchestration or is it implicit?
- How does Cline decide execution order?
- Can one skill invoke another?
- What's the execution entry point? (CLI command? file watching? event-based?)

### How Cline Handles Bundled Skills
**Questions to Answer:**
- What's in a skill directory? (Just `.md` files or executable code too?)
- How are skills discovered/registered? (file system scan?)
- How are skill dependencies expressed?
- Can skills be shared across projects or are they project-specific?

### Rules Integration
**Questions to Answer:**
- How do `.clinerules/` files work?
- Can they invoke skills?
- What patterns do they support?
- Are they execution rules or configuration rules?

---

## CROSS-TOOL ANALYSIS

### Concept Mapping (What We Need to Understand)

| Concept | Kilo | Copilot | Claude | Cursor | Cline |
|---------|------|---------|--------|--------|-------|
| **Agent** | `.md` + YAML | API Agent | system prompt | Cloud agent | Directory |
| **Skill** | Shared file | Per-agent | Tool JSON schema | ??? | Bundled dir |
| **Execution Entry** | Mode selection | Agent API call | Tool loop | Autonomous task | ??? |
| **Invocation** | Reference by name? | Hook callbacks? | Tool use + loop | Implicit agent | ??? |
| **Chaining** | Commands/workflows | Hooks? | Tool calling loop | Agent decides | ??? |
| **State/Context** | Session file | Agent state | Message history | Agent memory | ??? |

### Key Questions (Research Blockers)

**For ALL Tools:**
1. **Execution Entry Point**: Where does execution begin for a workflow/multi-step task?
2. **Step Invocation**: How does one step invoke the next? (function call? event? file reference?)
3. **Context Passing**: How is context/state passed between steps? (message? return value? shared memory?)
4. **Skill Chaining**: Can skills invoke other skills? How?
5. **Error Handling**: What happens if a step fails? (retry? fallback? abort?)
6. **Termination**: How does workflow know it's done? (explicit? implicit? timeout?)

---

## WHAT WE NEED TO KNOW FOR PHASE 2A

### For IR Design
- Should IR express **execution order** or just **components**?
- Should IR include **dependencies** between skills/workflows?
- Should IR include **conditional logic** or assume linear execution?

### For Builder Design
- How should builders translate IR execution concepts to tool-specific orchestration?
- Should builders generate execution code (e.g., Claude's tool calling loop)?
- Or just config/declaration and assume tool handles execution?

### For Validation
- What makes a workflow **valid** for each tool?
- Can we validate before building, or do we discover constraints during build?
- What falls back gracefully vs. what should error?

---

## RESEARCH STATUS

| Tool | Entry Point | Step Invocation | Context Passing | Skill Chaining | Error Handling |
|------|-------------|-----------------|-----------------|----------------|----------------|
| **Kilo** | ? | ? | ? | ? | ? |
| **Copilot** | ? | ? | ? | ? | ? |
| **Claude** | Known (tool loop) | Known (tool_use) | Known (messages) | ? | ? |
| **Cursor** | ? | ? | ? | ? | ? |
| **Cline** | ? | ? | ? | ? | ? |

---

## NEXT STEPS

1. Research actual Kilo command execution code
2. Research Copilot Agent API + hook orchestration
3. Research Claude tool calling patterns + best practices
4. Research Cursor agent autonomy model + multi-step patterns
5. Research Cline skill bundling + execution
6. Create execution model diagrams for each tool
7. Identify common patterns that can map to IR
8. Design builder strategies for each tool's execution model

