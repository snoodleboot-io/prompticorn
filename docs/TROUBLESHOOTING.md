# Troubleshooting Guide

This guide helps you diagnose and fix common issues with prompticorn.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Configuration Issues](#configuration-issues)
- [Builder Errors](#builder-errors)
- [Agent Discovery Issues](#agent-discovery-issues)
- [CLI Command Failures](#cli-command-failures)
- [Common Error Messages](#common-error-messages)
- [Debugging Tips](#debugging-tips)

---

## Installation Issues

### Python Version Compatibility

**Problem:** Installation fails with version errors

**Solution:**
```bash
# Check your Python version
python --version

# Prompticorn requires Python 3.10+
# If you have an older version, upgrade Python or use pyenv
```

**Supported versions:** Python 3.10, 3.11, 3.12, 3.13, 3.14

### Dependency Conflicts

**Problem:** `pip install prompticorn` fails with dependency conflicts

**Solution:**
```bash
# Use a virtual environment to avoid conflicts
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install prompticorn

# Or use uv (recommended)
uv venv
source .venv/bin/activate
uv pip install prompticorn
```

### Permission Errors

**Problem:** `Permission denied` errors during installation

**Solution:**
```bash
# Don't use sudo - use virtual environment instead
python -m venv .venv
source .venv/bin/activate
pip install prompticorn

# Or install to user directory
pip install --user prompticorn
```

### Platform-Specific Issues

**Windows:**
```bash
# If you get encoding errors
set PYTHONIOENCODING=utf-8
pip install prompticorn
```

**macOS/Linux:**
```bash
# If curses library errors occur
pip install windows-curses  # Only on Windows
```

---

## Configuration Issues

### .prompticorn/.prompticorn.yaml Not Found

**Problem:** Commands fail with "Configuration file not found"

**Solution:**
```bash
# Initialize configuration first
prompticorn init

# This creates .prompticorn/.prompticorn.yaml in your project root
```

**Expected location:** `./.prompticorn/.prompticorn.yaml` (current directory)

### Invalid YAML Syntax

**Problem:** `YAMLError: invalid syntax`

**Solution:**
```bash
# Validate your YAML
cat .prompticorn/.prompticorn.yaml

# Common issues:
# - Tabs instead of spaces (use spaces only)
# - Missing quotes around values with special characters
# - Incorrect indentation
```

**Example valid YAML:**
```yaml
version: "1.0"
repository:
  type: "single-language"
spec:
  language: "python"
  runtime: "3.12"
  package_manager: "uv"
```

### Language/Runtime Detection Failures

**Problem:** Language not detected or incorrect runtime

**Solution:**
```bash
# Re-run init and manually select language
prompticorn init

# Or edit .prompticorn/.prompticorn.yaml directly
# Update spec.language and spec.runtime fields
```

### Persona Selection Problems

**Problem:** No agents generated after persona selection

**Solution:**
```bash
# Check your persona selection in .prompticorn/.prompticorn.yaml
cat .prompticorn/.prompticorn.yaml | grep -A 5 personas

# Ensure at least one persona is selected
# Universal agents (ask, debug, explain) are always available
```

---

## Builder Errors

### Builder Not Found

**Problem:** `BuilderNotFoundError: Builder 'xyz' not found`

**Solution:**
```bash
# List available builders
prompticorn list

# Supported builders: kilo-cli, kilo-ide, claude, cline, cursor, copilot
# Check spelling in .prompticorn/.prompticorn.yaml or command
```

### Validation Failures

**Problem:** `BuilderValidationError: Agent validation failed`

**Solution:**
```bash
# Check agent prompt files exist
ls -la prompticorn/agents/

# Ensure each agent has:
# - prompt.md (top-level agent)
# - Valid YAML frontmatter
# - Required fields: name, description
```

### Output File Creation Failures

**Problem:** Cannot write output files

**Solution:**
```bash
# Check write permissions
ls -ld .kilo .clinerules .cursorrules

# Ensure directories exist or can be created
mkdir -p .kilo/rules .cursor/rules

# Check disk space
df -h .
```

### Variant Selection Issues

**Problem:** "Variant 'minimal' not found"

**Solution:**
```bash
# Check if agent prompt files exist
ls prompticorn/agents/*/prompt.md

# Fallback: System will try verbose if minimal missing
# Check logs for warnings
```

---

## Agent Discovery Issues

### Agents Not Found

**Problem:** `prompticorn list` shows no agents

**Solution:**
```bash
# Check agents directory exists
ls -la prompticorn/agents/

# Verify agent structure
        ls prompticorn/agents/code/prompt.md

        # Expected structure:
        # agents/
        #   agent_name/
        #     prompt.md
```

### Missing prompt.md Files

**Problem:** `MissingFileError: prompt.md not found`

**Solution:**
```bash
# Each agent needs at least one variant
# Check which agents are missing prompts
find prompticorn/agents -name "prompt.md"

# Create missing prompt.md with minimum structure:
---
name: agent_name
description: Brief description
---

# System Prompt
Your prompt content here.
```

### Subagent Discovery Failures

**Problem:** Subagents not discovered

**Solution:**
```bash
# Check subagent structure
ls prompticorn/agents/debug/subagents/

# Expected:
# agents/
#   debug/
#     subagents/
#       rubber-duck/
#         minimal/
#           prompt.md
```

### Registry Cache Issues

**Problem:** Changes to agents not reflected

**Solution:**
```bash
# Clear cache (if implemented)
rm -rf .prompticorn/cache/

# Re-run discovery
prompticorn validate
```

---

## CLI Command Failures

### `init` Command Failures

**Problem:** `prompticorn init` fails midway

**Solution:**
```bash
# Check if .prompticorn/.prompticorn.yaml already exists
        ls -la .prompticorn/.prompticorn.yaml

        # Backup and remove old config
        mv .prompticorn/.prompticorn.yaml .prompticorn/.prompticorn.yaml.backup

        # Re-run init
        prompticorn init

        # If interactive UI fails, check terminal compatibility
        export TERM=xterm-256color
        prompticorn init
```

### `list` Command Empty Results

**Problem:** `prompticorn list` shows nothing

**Solution:**
```bash
# Check configuration exists
cat .prompticorn/.prompticorn.yaml

# Verify agents directory
ls prompticorn/agents/

# Check persona filtering
# If personas selected, some agents may be filtered out
```

### `validate` Command Errors

**Problem:** `prompticorn validate` reports errors

**Solution:**
```bash
# Read error messages carefully
prompticorn validate

# Common issues:
# - Missing prompt files
# - Invalid YAML frontmatter
# - Incorrect directory structure
```

### `switch`/`swap` Failures

**Problem:** Cannot switch tools or swap personas

**Solution:**
```bash
# Check valid tool names
prompticorn switch --help

        # Valid tools: kilo-cli, kilo-ide, claude, cline, cursor, copilot

# Check persona names
cat prompticorn/personas/personas.yaml
```

---

## Common Error Messages

### `Click.exceptions.UsageError: No such command`

**Cause:** Invalid command name

**Fix:**
```bash
# List available commands
prompticorn --help

# Valid commands: init, list, validate, switch, swap, update
```

### `FileNotFoundError: .prompticorn/.prompticorn.yaml`

**Cause:** Configuration not initialized

**Fix:**
```bash
prompticorn init
```

### `YAMLError: could not determine a constructor`

**Cause:** Invalid YAML syntax

**Fix:** Check YAML indentation and quotes

### `RegistryException: Agent 'xyz' not found`

**Cause:** Agent doesn't exist or name misspelled

**Fix:**
```bash
# List available agents
prompticorn list

# Check agent directory
ls prompticorn/agents/
```

### `UnsupportedFeatureError: Builder does not support 'xyz'`

**Cause:** Builder doesn't support requested feature

**Fix:** Check builder capabilities in documentation

---

## Debugging Tips

### Enable Verbose Mode

```bash
# Check stderr output for diagnostic information
prompticorn init 2> debug.log
```

### Check Logs

```bash
# Logs typically go to stderr
prompticorn init 2> debug.log

# Review log file
cat debug.log
```

### Verify Installation

```bash
# Check prompticorn is installed
which prompticorn

# Check version
pip show prompticorn

# Test import
python -c "import prompticorn; print(prompticorn.__file__)"
```

### Clear Cache

```bash
# Remove cache directories
rm -rf .prompticorn/cache/
rm -rf __pycache__/
rm -rf .pytest_cache/

# Re-run command
prompticorn init
```

### Check File Permissions

```bash
# Ensure files are readable
        ls -la .prompticorn/.prompticorn.yaml
        ls -la prompticorn/agents/

        # Fix permissions if needed
        chmod 644 .prompticorn/.prompticorn.yaml
        chmod -R 755 prompticorn/
```

### Validate YAML

```bash
# Use Python to validate YAML
python -c "import yaml; yaml.safe_load(open('.prompticorn/.prompticorn.yaml'))"

# Or use online YAML validator
```

### Check Directory Structure

```bash
# Verify expected structure
tree prompticorn/agents/ -L 3

# Or
find prompticorn/agents -type f -name "prompt.md"
```

---

## Getting More Help

### GitHub Issues
Report bugs or request help: [GitHub Issues](https://github.com/snoodleboot-io/prompticorn/issues)

### Documentation
- [README.md](../README.md) - Overview
- [GETTING_STARTED.md](./user-guide/GETTING_STARTED.md) - Getting started guide
- [API_REFERENCE.reference.md](./reference/API_REFERENCE.reference.md) - API documentation

### Common Solutions Checklist

- [ ] Python 3.10+ installed
- [ ] Virtual environment activated
- [ ] `prompticorn init` run successfully
- [ ] `.prompticorn/.prompticorn.yaml` exists and valid
- [ ] Agents directory exists with proper structure
- [ ] File permissions correct
- [ ] No YAML syntax errors

If all checks pass and issue persists, please file a GitHub issue with:
- Error message
- `pip show prompticorn` output
- `.prompticorn/.prompticorn.yaml` content (redact sensitive info)
- Output of `prompticorn validate`
