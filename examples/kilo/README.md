# Kilo IDE Agent Example

This example shows the output from the **KiloBuilder** for a simple "code" agent.

## What's Included

- **`code.md`** - Complete Kilo agent configuration file with YAML frontmatter and markdown sections

## File Format

Kilo agents use a specific format:

```
---
name: agent_name
description: Agent description
model: anthropic/claude-opus-4-1
state_management: .prompticorn/sessions/
---

# System Prompt

[Agent behavior and instructions]

# Tools

- tool1
- tool2

# Skills

[Optional: skill definitions]

# Workflows

[Optional: workflow definitions]

# Subagents

[Optional: list of subagents]
```

## Installation

Place the agent file in your Kilo project:

```bash
# Create agents directory if it doesn't exist
mkdir -p .kilo/agents

# Copy the example
cp examples/kilo/code.md .kilo/agents/code.md
```

After copying, restart Kilo IDE to load the new agent:
- Close and reopen Kilo
- Or: Use "Reload Configuration" command if available

## File Sections Explained

### YAML Frontmatter (`---`)

Required metadata at the top of the file:

- **name**: Agent identifier (used internally, must be unique)
- **description**: Human-readable description shown in UI
- **model**: Claude model to use (e.g., `anthropic/claude-opus-4-1`)
- **state_management**: Path to session storage (for continuity between calls)

### System Prompt

The core instructions for the agent's behavior. This section:
- Defines the agent's role and expertise
- Specifies quality standards
- Outlines the workflow for common tasks
- Sets tone and communication style

Good system prompts are:
- ✅ Specific about the agent's role
- ✅ Clear about expectations
- ✅ Include concrete examples
- ✅ Define constraints and rules

### Tools Section

Lists the tools available to the agent. Common tools:
- `read` - Read files and directories
- `write` - Write or modify files
- `execute` - Run shell commands
- `bash` - Execute terminal commands
- `file-operations` - File system operations

### Skills Section (Optional)

Reusable skills the agent can invoke. Each skill is a named pattern or workflow.

Example:
```markdown
# Skills

## Code Review Skill
- Read source files
- Check for common issues
- Provide feedback

## Testing Skill
- Write unit tests
- Run test suite
- Report coverage
```

### Workflows Section (Optional)

Step-by-step workflows for complex tasks. Use when you want the agent to follow a specific process.

Example:
```markdown
# Workflows

## Feature Implementation
1. Read existing code
2. Understand patterns
3. Write new code
4. Add tests
5. Document changes
```

### Subagents Section (Optional)

List of subagents this agent can delegate to. Each subagent gets its own file.

Example:
```markdown
# Subagents

- test-writer
- code-reviewer
- documenter
```

## Customization Guide

### Change the Agent Name

Replace all occurrences of `code` with your desired name:

```yaml
name: custom-agent  # Changed from 'code'
```

Update the system prompt accordingly:
```markdown
# System Prompt

You are an expert [in your custom domain]...
```

### Add/Remove Tools

Edit the Tools section:

```markdown
# Tools

- read
- write
- execute
- bash
```

### Create a Domain-Specific Version

For example, to create a "test-writer" agent:

```bash
cp .kilo/agents/code.md .kilo/agents/test-writer.md
```

Then edit:
```yaml
name: test-writer
description: Comprehensive test writing assistant
```

Update system prompt:
```markdown
# System Prompt

You are an expert test engineer. Write comprehensive,
well-structured tests with high coverage following
best practices for your language and framework...
```

### Add Custom Workflows

Define specific workflows your agent should follow:

```markdown
# Workflows

## Code Review Workflow
1. **Understand**: Read the changed files and related code
2. **Analyze**: Check for bugs, performance issues, style
3. **Test**: Verify test coverage and test quality
4. **Provide Feedback**: Write actionable review comments

## Feature Implementation Workflow
1. **Plan**: Break down the feature into tasks
2. **Implement**: Write clean, tested code
3. **Review**: Self-review before submission
4. **Test**: Verify with comprehensive tests
```

### Add Subagents

To delegate work to specialized subagents:

```markdown
# Subagents

- code-reviewer
- test-writer
- documenter
```

Then create files for each:
- `.kilo/agents/code-reviewer.md`
- `.kilo/agents/test-writer.md`
- `.kilo/agents/documenter.md`

## Common Patterns

### Python Code Agent

```yaml
name: python-code
description: Python development and code generation
```

System prompt should mention:
- Language version (e.g., Python 3.11+)
- Style guide (e.g., PEP 8)
- Testing framework (e.g., pytest)
- Type hints requirements

### JavaScript/TypeScript Agent

```yaml
name: typescript-code
description: TypeScript and JavaScript development
```

Consider tools:
- `npm` or `yarn` package management
- Testing with Jest or Vitest
- Linting with ESLint

### Architecture/Design Agent

```yaml
name: architect
description: System design and architecture assistant
```

Workflows might include:
- Requirements analysis
- Design document creation
- Technology evaluation
- Trade-off analysis

## Troubleshooting

### Agent doesn't appear in Kilo

**Check:**
1. File is in `.kilo/agents/` directory
2. Filename matches agent name (`code.md` for `name: code`)
3. YAML frontmatter is valid (starts/ends with `---`)
4. Kilo has been reloaded (close and reopen)

**Fix:**
```bash
# Verify file exists and is readable
ls -la .kilo/agents/code.md

# Check YAML syntax
head -5 .kilo/agents/code.md  # Should show --- markers
```

### Model not recognized

**Check:**
- Model name is from [Anthropic's model list](https://docs.anthropic.com/en/docs/models/overview)
- Common models: `anthropic/claude-opus-4-1`, `anthropic/claude-3-sonnet-20240229`

**Verify:**
```yaml
model: anthropic/claude-opus-4-1  # Valid
# NOT: model: gpt-4  # Invalid - this is not a Claude model
```

### Tools not working

**Check:**
- Tool names are spelled correctly
- Tools are listed in the Tools section
- Kilo IDE supports the requested tool

**Valid tools:**
- `read`, `write`, `execute`, `bash`, `file-operations`

## Advanced Features

### Session Management

Kilo uses `.prompticorn/sessions/` for maintaining context across calls. The agent file specifies this path:

```yaml
state_management: .prompticorn/sessions/
```

This enables:
- Context persistence between calls
- Mode switching within sessions
- Workflow tracking
- Action history

### Environment Variables

Reference environment variables in system prompts:

```markdown
# System Prompt

Use the coding standards defined in:
- Language: $LANGUAGE
- Framework: $FRAMEWORK
- Testing: $TEST_FRAMEWORK
```

These are expanded at runtime.

## Example Variations

### Minimal Version

For lightweight configurations:

```yaml
---
name: code
description: Code generation
model: anthropic/claude-opus-4-1
---

# System Prompt

You are a code generation assistant.
```

### Verbose Version

For comprehensive configurations:

```yaml
---
name: code
description: Code generation and review assistant
model: anthropic/claude-opus-4-1
state_management: .prompticorn/sessions/
---

# System Prompt

[Detailed instructions]

# Tools

[Tool list]

# Skills

[Skill definitions]

# Workflows

[Workflow definitions]

# Subagents

[Subagent list]
```

## Next Steps

1. **Copy this example** to `.kilo/agents/`
2. **Customize** the name, description, and system prompt
3. **Add tools** appropriate for your use case
4. **Reload Kilo** to make the agent available
5. **Test** by running the agent and verifying behavior

## For More Information

- [Kilo Documentation](https://kilo.ai/docs)
- [Builder Documentation](../../docs/BUILDERS.md)
- [Agent Configuration Guide](../../docs/AGENT_CONFIG.md)
