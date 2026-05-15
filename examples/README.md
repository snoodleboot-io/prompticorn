# Prompticorn Builder Examples

This directory contains comprehensive examples of builder outputs for all 5 supported tools: **Kilo**, **Cline**, **Claude**, **GitHub Copilot**, and **Cursor**.

Each example demonstrates a simple "code" agent configured with default values, showing exactly what each builder produces.

## Overview

| Tool | Format | File | Use Case |
|------|--------|------|----------|
| **Kilo** | YAML + Markdown | `.kilo/agents/code.md` | Kilo IDE agent configuration |
| **Cline** | Markdown | `.clinerules` | Cline AI rules and instructions |
| **Claude** | JSON | `code.json` | Claude Messages API integration |
| **GitHub Copilot** | YAML + Markdown | `.github/instructions/code.md` | Copilot in GitHub Codespaces |
| **Cursor** | Markdown | `.cursorrules` | Cursor IDE custom rules |

## Quick Links

- [Kilo Example](./kilo/README.md) - `.kilo/agents/code.md`
- [Cline Example](./cline/README.md) - `.clinerules`
- [Claude Example](./claude/README.md) - `code.json`
- [GitHub Copilot Example](./copilot/README.md) - `.github/instructions/code.md`
- [Cursor Example](./cursor/README.md) - `.cursorrules`

## Common Agent Configuration

All examples use the same base agent:

```
Name:        code
Description: Code generation and review assistant
System Prompt: You are an expert code generation assistant. Write clean, 
               well-documented Python code following SOLID principles.
Tools:       read, write, execute
Model:       anthropic/claude-opus-4-1
```

## How to Use These Examples

### Option 1: Copy & Customize

1. **Choose your tool**: Select the subdirectory for your IDE/tool
2. **Copy the example file**: Copy the provided example to your project
3. **Customize the content**: Edit the system prompt, tools, and descriptions
4. **Deploy**: Follow the "Installation" section in each tool's README

### Option 2: Generate from Prompticorn

Use the Prompticorn CLI to generate custom outputs:

```bash
# Install prompticorn
pip install prompticorn

# Initialize configuration (runs setup wizard)
prompticorn init

# Switch to a different tool output
prompticorn switch
```

### Option 3: Use as Templates

These examples serve as templates for creating new agents:

1. Study the structure in your chosen tool's example
2. Create a new agent with different name/description
3. Generate output using Prompticorn
4. Deploy following the tool-specific installation guide

## What's Included in Each Example

Each subdirectory contains:

- **README.md** - Detailed guide for that tool
  - What the example shows
  - Where to place the file in your project
  - How to customize it
  - Troubleshooting tips

- **Example output file**
  - `code.yml` (Kilo)
  - `code.clinerules` (Cline)
  - `code.json` (Claude)
  - `copilot-instructions.md` (Copilot)
  - `.cursorrules` (Cursor)

Each file is production-ready and copy-paste compatible.

## Key Features Demonstrated

All examples show:

✅ **System Prompt** - AI behavior definition  
✅ **Tools** - Available functions (read, write, execute)  
✅ **Metadata** - Configuration (name, description, model)  
✅ **Tool-Specific Features** - Frontmatter, workflows, constraints

## Customization Guide

### Change the Agent Name

1. In each example, replace `code` with your agent name (e.g., `test`, `architect`)
2. Update the description accordingly
3. Adjust the system prompt for the new role

### Add/Remove Tools

1. Edit the `tools:` list in the metadata section
2. Update the tools description to match available tools
3. Available tools: `read`, `write`, `execute`, `bash`, `file-operations`

### Customize System Prompt

Each example includes a sample system prompt. Customize it by:

1. Changing the role/expertise area
2. Adding specific behavior rules
3. Specifying output format preferences
4. Including domain-specific instructions

### Add Workflows (Kilo & Copilot)

If using Kilo or Copilot, add workflow sections:

```markdown
## Workflows

### Code Review Workflow
1. Read the code
2. Analyze for bugs
3. Check test coverage
4. Provide feedback
```

## Example Walkthrough

Let's say you want to create a "test" agent instead of "code":

### Step 1: Choose Your Tool
```
Select: Kilo IDE (.kilo/agents/test.md)
```

### Step 2: Copy Example
```bash
cp examples/kilo/code.yml .kilo/agents/test.md
```

### Step 3: Customize
```yaml
---
name: "test"
description: "Test writing and coverage assistant"
model: "anthropic/claude-opus-4-1"
state_management: ".prompticorn/sessions/"
---

# System Prompt

You are an expert test engineer. Write comprehensive, 
well-structured tests with high coverage...
```

### Step 4: Deploy
```bash
# Restart Kilo IDE to load the new agent
kilo restart
```

## File Placement Reference

When using these examples, ensure correct placement:

```
your-project/
├── .kilo/
│   └── agents/
│       └── code.md          ← Kilo example
├── .github/
│   └── instructions/
│       └── code.md          ← Copilot example
├── .clinerules              ← Cline example
├── .cursorrules             ← Cursor example
└── code.json                ← Claude example (custom location)
```

## Next Steps

1. **Pick a tool**: Choose the IDE/tool you use most
2. **Read the README**: Understand the format and features
3. **Copy the example**: Get started immediately
4. **Customize**: Adapt to your needs
5. **Deploy**: Integrate into your workflow

## For More Information

- [Prompticorn Documentation](../docs/README.md)
- [Builder API Reference](../docs/BUILDERS.md)
- [Agent Configuration Guide](../docs/AGENT_CONFIG.md)

## Questions?

- Check the tool-specific README for common issues
- See [Troubleshooting Guide](../docs/TROUBLESHOOTING.md)
- Open an issue at https://github.com/Kilo-Org/prompticorn/issues
