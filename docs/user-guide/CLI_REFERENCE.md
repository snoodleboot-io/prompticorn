# CLI Command Reference

## Overview

The `prompticorn` CLI builds AI coding-assistant configurations from a shared
prompt library. It discovers a registry of agents (and their subagents) bundled
with the package, asks you about your project, and generates tool-specific
configuration files for the assistant you choose.

There are six commands:

| Command | Purpose |
|---------|---------|
| `prompticorn init` | Interactive setup: ask questions, save config, generate tool files |
| `prompticorn list` | List all discovered agents, subagents, and prompt variants |
| `prompticorn validate` | Validate the bundled agents/ registry structure |
| `prompticorn switch` | Switch the active AI assistant and regenerate configs |
| `prompticorn swap` | Change active personas and regenerate configs |
| `prompticorn update` | Edit individual config options interactively |

### Supported AI assistants

`prompticorn` generates configuration for five AI tools (Kilo is offered in two
flavors — CLI and IDE):

| Tool | Selection label | Output |
|------|-----------------|--------|
| Kilo Code (CLI) | `Kilo CLI` (`kilo-cli`) | `.opencode/rules/` with collapsed mode files |
| Kilo Code (IDE) | `Kilo IDE` (`kilo-ide`) | `.kilo/agents/` individual agent files |
| Claude | `Claude` (`claude`) | `.claude/` directory with Markdown agent files and `CLAUDE.md` |
| Cline | `Cline` (`cline`) | `.clinerules` file (concatenated rules) |
| Cursor | `Cursor` (`cursor`) | `.cursor/rules/` directory + `.cursorrules` |
| GitHub Copilot | `Copilot` (`copilot`) | `.github/copilot-instructions.md` |

### Version

The package version is dynamic. `pyproject.toml` declares
`dynamic = ["version"]`, sourced from `prompticorn/__about__.py`, and the real
version (`MAJOR.MINOR.PATCH`) is injected by CI/CD at build time. Local and
editable installs report the development placeholder `0.0.0.dev0`. There is no
hard-coded release number.

## Global Options

- `--help`: Show a help message and exit. Works on the root command and on every
  subcommand (for example, `prompticorn init --help`).

---

## `prompticorn init`

Interactively initialize the prompt configuration for your project. This is the
main setup command. It walks through a series of questions, writes the
configuration to `.prompticorn/.prompticorn.yaml`, and generates the selected
tool's configuration files.

**Usage:**
```bash
prompticorn init
```

`init` is fully interactive — there are no flags or arguments. Navigate with the
up/down arrows (or number keys) and press Enter to accept a default.

### Interactive flow

1. **Which AI assistant would you like to configure?**
   Choose one of: `Kilo CLI`, `Kilo IDE`, `Claude`, `Cline`, `Cursor`,
   `Copilot`. The default selection is `Kilo IDE`.

2. **What type of repository is this?**
   Choose `single-language` or `multi-language-monorepo`.

3. **Which prompt variant would you like to use?**
   - `Minimal` — lightweight prompts for faster tokens and lower cost (default).
   - `Verbose` — detailed prompts with more examples and explanations.

4. **Which personas will be working on this codebase?**
   Multi-select. Only agents and workflows for the selected personas are
   generated (a few universal agents are always included — see
   [`prompticorn swap`](#prompticorn-swap)). Use Space to toggle and Enter to
   confirm.

5. **Language questions.**
   - For `single-language`: pick your primary language, then answer
     language-specific questions (runtime version, package manager, test
     framework, linter, formatter, coverage targets, abstract-class style, etc.).
   - For `multi-language-monorepo`: add folders one at a time (`backend`/
     `frontend` presets or a custom path), pick a language per folder, and answer
     that folder's language questions inline. Missing folders are created on disk.

6. **Project questions** (asked once, language-agnostic). These populate the
   project-level fields of the core conventions. Each has a "Not specified"
   option that renders as a clear placeholder in the conventions.

   | Question | Options |
   |----------|---------|
   | Source-tree layout | `flat` (default), `src` |
   | Database | Not specified, PostgreSQL, MySQL, SQLite, MongoDB, DynamoDB, Redis |
   | ORM / query layer | Not specified, SQLAlchemy, Prisma, Django ORM, GORM, TypeORM, Raw SQL |
   | Error-handling pattern | Not specified, Exceptions, Result type, Error values / codes |
   | Commit message style | Not specified, Conventional Commits, Free-form |
   | Soft PR size limit (lines) | Not specified, 200, 400, 800 |
   | Deployment target | Not specified, AWS Lambda, AWS ECS, Kubernetes, GKE, Vercel, Heroku, On-prem |

   The layout choice is stored as `project.layout_style`. `flat` keeps your
   package/modules at the repo root (the idiomatic default); `src` nests sources
   under a `src/` directory. The per-language standard source tree is rendered
   into the generated core conventions.

7. **Save & generate.** The configuration is written to
   `.prompticorn/.prompticorn.yaml`. If you are switching away from a previously
   configured tool, that tool's old artifacts are removed first. Finally, the
   selected tool's configuration files are generated.

### Example output

```
============================================================
  Configuration saved!
============================================================

  Config file: .prompticorn/.prompticorn.yaml

------------------------------------------------------------
  Generating AI assistant configurations (minimal)...
------------------------------------------------------------
  Created .kilo/agents/code.md
  Created .kilo/agents/test.md
  Created .kilo/agents/review.md
  Created .kilo/agents/refactor.md
  ... (only agents for selected personas, plus universal agents)

============================================================
  Setup complete!
============================================================
```

> The generated configs are populated with your actual spec choices (language,
> runtime, package manager, test framework, linter, formatter, coverage targets,
> abstract-class style) and project settings, woven into the core conventions.

---

## `prompticorn list`

List every agent discovered in the bundled agents registry, together with each
agent's subagents and their `minimal`/`verbose` prompt variants. This command is
discovery-based: it inspects the bundled `prompticorn/agents/` directory through
the agent registry. It does **not** read your generated config or any
`prompts/` directory.

For each agent the base `prompt.md` is shown. For each subagent the available
`minimal/prompt.md` and `verbose/prompt.md` variants are shown. Files present on
disk are marked `✓`; absent files are marked `✗ MISSING`.

**Usage:**
```bash
prompticorn list
```

**Example output:**
```
AGENT REGISTRY

architect  — System design, architecture planning, and technical decisions
  ✓  prompt.md
  subagents:
    architect-data-model
      ✓  minimal/prompt.md
      ✓  verbose/prompt.md
    architect-scaffold
      ✓  minimal/prompt.md
      ✓  verbose/prompt.md

code  — Implement features and make direct code changes
  ✓  prompt.md
  subagents:
    code-implementation
      ✓  minimal/prompt.md
      ✓  verbose/prompt.md

test  — Write comprehensive tests with a coverage-first approach
  ✓  prompt.md
  ...
```

If the registry cannot be loaded, the command prints
`✗ Failed to load agent registry: <reason>` and exits with status `1`.

---

## `prompticorn validate`

Validate the structure of the bundled agents registry and confirm that every
discovered agent loads cleanly. Like `list`, this command is discovery-based and
checks the `agents/` structure — it does **not** validate a flat `prompts/`
layout or your generated output files.

**Checks performed:**
- Each agent has a base `prompt.md` (or its `minimal`/`verbose` variants).
- Each subagent has `minimal/` and `verbose/` variant directories, each with a
  `prompt.md`.
- All discovered agents parse without load errors.

**Usage:**
```bash
prompticorn validate
```

**Example output (success):**
```
▶ Validating agent registry...

  ✓ Registry valid: 25 agents, 82 subagents.
```

**Example output (failure):**
```
▶ Validating agent registry...

  ✗ agents/code/subagents/code-implementation/verbose/prompt.md: missing
  ✗ load error: <details>

  2 issue(s) found.
```

On success the command reports the number of top-level agents and subagents and
exits `0`. On failure it lists each structural issue and exits `1`.

---

## `prompticorn switch`

Switch to a different AI assistant tool. The existing
`.prompticorn/.prompticorn.yaml` configuration is reused; only the output format
and location change. Old artifacts from the previous tool are removed before the
new tool's configuration is generated, and the selected tool is saved back to the
config (`ai_tool`).

**Usage:**
```bash
prompticorn switch [TOOL_NAME]
```

**Argument:**
- `TOOL_NAME` (optional): one of `kilo-cli`, `kilo-ide`, `claude`, `cline`,
  `cursor`, `copilot`. The name is normalized (case and separators are
  ignored, e.g. `Kilo-IDE` → `kilo-ide`). If omitted, an interactive menu is
  shown.

A configuration must already exist; if not, the command prints an error telling
you to run `prompticorn init` first.

**Examples:**
```bash
prompticorn switch              # interactive menu
prompticorn switch kilo-ide     # switch directly to Kilo IDE
prompticorn switch claude       # switch directly to Claude
prompticorn switch cline        # switch directly to Cline
```

**Example output:**
```
============================================================
  Switching AI Tool
============================================================

  Current tool: kilo-ide
  Target tool:   claude

------------------------------------------------------------
  Removing old artifacts...
    Removed directory: .kilo

------------------------------------------------------------
  Generating claude configuration...
    Created CLAUDE.md
    Created .claude/agents/code.md
    ...

============================================================
  Switched to claude!
============================================================
```

---

## `prompticorn swap`

Change which personas (roles) are active and regenerate the configuration with
only the agents relevant to the selected personas. The currently configured tool
and its existing artifacts are reused — `swap` removes the current tool's
generated artifacts and rebuilds them with the new persona filter.

A configuration and a configured AI tool must already exist; otherwise the
command tells you to run `prompticorn init` first.

Universal agents — `ask`, `debug`, `explain`, `plan`, and `orchestrator` — are
always generated regardless of persona selection.

**Usage:**
```bash
prompticorn swap
```

`swap` is interactive only. The persona menu is pre-checked with your current
selection; if you confirm without changing anything, the command reports
"No changes made" and exits without regenerating.

**Example output:**
```
============================================================
  Swap Personas
============================================================

  Current personas: Software Engineer (Fullstack)

------------------------------------------------------------
  Persona Changes
------------------------------------------------------------
  Added: DevOps Engineer

------------------------------------------------------------
  Removing old artifacts...
    Removed directory: .kilo

------------------------------------------------------------
  Regenerating kilo-ide configuration...
    Created .kilo/agents/code.md
    Created .kilo/agents/devops.md
    ...

============================================================
  Personas swapped successfully!
============================================================

  Active personas: Software Engineer (Fullstack), DevOps Engineer
```

---

## `prompticorn update`

Update individual configuration options without re-running the full `init` flow.
An interactive menu lists each editable option with its current value; modified
options are tagged `[changed]` in green. Changes are only written when you choose
**Save & Exit**.

Editable options include:
- Repository type
- Language
- Runtime version
- Package manager
- Test framework
- Linter
- Formatter
- Coverage targets

A configuration must already exist; otherwise the command tells you to run
`prompticorn init` first.

**Usage:**
```bash
prompticorn update
```

**Example output (after saving):**
```
============================================================
  Configuration saved!
============================================================
```

---

## Configuration file

Configuration is stored in `.prompticorn/.prompticorn.yaml`. Key sections:

```yaml
repository:
  type: single_language        # or multi_language_monorepo, mixed

variant: minimal               # or verbose

active_personas:
  - software_engineer
  - devops_engineer

ai_tool: kilo-ide              # last selected AI tool (set by init/switch)

spec:                          # single-language spec (a list for monorepos)
  language: python
  runtime: "3.12"
  package_manager: uv
  test_framework: pytest
  linter: [ruff]
  formatter: [ruff]
  coverage: ...

project:
  layout_style: flat           # flat (default) or src
  database: PostgreSQL
  orm: SQLAlchemy
  error_handling: Exceptions
  commit_style: Conventional Commits
  pr_size: "400"
  deploy_target: AWS Lambda
```

Per-language source-tree layouts are defined in
`prompticorn/configurations/source_layouts.yaml` and rendered into the generated
core conventions based on `project.layout_style`.

---

## Exit codes

- `0`: Success.
- `1`: Error (for example, registry failed to load, or validation found issues).

Interactive commands raise a Click abort when the configuration is missing or
when you cancel the operation (Ctrl+C / Esc).

---

## Quick reference

| Command | Description | Interactive |
|---------|-------------|-------------|
| `prompticorn init` | Initialize configuration and generate tool files | Yes |
| `prompticorn list` | List discovered agents, subagents, and variants | No |
| `prompticorn validate` | Validate the bundled agents registry structure | No |
| `prompticorn switch [TOOL]` | Switch AI tool and regenerate configs | Optional |
| `prompticorn swap` | Change active personas and regenerate configs | Yes |
| `prompticorn update` | Edit individual config options | Yes |
