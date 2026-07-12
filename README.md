# prompticorn

A unified, tool-agnostic prompt architecture for managing AI coding-assistant configurations across 5 assistants.

> **Version:** the published version is dynamic. `pyproject.toml` declares
> `dynamic = ["version"]` sourced from `prompticorn/__about__.py`, and CI/CD injects the
> real `MAJOR.MINOR.PATCH` at build time. Local and editable installs report `0.0.0.dev0`.
> Check your installed version with `pip show prompticorn`.

Define your project's agents, conventions, and personas once, then generate the
right config for whichever assistant your team uses:

- **Kilo** Code — IDE (`.kilo/agents/`) and CLI (`.opencode/rules/`)
- **Cline** — `.clinerules`
- **Claude** — `.claude/` directory plus `CLAUDE.md`
- **Cursor** — `.cursor/rules/` plus `.cursorrules`
- **GitHub Copilot** — `.github/copilot-instructions.md`
- **Roo Code** — `.roomodes` custom modes plus `.roo/` rules, skills, and commands
- **JetBrains Junie** (CLI) — `.junie/` agents, skills, and commands plus `AGENTS.md`
- **Zed** — `.agents/skills/` (agents-as-skills) plus `AGENTS.md` instructions
- **Gemini CLI** — `.gemini/` agents, skills, and TOML commands plus `AGENTS.md`

## What's in the library

- **25 primary agents** (architect, backend, frontend, code, test, debug, security, devops, and more)
- **~100 workflows** in minimal and verbose variants
- **~95 specialized skills**
- **29 languages** with first-class conventions (`prompticorn/agents/core/conventions-*.md`)

## Install

```bash
pip install prompticorn
# or
uv add prompticorn
```

This installs the `prompticorn` CLI command.

## Quick Start

```bash
cd your-project
prompticorn init
```

`init` is interactive: it asks which assistant to configure, your repository
type, prompt variant, personas, language-specific settings, and a set of
project questions (database, ORM, error-handling pattern, commit style, PR-size
limit, deploy target, and source-tree layout). It then writes
`.prompticorn/.prompticorn.yaml` and generates the assistant's config files.

See [docs/QUICKSTART.md](./docs/QUICKSTART.md) for the full walkthrough.

## Key Features

- **Unified IR system** — define agents once, generate for every supported tool.
- **9 production builders** — Kilo, Cline, Claude, Cursor, Copilot, Roo Code, Junie, Zed, Gemini CLI.
- **Minimal / verbose variants** — trade tokens for detail at build time.
- **Persona-based filtering** — pick your team's roles and only relevant agents are generated.
- **Spec-driven conventions** — your language, runtime, package manager, test
  framework, linter, formatter, coverage targets, and project settings are baked
  into the generated conventions.
- **Per-language source layouts** — the core convention renders each language's
  standard source tree; `flat` is the default and `src` is selectable.
- **Auto-discovery registry** — agents are discovered from the bundled
  `agents/` tree; no manual registration.

## Commands

| Command | Description |
|---------|-------------|
| `prompticorn init` | Interactive setup: pick a tool, answer language and project questions, generate configs. |
| `prompticorn list` | List discovered agents, their subagents, and prompt variants (live agent discovery). |
| `prompticorn validate` | Check the `agents/` structure: every agent and subagent has the expected prompt files and loads cleanly. |
| `prompticorn switch [tool]` | Switch to a different assistant, removing old artifacts and regenerating from the saved config. |
| `prompticorn swap` | Change active personas and regenerate configs with the new agent set. |
| `prompticorn update` | Update saved configuration options interactively. |

## Documentation

- **[docs/QUICKSTART.md](./docs/QUICKSTART.md)** — 5-minute getting-started guide
- **[docs/INDEX.md](./docs/INDEX.md)** — documentation navigation hub
- **[docs/PERSONAS.md](./docs/PERSONAS.md)** — persona-based filtering

## Development

```bash
git clone https://github.com/snoodleboot-io/prompticorn.git
cd prompticorn

# Install in editable mode (reports version 0.0.0.dev0)
uv pip install -e .

# Run tests with coverage (target ~85%)
uv run pytest

# Mutation testing
uv run mutmut run

# Lint, format, and type-check
uv run ruff check .
uv run ruff format .
uv run pyright
```
