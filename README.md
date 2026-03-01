# Prompt Library

A shared library of AI coding assistant prompt files. Edit once in `prompts/`,
build for any tool with a single command.

Kilo Code is the primary target. Cline, Cursor, and GitHub Copilot are derived
from the same source.

## Versioning

This project uses [derived versioning](docs/derived-versioning.md) designed for trunk-based development:

- **Major**: Human-controlled via `.major-version` file (breaking changes)
- **Minor**: Count of `feat/` branches merged since last major tag
- **Patch**: Count of `bug/`/`hotfix/`/`security/` branches merged since last feature

Branch naming conventions:
- `feat/*` → increments minor version
- `bug/*`, `hotfix/*`, `security/*` → increments patch version

Version is calculated at merge time—no version file conflicts.

## Structure

```
prompt-library/
├── promptcli/                     ← installable package
│   ├── prompts/                   ← THE SOURCE OF TRUTH — edit files here only
│   │   ├── core-system.md         ← always-on base behaviors (all modes)
│   │   ├── core-conventions.md    ← ⚙️ fill in for each project
│   │   ├── architect-*.md
│   │   ├── test-*.md
│   │   ├── refactor-*.md
│   │   ├── document-*.md
│   │   ├── explain-*.md
│   │   ├── migration-*.md
│   │   ├── code-*.md
│   │   ├── review-*.md
│   │   ├── debug-*.md
│   │   ├── ask-*.md
│   │   ├── security-*.md
│   │   ├── compliance-*.md
│   │   └── orchestrator-*.md
│   ├── builders/
│   │   ├── kilo.py
│   │   ├── cline.py
│   │   ├── cursor.py
│   │   └── copilot.py
│   ├── registry.py                ← mode/file manifest — edit here to add modes
│   └── cli.py                     ← Click entry point
│
└── pyproject.toml                 ← uv pip install -e . → `prompt` command
```

## Install

Requires [uv](https://docs.astral.sh/uv/). Built with [hatchling](https://hatch.pypa.io/).

```bash
uv pip install -e .
```

This registers the `prompt` command globally.

To sync dependencies into a project-local venv:

```bash
uv sync
```

## Commands

### Build for a specific tool

```bash
# Run from inside your project directory — output lands there by default
cd my-project

prompt build kilo       # → .kilo/
prompt build cline      # → .clinerules
prompt build cursor     # → .cursor/rules/ + .cursorrules (legacy)
prompt build copilot    # → .github/copilot-instructions.md + .github/instructions/
prompt build all        # → all of the above
```

### Target a different directory

```bash
prompt build kilo --output /path/to/my-project
prompt build all  --output ~/projects/my-app
```

### Preview without writing

```bash
prompt build kilo --dry-run
prompt build all  --dry-run
```

### Inspect and validate

```bash
prompt list       # show all modes and their registered prompt files
prompt validate   # check for missing files and unregistered orphans
```

## Workflow

### 1. Setup for a new project

```bash
# 1. Fill in your project's coding standards
$EDITOR prompts/core-conventions.md

# 2. Build the config for your tool of choice
cd my-project
prompt build kilo

# 3. Commit the generated config
git add .kilo/
git commit -m "chore: add Kilo Code prompt config"
```

### 2. Updating prompts

```bash
# Edit the source file
$EDITOR prompts/security-review.md

# Rebuild — just the tools you use
prompt build kilo --output ~/projects/my-project
```

### 3. Adding a new prompt file to an existing mode

1. Drop the `.md` file in `prompts/`
2. Add the filename to `MODE_FILES[mode]` in `promptcli/registry.py`
3. Add a `CONCAT_ORDER` entry if the file should appear in Cline/Cursor/Copilot output
4. Run `prompt validate` to confirm
5. Run `prompt build all`

### 4. Adding a new mode

1. Add an entry to `MODES` in `promptcli/registry.py`
2. Add an entry to `MODE_FILES` with its prompt files
3. Add a `COPILOT_APPLY` glob pattern
4. Run `prompt validate` and `prompt build all`

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

## Tool Output Reference

| Tool | Command | What gets written |
|------|---------|-------------------|
| Kilo Code | `prompt build kilo` | `.kilo/rules/` (always-on) + `.kilo/rules-{mode}/` (per-mode) |
| Cline | `prompt build cline` | `.clinerules` (all rules concatenated) |
| Cursor | `prompt build cursor` | `.cursor/rules/{mode}/*.mdc` + `.cursorrules` (legacy) |
| GitHub Copilot | `prompt build copilot` | `.github/copilot-instructions.md` + `.github/instructions/{mode}.instructions.md` |
