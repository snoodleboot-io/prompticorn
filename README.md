# Promptosaurus

A shared library of AI coding assistant prompt files. Edit once in `prompts/`, build for any tool with a single command.

Kilo Code is the primary target. Cline, Cursor, and GitHub Copilot are derived from the same source.

## Install

Install via pip:

```bash
pip install promptosaurus
```

Or with uv:

```bash
uv add promptosaurus
```

This installs the `promptosaurus` CLI command.

## Quick Start

### 1. Initialize your project

Run from inside your project directory:

```bash
cd my-project
promptosaurus init
```

This interactive command will:
1. Ask about your repository type (single-language or multi-folder)
2. Configure your language, runtime, package manager, and testing framework
3. Select which AI assistants to configure (kilo, cline, cursor, copilot — multiple allowed)
4. Generate all selected configurations automatically

### 2. List available modes

```bash
promptosaurus list
```

Shows all modes and their registered prompt files.

### 3. Validate configuration

```bash
promptosaurus validate
```

Check for missing files and unregistered orphans.

## Commands

| Command | Description |
|---------|-------------|
| `promptosaurus init` | Interactively initialize prompt configuration for your project |
| `promptosaurus list` | List all registered modes and their prompt files |
| `promptosaurus switch` | Switch to a different AI assistant tool |
| `promptosaurus update` | Update configuration options interactively |
| `promptosaurus validate` | Check that all registered prompt files exist and no files are missing |

## Workflow

### Adding prompts to your project

1. Run `promptosaurus init` to generate configurations
2. Edit files in the generated directories (e.g., `.kilo/rules/`)
3. Run `promptosaurus init` again to regenerate

### Updating prompts

Edit the source prompts, then re-run:

```bash
promptosaurus init
```

## Mode Reference

| Mode | Key | Purpose |
|------|-----|---------|
| Architect | `architect` | Scaffold projects, task breakdowns, data models |
| Test | `test` | Coverage-first test writing |
| Refactor | `refactor` | Structural changes, behavior preserved |
| Document | `document` | Docstrings, READMEs, changelogs |
| Explain | `explain` | Code walkthroughs for onboarding |
| Migration | `migration` | Dependency upgrades, framework ports |
| Code | `code` | Feature implementation, boilerplate |
| Review | `review` | Code, performance, accessibility review |
| Debug | `debug` | Root cause, log analysis, rubber duck |
| Ask | `ask` | Q&A, decision logs |
| Security | `security` | Security review (code and infra) |
| Compliance | `compliance` | SOC 2, ISO 27001, GDPR, HIPAA, PCI-DSS |
| Orchestrator | `orchestrator` | CI/CD, DevOps, PR descriptions |

## Tool Output

| Tool | Output Directory/Files |
|------|----------------------|
| Kilo Code | `.kilo/rules/` (always-on) + `.kilo/rules-{mode}/` (per-mode) + `.kilocodemodes` + `.kiloignore` |
| Cline | `.clinerules` (all rules concatenated) |
| Cursor | `.cursor/rules/{mode}/*.mdc` + `.cursorrules` (legacy) |
| GitHub Copilot | `.github/copilot-instructions.md` + `.github/instructions/{mode}.instructions.md` |

## Development

To contribute or develop locally:

```bash
# Clone the repository
git clone https://github.com/snoodleboot-io/promptosaurus.git
cd promptosaurus

# Install in development mode
pip install -e .

# Or with uv
uv pip install -e .
```
