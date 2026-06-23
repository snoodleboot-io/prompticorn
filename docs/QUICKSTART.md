# Quick Start Guide

Get up and running with prompticorn in about 5 minutes.

## What is prompticorn?

prompticorn turns one shared prompt library into ready-to-use configuration for
your AI coding assistant. The library ships with:

- **25 primary agents** spanning architecture, backend, frontend, code, test,
  debug, security, devops, and more
- **~100 workflows** for common development tasks, in minimal and verbose variants
- **~95 specialized skills**
- **29 languages** with first-class conventions

It generates configs for 5 assistants: **Kilo** (IDE and CLI), **Cline**,
**Claude**, **Cursor**, and **GitHub Copilot**.

## Install

```bash
pip install prompticorn
# or
uv add prompticorn
```

This installs the `prompticorn` CLI command. (Editable installs report version
`0.0.0.dev0`; published builds carry a real version injected by CI/CD.)

## Initialize your project

From your project root, run:

```bash
prompticorn init
```

`init` is fully interactive. Use the arrow keys or numbers to choose; press
Enter to accept the highlighted default. The flow is:

1. **AI assistant** — pick the assistant to configure:
   Kilo CLI, Kilo IDE, Claude, Cline, Cursor, or Copilot.
2. **Repository type** — single-language project or multi-language monorepo.
   For a monorepo you add folders (backend/frontend presets or custom paths),
   each with its own language and language questions.
3. **Prompt variant** — *Minimal* (leaner, cheaper tokens) or *Verbose*
   (more examples and explanation).
4. **Personas** — choose one or more roles (software engineer, QA, devops, etc.).
   Only agents and workflows relevant to the selected personas are generated;
   universal agents (ask, debug, explain, plan, orchestrator) are always included.
5. **Language questions** — for each language, you answer settings like runtime
   version, package manager, test framework, linter, formatter, coverage target,
   and abstract-class style.
6. **Project questions** — language-agnostic settings asked once and baked into
   the core conventions, in this order:
   - **Source-tree layout** — `flat` (package/modules at the repo root, the
     default) or `src` (sources under a `src/` directory). The matching standard
     layout for your primary language is rendered into the conventions.
   - **Database** — PostgreSQL, MySQL, SQLite, MongoDB, DynamoDB, Redis, or none.
   - **ORM / query layer** — SQLAlchemy, Prisma, Django ORM, GORM, TypeORM, raw SQL, or none.
   - **Error-handling pattern** — exceptions, result type, or error values/codes.
   - **Commit style** — Conventional Commits or free-form.
   - **PR-size limit** — a soft cap (200 / 400 / 800 lines) agents aim to stay under.
   - **Deploy target** — AWS Lambda, AWS ECS, Kubernetes, GKE, Vercel, Heroku, and more.

   Any question can be left as *Not specified*.

When you finish, `init`:

- writes your configuration to `.prompticorn/.prompticorn.yaml`,
- removes stale artifacts if you switched away from a previously configured tool, and
- generates the selected assistant's config files (for example `.claude/` and
  `CLAUDE.md` for Claude, or `.cursor/rules/` and `.cursorrules` for Cursor).

The generated conventions reflect your actual spec choices — language, runtime,
package manager, test framework, linter, formatter, coverage targets, and the
project settings above.

## Verify and explore

```bash
# List discovered agents, subagents, and prompt variants
prompticorn list

# Validate the agents/ structure (every agent/subagent has its prompt files)
prompticorn validate
```

Both commands use live agent discovery over the bundled `agents/` tree.

## Change your setup later

You do not need to re-run the full `init` to adjust things:

```bash
# Switch to a different assistant (regenerates from the saved config)
prompticorn switch cursor

# Change active personas and regenerate with the new agent set
prompticorn swap

# Update individual configuration options interactively
prompticorn update
```

## Key concepts

- **Agents** — instructions for specialized assistants (backend developer,
  devops engineer, test writer, etc.), each with a clear purpose.
- **Workflows** — step-by-step guides for tasks (debugging, refactoring,
  performance work). Available in minimal and verbose variants.
- **Skills** — focused expertise on narrow topics that agents draw on.
- **Personas** — team roles that filter which agents and workflows are generated.
- **Conventions** — per-language and project-level rules rendered into your tool's
  config from your `init` answers.

## What's next?

- Read [INDEX.md](./INDEX.md) to navigate the rest of the documentation.
- Read [PERSONAS.md](./PERSONAS.md) to fine-tune which agents your team gets.
- Open one generated agent file to see the style before adopting it broadly.
