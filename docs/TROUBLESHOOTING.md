# Troubleshooting Guide

This guide helps you diagnose and fix common issues with promptosaurus.

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

# Promptosaurus requires Python 3.10+
# If you have an older version, upgrade Python or use pyenv
```

**Supported versions:** Python 3.10, 3.11, 3.12, 3.13, 3.14

### Dependency Conflicts

**Problem:** `pip install promptosaurus` fails with dependency conflicts

**Solution:**
```bash
# Use a virtual environment to avoid conflicts
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install promptosaurus

# Or use uv (recommended)
uv venv
source .venv/bin/activate
uv pip install promptosaurus
```

### Permission Errors

**Problem:** `Permission denied` errors during installation

**Solution:**
```bash
# Don't use sudo - use virtual environment instead
python -m venv .venv
source .venv/bin/activate
pip install promptosaurus

# Or install to user directory
pip install --user promptosaurus
```

### Platform-Specific Issues

**Windows:**
```bash
# If you get encoding errors
set PYTHONIOENCODING=utf-8
pip install promptosaurus
```

**macOS/Linux:**
```bash
# If curses library errors occur
pip install windows-curses  # Only on Windows
```

---

## Configuration Issues

### .promptosaurus/.promptosaurus.yaml Not Found

**Problem:** Commands fail with "Configuration file not found"

**Solution:**
```bash
# Initialize configuration first
promptosaurus init

# This creates .promptosaurus/.promptosaurus.yaml in your project root
```

**Expected location:** `./.promptosaurus/.promptosaurus.yaml` (current directory)

### Invalid YAML Syntax

**Problem:** `YAMLError: invalid syntax`

**Solution:**
```bash
# Validate your YAML
cat .promptosaurus/.promptosaurus.yaml

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
promptosaurus init

# Or edit .promptosaurus/.promptosaurus.yaml directly
# Update spec.language and spec.runtime fields
```

### Persona Selection Problems

**Problem:** No agents generated after persona selection

**Solution:**
```bash
# Check your persona selection in .promptosaurus/.promptosaurus.yaml
cat .promptosaurus/.promptosaurus.yaml | grep -A 5 personas

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
promptosaurus list

# Supported builders: kilo-cli, kilo-ide, claude, cline, cursor, copilot
# Check spelling in .promptosaurus/.promptosaurus.yaml or command
```

### Validation Failures

**Problem:** `BuilderValidationError: Agent validation failed`

**Solution:**
```bash
# Check agent prompt files exist
ls -la promptosaurus/agents/

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
ls promptosaurus/agents/*/prompt.md

# Fallback: System will try verbose if minimal missing
# Check logs for warnings
```

---

## Agent Discovery Issues

### Agents Not Found

**Problem:** `promptosaurus list` shows no agents

**Solution:**
```bash
# Check agents directory exists
ls -la promptosaurus/agents/

# Verify agent structure
        ls promptosaurus/agents/code/prompt.md

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
find promptosaurus/agents -name "prompt.md"

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
ls promptosaurus/agents/debug/subagents/

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
rm -rf .promptosaurus/cache/

# Re-run discovery
promptosaurus validate
```

---

## CLI Command Failures

### `init` Command Failures

**Problem:** `promptosaurus init` fails midway

**Solution:**
```bash
# Check if .promptosaurus/.promptosaurus.yaml already exists
        ls -la .promptosaurus/.promptosaurus.yaml

        # Backup and remove old config
        mv .promptosaurus/.promptosaurus.yaml .promptosaurus/.promptosaurus.yaml.backup

        # Re-run init
        promptosaurus init

        # If interactive UI fails, check terminal compatibility
        export TERM=xterm-256color
        promptosaurus init
```

### `list` Command Empty Results

**Problem:** `promptosaurus list` shows nothing

**Solution:**
```bash
# Check configuration exists
cat .promptosaurus/.promptosaurus.yaml

# Verify agents directory
ls promptosaurus/agents/

# Check persona filtering
# If personas selected, some agents may be filtered out
```

### `validate` Command Errors

**Problem:** `promptosaurus validate` reports errors

**Solution:**
```bash
# Read error messages carefully
promptosaurus validate

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
promptosaurus switch --help

        # Valid tools: kilo-cli, kilo-ide, claude, cline, cursor, copilot

# Check persona names
cat promptosaurus/personas/personas.yaml
```

---

## Common Error Messages

### `Click.exceptions.UsageError: No such command`

**Cause:** Invalid command name

**Fix:**
```bash
# List available commands
promptosaurus --help

# Valid commands: init, list, validate, switch, swap, update
```

### `FileNotFoundError: .promptosaurus/.promptosaurus.yaml`

**Cause:** Configuration not initialized

**Fix:**
```bash
promptosaurus init
```

### `YAMLError: could not determine a constructor`

**Cause:** Invalid YAML syntax

**Fix:** Check YAML indentation and quotes

### `RegistryException: Agent 'xyz' not found`

**Cause:** Agent doesn't exist or name misspelled

**Fix:**
```bash
# List available agents
promptosaurus list

# Check agent directory
ls promptosaurus/agents/
```

### `UnsupportedFeatureError: Builder does not support 'xyz'`

**Cause:** Builder doesn't support requested feature

**Fix:** Check builder capabilities in documentation

---

## Debugging Tips

### Enable Verbose Mode

```bash
# Check stderr output for diagnostic information
promptosaurus init 2> debug.log
```

### Check Logs

```bash
# Logs typically go to stderr
promptosaurus init 2> debug.log

# Review log file
cat debug.log
```

### Verify Installation

```bash
# Check promptosaurus is installed
which promptosaurus

# Check version
pip show promptosaurus

# Test import
python -c "import promptosaurus; print(promptosaurus.__file__)"
```

### Clear Cache

```bash
# Remove cache directories
rm -rf .promptosaurus/cache/
rm -rf __pycache__/
rm -rf .pytest_cache/

# Re-run command
promptosaurus init
```

### Check File Permissions

```bash
# Ensure files are readable
        ls -la .promptosaurus/.promptosaurus.yaml
        ls -la promptosaurus/agents/

        # Fix permissions if needed
        chmod 644 .promptosaurus/.promptosaurus.yaml
        chmod -R 755 promptosaurus/
```

### Validate YAML

```bash
# Use Python to validate YAML
python -c "import yaml; yaml.safe_load(open('.promptosaurus/.promptosaurus.yaml'))"

# Or use online YAML validator
```

### Check Directory Structure

```bash
# Verify expected structure
tree promptosaurus/agents/ -L 3

# Or
find promptosaurus/agents -type f -name "prompt.md"
```

---

## Getting More Help

### GitHub Issues
Report bugs or request help: [GitHub Issues](https://github.com/snoodleboot-io/promptosaurus/issues)

### Documentation
- [README.md](../README.md) - Overview
- [GETTING_STARTED.md](./user-guide/GETTING_STARTED.md) - Getting started guide
- [API_REFERENCE.reference.md](./reference/API_REFERENCE.reference.md) - API documentation

### Common Solutions Checklist

- [ ] Python 3.10+ installed
- [ ] Virtual environment activated
- [ ] `promptosaurus init` run successfully
- [ ] `.promptosaurus/.promptosaurus.yaml` exists and valid
- [ ] Agents directory exists with proper structure
- [ ] File permissions correct
- [ ] No YAML syntax errors

If all checks pass and issue persists, please file a GitHub issue with:
- Error message
- `pip show promptosaurus` output
- `.promptosaurus/.promptosaurus.yaml` content (redact sensitive info)
- Output of `promptosaurus validate`
