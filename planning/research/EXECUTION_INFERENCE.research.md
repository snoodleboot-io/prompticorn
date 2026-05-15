# Execution Model Inference - Based on Tool Capabilities & Documentation

**Approach:** Using available documentation + logical inference about tool design

---

## CLAUDE (API) - EXECUTION MODEL (HIGH CONFIDENCE)

### Execution Flow
```
1. Send API request with:
   - system_prompt (agent definition)
   - tools (list of JSON schemas for skills)
   - messages (conversation history)

2. Claude responds with:
   - text response
   - optionally: tool_use blocks {tool_name, input, id}

3. For each tool_use:
   - Extract tool name + input
   - Call external tool handler
   - Return result as assistant_content

4. Loop back to step 2 until Claude doesn't use tools

5. Terminal response when Claude doesn't call tools
```

### Skills as Tools
- Skills = tool definitions in `tools` list
- Each skill has JSON schema (input parameters)
- Tool execution is **external** (caller responsibility)
- Multi-step workflows = nested tool calls within conversation context

### Confidence Level
**HIGH** - This is standard Claude API behavior documented in docs

### Builder Implication
ClaudeBuilder must:
- Convert IR Skills → JSON tool schemas
- Generate system_prompt from IR Agent
- Provide tool execution handlers (or framework for them)
- Caller manages the tool calling loop

---

## KILO (IDE/CLI) - EXECUTION MODEL (MEDIUM CONFIDENCE)

### Agent Execution
```
1. User selects mode in Kilo IDE/CLI
2. Kilo loads .kilo/agents/{mode}.md
3. Parses YAML frontmatter:
   - description (for user UI)
   - mode (primary | subagent)
   - permission (read, write, execute, etc)
4. Extracts markdown body (agent instructions)
5. Creates system prompt for Claude: instructions + core rules
6. Returns Claude responses to user
7. Session file (.prompticorn/sessions/) tracks context across mode switches
```

### Skills Usage (INFERRED)
```
How agents use shared skills:
1. Agent system prompt includes: "You have access to these skills: {skill_list}"
2. Agent reads skill descriptions and instructions
3. Agent decides to "use" a skill by mentioning it in response
4. User/CLI recognizes skill invocation and executes skill logic
5. Result returned to agent for next turn
```
- Skills are **documented in agent instructions**
- Agent decides to invoke by name reference
- Skill invocation is **chat-based** (agent says "use skill X")

### Workflows (INFERRED)
```
How workflows work:
1. .kilo/commands/{workflow}.md contains steps
2. Steps are either:
   a) User instructions ("run this command")
   b) Agent invocations ("call this agent")
   c) Skill invocations ("use this skill")
3. Slash commands (/submit-pr) trigger workflow execution
4. Workflow orchestrator reads steps sequentially
5. Step results feed into next step
```
- Workflows = **step lists with references**
- References resolved to agents/skills at runtime
- Execution is **sequential** (step N depends on N-1 result)

### Confidence Level
**MEDIUM** - Inferred from Kilo structure, needs verification

### Builder Implication
KiloBuilder must:
- Generate agent `.md` with skill descriptions + instructions
- Support skill/workflow references in agent prompts
- Create workflow step definitions in `.kilo/commands/`
- Handle skill invocation syntax (how agents reference skills)

---

## COPILOT (CLOUD) - EXECUTION MODEL (MEDIUM-LOW CONFIDENCE)

### Agent Execution
```
1. Agent API receives system prompt + skills + initial task
2. Agent is instantiated with these resources
3. Agent can:
   a) Call tools directly (native Claude tool_use)
   b) Trigger hooks at lifecycle points
4. Hooks can:
   a) Pre-tool: Modify tool inputs before execution
   b) Post-tool: Process results after execution
   c) Error: Handle failures
   d) Lifecycle: Setup/teardown
```

### Skills Model (INFERRED)
```
How per-agent skills work:
1. Skills attached to agent at creation time
2. Each skill = {name, description, implementation}
3. Agent references skill by name in tool_use
4. Hook validates skill exists for this agent
5. Hook executes skill (or delegates to tool handler)
```
- Skills are **agent-specific** (different per agent)
- Skill invocation is **hook-based** (pre/post tool execution)
- Skill chaining = skills can invoke other skills via hooks

### Multi-Step Workflows (INFERRED)
```
How orchestration works:
1. Hooks fired at key points:
   - onSessionStart: Initialize workflow state
   - onPreToolUse: Validate/modify tool before use
   - onPostToolUse: Process results, decide next step
   - onErrorOccurred: Handle failures
   - onSessionEnd: Cleanup
2. Post-tool hook decides: next step or complete?
3. Workflow state maintained in agent session
```
- Workflows = **implicit** (driven by hook orchestration)
- Steps = tool invocations chained via hooks
- Control flow = determined by hook logic

### Confidence Level
**MEDIUM-LOW** - Inferred from docs, needs verification from actual Agent API

### Builder Implication
CopilotBuilder must:
- Create hooks for each workflow step
- Implement onPostToolUse hook for step chaining
- Generate skill attachment at agent creation
- Handle skill invocation within hooks

---

## CURSOR - EXECUTION MODEL (LOW CONFIDENCE - SPECULATIVE)

### Agent Execution (INFERRED)
```
1. User provides task to cloud agent
2. Agent research phase: reads repo, understands codebase
3. Agent planning phase: creates implementation plan
4. Agent execution phase: makes changes iteratively
5. Agent review: presents diffs for user approval
6. Agent loop: user feedback → iterate
```

### Skills/Capabilities (INFERRED)
```
No explicit "skills" concept detected. Instead:
1. Agent capabilities = what agent prompt enables
2. Rules affect agent behavior/constraints
3. Capabilities are IMPLICIT (baked into agent)
4. Equivalent to skill = agent has instruction to "do X"
```
- Cursor uses **global rules** (not per-agent)
- Rules define agent constraints/capabilities
- Skills = **instructions in agent system prompt**

### Multi-Step Workflows (INFERRED)
```
How Cursor orchestrates tasks:
1. Agent receives task description
2. Agent autonomously decides steps
3. Agent executes plan (research → code → validate → iterate)
4. Workflow is IMPLICIT and AGENT-DRIVEN
5. User can iterate with feedback
```
- Workflows = **agent autonomy** (not explicit definitions)
- Steps = decided by agent, not predetermined
- Control flow = agent reasoning (implicit)

### Confidence Level
**LOW** - Cursor documentation is marketing-focused, not technical

### Builder Implication
CursorBuilder must:
- Convert IR to cloud agent configuration
- Express skills as agent instructions (system prompt)
- Express workflows as agent capabilities
- Fallback strategy: skills/workflows → rules + agent instructions

---

## CLINE - EXECUTION MODEL (LOW CONFIDENCE - SPECULATIVE)

### Agent Execution (INFERRED)
```
1. Cline receives task (via VS Code or CLI)
2. Agent directory structure:
   - .agents/skills/{skill-name}/
   - .clinerules/
3. Agent loads skills and rules
4. Agent executes task using skills
5. Loop: execute → evaluate → iterate
```

### Skills Model (INFERRED)
```
How bundled skills work:
1. .agents/skills/skill-name/ is one skill directory
2. Each skill contains:
   a) Skill definition (markdown or code)
   b) Implementation/logic
3. Skills are DISCOVERED and LOADED automatically
4. Skill invocation = agent calls skill by name
5. Skills can chain (skill A calls skill B)
```
- Skills are **bundled** (not shared across projects)
- Skills are **discoverable** (file system scan)
- Skills have **implementation** (not just description)
- Chaining = within skill implementation (programmatic)

### Rules Integration (INFERRED)
```
How rules work:
1. .clinerules/ contains project rules
2. Rules modify agent behavior
3. Rules can:
   a) Constrain execution (what agent can do)
   b) Guide execution (how agent should approach)
4. Fallback for missing skills support
```
- Rules = **project-level constraints**
- Rules ≠ Workflows (rules affect all agents)

### Confidence Level
**LOW** - Cline documentation is sparse on execution details

### Builder Implication
ClaudeBuilder must:
- Generate skill directories with implementation
- Create .clinerules/ for constraints
- Handle skill discovery/loading
- Support skill chaining via implementation calls

---

## CROSS-TOOL ANALYSIS

### Entry Points (Execution Begins)
| Tool | Entry Point |
|------|-------------|
| Claude | API call with system_prompt + tools |
| Kilo | Mode selection → agent prompt |
| Copilot | Agent API call with skills |
| Cursor | Task submission to cloud agent |
| Cline | Task via VS Code or CLI |

### Step Invocation (How Steps Invoke Each Other)
| Tool | Mechanism |
|------|-----------|
| Claude | tool_use → tool execution → result in messages |
| Kilo | Agent mentions skill → recognized in chat |
| Copilot | Hook calls → tool → result → next hook |
| Cursor | Agent reasoning decides next step |
| Cline | Skill implementation calls skill |

### Context Passing (State Between Steps)
| Tool | Mechanism |
|------|-----------|
| Claude | Message history (stateful conversation) |
| Kilo | Session file (persistent context) |
| Copilot | Agent session state |
| Cursor | Agent memory + iteration feedback |
| Cline | Shared skill state (TBD) |

### Skill Chaining (Skill Invokes Skill)
| Tool | Support | Mechanism |
|------|---------|-----------|
| Claude | **YES** | Tool calls tool within tool implementation |
| Kilo | **UNKNOWN** | Agent references skill in instructions? |
| Copilot | **UNKNOWN** | Hook calls hook? Skill calls skill? |
| Cursor | **NO** | No explicit skills |
| Cline | **YES** | Skill implementation calls skill |

---

## CRITICAL UNKNOWNS (Research Gaps)

### For Phase 2A Blocking
1. **Kilo**: How does agent reference a skill at execution time?
   - Is it description matching?
   - Is it explicit name reference?
   - Is it via special syntax in agent instructions?

2. **Copilot**: How do hooks work in practice?
   - Can post-tool hook call another tool? (skill chaining)
   - Does hook have access to agent skills?
   - How is state passed between hooks?

3. **Cursor**: How are capabilities expressed?
   - Are rules the only customization?
   - Can rules express multi-step workflows?
   - How does agent autonomy model translate to IR?

4. **Cline**: How is skill bundling managed?
   - What's in a skill directory?
   - How does discovery work?
   - Can skills reference other skills?

---

## NEXT RESEARCH STEPS

1. **For Kilo**: Look at actual kilo.ai documentation or open source examples
2. **For Copilot**: Study Agent API hook examples in GitHub docs
3. **For Cursor**: Reverse-engineer from Cursor behavior + docs
4. **For Cline**: Check Cline GitHub repo for skill examples
5. **For Claude**: Verify tool calling patterns with SDK examples

---

## Decision: Can Phase 2A Start?

**NO** - Too many unknowns about:
- How each tool invokes skills at runtime
- How each tool chains operations
- How state is managed across steps
- Whether skill chaining is supported

**Recommendation:**
- Need targeted research on each tool's execution model
- Should NOT start Phase 2A builders until we understand invocation mechanisms
- IR design depends on execution model decisions

