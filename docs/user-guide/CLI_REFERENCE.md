# CLI Command Reference

## Overview

The Prompticorn CLI provides commands for initializing, configuring, and managing AI assistant configurations. Built with Click, it offers an intuitive interface for generating tool-specific configurations from the Intermediate Representation (IR) models.

## Global Options

All commands support these global options:

- `--help`: Show help message and exit

## Commands

### `prompticorn list`

List all registered modes and their associated prompt files.

**Usage:**
```bash
prompticorn list
```

**Options:**
- None

**Example Output:**
```
ALWAYS ON (all modes)
  ✓ agents/core/system.md
  ✓ agents/core/conventions.md
  ✓ agents/core/session.md
  ...

ARCHITECT MODE  [architect]
  ✓ agents/architect/subagents/architect-scaffold.md
  ✓ agents/architect/subagents/architect-task-breakdown.md
  ✓ agents/architect/subagents/architect-data-model.md

TEST MODE  [test]
  ✓ agents/test/subagents/test-strategy.md
  ...
```

### `prompticorn init`
Interactively initialize prompt configuration for your project.

**Usage:**
```bash
prompticorn init
```

**Note:** `init` is interactive only. It prompts you through all configuration steps.

**Workflow:**
1. Select AI assistant to configure (Kilo CLI, Kilo IDE, Cline, Cursor, Copilot)
2. Select repository type (single language, multi-language monorepo, mixed)
3. Choose prompt variant (Minimal or Verbose)
4. Select personas for role-based filtering
5. Configure language/runtime/settings based on selections
6. Save configuration and generate initial artifacts

**Examples:**
```bash
# Interactive initialization
prompticorn init
```

### `prompticorn switch`
Switch to a different AI assistant tool.

**Usage:**
```bash
prompticorn switch [TOOL_NAME]
```

**Arguments:**
- `TOOL_NAME`: Target tool (kilo-cli, kilo-ide, cline, cursor, copilot)

**If no tool name provided:** Shows interactive menu to select target tool.

**Examples:**
```bash
# Switch directly to Cline
prompticorn switch cline

# Interactive tool selection
prompticorn switch

# Switch to GitHub Copilot
prompticorn switch copilot
```

### `prompticorn swap`
Swap active personas and regenerate configurations.

**Usage:**
```bash
prompticorn swap
```

**Note:** `swap` is interactive only. It shows a menu to select personas.

**Examples:**
```bash
# Interactive persona selection
prompticorn swap
```

### `prompticorn update`
Update configuration options interactively.

**Usage:**
```bash
prompticorn update
```

**Note:** `update` is interactive only. It shows a menu to change specific options.

**If no arguments provided:** Shows interactive menu to update configuration.

**Examples:**
```bash
# Interactive configuration update
prompticorn update
```

### `prompticorn validate`
Validate configuration integrity.

**Usage:**
```bash
prompticorn validate
```

**Checks Performed:**
- Configuration file exists and is valid
- All registered prompt files exist on disk
- No orphan files in prompts directory
- All concat_order entries reference registered files
- Valid tool configuration
- Valid persona configuration

**Examples:**
```bash
# Validate current configuration
prompticorn validate
```

## Advanced Usage

### Direct Builder Access

For programmatic access, use the Python API:

```python
from prompticorn.builders.factory import BuilderFactory
from prompticorn.ir.models import Agent
from prompticorn.builders.base import BuildOptions

# Get builder
builder = BuilderFactory.get_builder("kilo")

# Create agent
agent = Agent(
    name="code",
    description="Write and review code",
    system_prompt="You are an expert programmer...",
    tools=["read", "write", "bash"],
    skills=["implementation", "debugging"]
)

# Build agent
output = builder.build(agent, BuildOptions(variant="verbose"))
```

### Configuration File

The configuration is stored in `.prompticorn/.prompticorn.yaml` by default. Key sections include:

```yaml
repository:
  type: single_language  # or multi_language_monorepo, mixed
  # ... other repository settings

variant: minimal  # or verbose

active_personas:
  - software_engineer
  - devops_engineer

ai_tool: kilo-ide  # currently selected AI tool

# ... tool-specific and language-specific settings
```

## Environment Variables

The CLI respects these environment variables:

- `PROMPTICORN_PROMPTS_PATH`: Path to prompts directory (default: `prompticorn/prompts`)
- `PROMPTICORN_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Exit Codes

The CLI uses standard exit codes:

- `0`: Success
- `1`: General error
- `2`: Invalid command or arguments
- `3`: Configuration error
- `4`: Validation error
- `130`: Operation cancelled by user (Ctrl+C)

## Examples

### Complete Setup Workflow
```bash
# 1. Initialize configuration
prompticorn init
#   -> Select: Kilo IDE
#   -> Select: Single language repository
#   -> Select: Verbose variant
#   -> Select: Software Engineer, DevOps Engineer personas
#   -> Configure: Python 3.11, uv, pytest, etc.

# 2. Verify configuration
prompticorn validate

# 3. Switch to different tool if needed
prompticorn switch cline

# 4. Update personas for different task
prompticorn swap

# 5. Regenerate configurations
prompticorn init  # will reuse existing config and regenerate
```

### Automation Scripts
```bash
#!/bin/bash
# Generate configurations for all tools

# Ensure configuration exists
if [ ! -f .prompticorn/.prompticorn.yaml ]; then
    echo "Please run 'prompticorn init' first"
    exit 1
fi

# Generate for each tool
for tool in kilo-ide kilo-cli cline cursor copilot; do
    echo "Generating $tool configuration..."
    prompticorn switch $tool
done

echo "All configurations generated!"
```
