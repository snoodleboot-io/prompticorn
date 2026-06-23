# Advanced Configuration Guide

Comprehensive guide to the `.prompticorn/.prompticorn.yaml` schema and advanced
configuration options in prompticorn.

## Table of Contents

- [Configuration File Schema](#configuration-file-schema)
- [The `spec` Section](#the-spec-section)
- [Single-Language Projects](#single-language-projects)
- [Multi-Language Monorepos](#multi-language-monorepos)
- [The `project` Section](#the-project-section)
- [Persona Configuration](#persona-configuration)
- [Variant Selection](#variant-selection)
- [Supported AI Tools](#supported-ai-tools)
- [How Conventions Are Generated](#how-conventions-are-generated)
- [Configuration Validation](#configuration-validation)
- [Best Practices](#best-practices)

---

## Configuration File Schema

The configuration lives at `.prompticorn/.prompticorn.yaml` (the directory is
`.prompticorn/`, the file is `.prompticorn.yaml`). It is your project's single
source of truth — `init`, `switch`, `swap`, and `update` all read and write it.

> An older `.promptosaurus/` directory is automatically migrated to
> `.prompticorn/` on first run.

### Required fields

```yaml
version: "1.0"              # config schema version
repository:
  type: "single-language"   # or "multi-language-monorepo"
spec: {}                    # language/folder specification(s)
```

### Optional fields

```yaml
variant: "minimal"          # or "verbose"
active_personas: []         # list of persona IDs
ai_tool: "claude"           # last-selected tool (written by switch)
project: {}                 # language-agnostic project settings
```

### Complete schema reference

```yaml
version: string               # "1.0" (required)

repository:
  type: string                # "single-language" | "multi-language-monorepo"

spec:
  # single-language: a mapping (see "The spec Section")
  # multi-language-monorepo: a list of folder mappings

project:                      # language-agnostic settings (see "The project Section")
  layout_style: string        # "flat" (default) | "src"
  database: string            # e.g. "PostgreSQL" or "" (not specified)
  orm: string                 # e.g. "SQLAlchemy"
  error_handling: string      # e.g. "Exceptions"
  commit_style: string        # e.g. "Conventional Commits"
  pr_size: string             # e.g. "400" (soft limit, lines changed)
  deploy_target: string       # e.g. "AWS Lambda"

variant: string               # "minimal" | "verbose"
active_personas: list[string] # e.g. ["software_engineer", "qa_tester"]
ai_tool: string               # "claude" | "cline" | "cursor" | "copilot" | "kilo-ide" | "kilo-cli"
```

---

## The `spec` Section

The `spec` section captures language-specific choices. These field names match
the keys read by the convention generators
(`prompticorn/builders/convention_generator.py` and
`prompticorn/ir/loaders/core_files_loader.py`):

```yaml
spec:
  language: string            # "python", "typescript", "rust", ...
  runtime: string             # "3.12", "5.4", "1.22", ...
  package_manager: string     # "uv", "npm", "go mod", ...
  test_framework: string      # "pytest", "vitest", "go test", ...
  linter: string              # single linter, e.g. "ruff"
  linters: list[string]       # multiple linters, e.g. ["ruff", "mypy"]
  formatter: string           # e.g. "black"
  abstract_class_style: string  # "interface" (default) | "abc" | "Protocol"
  coverage:                   # coverage TARGETS as a mapping (not a single number)
    line: 80
    branch: 70
    function: 90
    statement: 85
    mutation: 80
    path: 60
```

Notes:

- `spec.coverage` is a **mapping of targets**, not a scalar. (The default
  template from `ConfigHandler.get_default_single_language_template` seeds the
  values shown above.) A bad shape is ignored rather than crashing rendering.
- Both `linter` (single) and `linters` (list) are recognised.
- `abstract_class_style` defaults to `"interface"` when omitted, so the
  language conventions' conditional blocks always render.

### Default single-language template

`prompticorn init` writes a template equivalent to:

```yaml
version: "1.0"
repository:
  type: "single-language"
  mappings: {}
spec:
  language: ""
  runtime: ""
  package_manager: ""
  test_framework: ""
  linter: ""
  linters: []
  formatter: ""
  abstract_class_style: "interface"
  coverage:
    line: 80
    branch: 70
    function: 90
    statement: 85
    mutation: 80
    path: 60
project:
  layout_style: "flat"
  database: ""
  orm: ""
  error_handling: ""
  commit_style: ""
  pr_size: ""
  deploy_target: ""
```

---

## Single-Language Projects

For projects using one primary programming language.

### Minimal configuration

```yaml
version: "1.0"
repository:
  type: "single-language"
spec:
  language: "python"
  runtime: "3.12"
  package_manager: "uv"
```

### Complete Python configuration

```yaml
version: "1.0"
repository:
  type: "single-language"
spec:
  language: "python"
  runtime: "3.12"
  package_manager: "uv"
  test_framework: "pytest"
  linters: ["ruff", "mypy"]
  formatter: "black"
  abstract_class_style: "abc"
  coverage:
    line: 90
    branch: 80
    function: 95
    statement: 90
    mutation: 80
    path: 70
variant: "minimal"
active_personas:
  - "software_engineer"
  - "qa_tester"
project:
  layout_style: "flat"
  database: "PostgreSQL"
  orm: "SQLAlchemy"
  error_handling: "Exceptions"
  commit_style: "Conventional Commits"
  pr_size: "400"
  deploy_target: "AWS Lambda"
```

### Complete TypeScript configuration

```yaml
version: "1.0"
repository:
  type: "single-language"
spec:
  language: "typescript"
  runtime: "5.4"
  package_manager: "npm"
  test_framework: "vitest"
  linters: ["eslint", "@typescript-eslint"]
  formatter: "prettier"
  abstract_class_style: "interface"
  coverage:
    line: 85
    branch: 75
    function: 90
    statement: 85
    mutation: 75
    path: 60
variant: "verbose"
active_personas:
  - "frontend_software_engineer"
  - "devops_engineer"
project:
  layout_style: "src"
  database: "PostgreSQL"
  orm: "Prisma"
  commit_style: "Conventional Commits"
  deploy_target: "Vercel"
```

### Supported languages

prompticorn ships standard conventions for **29 languages** (one
`conventions-<language>.md` per language):

```
c, clojure, cpp, csharp, dart, elixir, elm, fsharp, golang, groovy,
haskell, html, java, javascript, julia, kotlin, lua, objc, php, python,
r, ruby, rust, scala, shell, sql, swift, terraform, typescript
```

---

## Multi-Language Monorepos

For projects with multiple languages in different folders. The `spec` is a
**list** of folder mappings; the first folder's language is treated as the
primary language for the core conventions.

```yaml
version: "1.0"
repository:
  type: "multi-language-monorepo"
spec:
  - folder: "backend/api"
    type: "backend"
    subtype: "api"
    language: "python"
    runtime: "3.12"
    package_manager: "uv"
    test_framework: "pytest"

  - folder: "frontend"
    type: "frontend"
    subtype: "ui"
    language: "typescript"
    runtime: "5.4"
    package_manager: "npm"
    test_framework: "vitest"

  - folder: "shared/utils"
    type: "custom"
    subtype: "custom"
    language: "typescript"
    runtime: "5.4"
    package_manager: "npm"

variant: "minimal"
active_personas:
  - "fullstack_software_engineer"
  - "devops_engineer"
project:
  layout_style: "flat"
  database: "PostgreSQL"
```

A convention file is generated per folder language. If two folders share a
language, the later spec wins (conventions are keyed by language).

### Folder types and subtypes

Folder presets are offered interactively during `init`:

#### Backend

- `api` — REST/GraphQL API server
- `worker` — background worker / queue processor
- `library` — shared backend library
- `cli` — command-line tool

#### Frontend

- `ui` — web application (React, Vue, etc.)
- `library` — shared frontend library
- `e2e` — end-to-end tests

#### Custom

Any folder path with a language you choose; `type` and `subtype` are both
`custom`.

### Hierarchical paths

Folder paths may be nested, e.g. `services/auth/api`, `services/auth/worker`,
`services/payment/api`.

---

## The `project` Section

The `project` section captures **language-agnostic** decisions (database, ORM,
error-handling pattern, commit style, PR-size limit, deployment target, and the
source-tree layout style). These are collected during `init` and rendered into
the core conventions.

See [PROJECT_SETTINGS.md](./user-guide/PROJECT_SETTINGS.md) for full per-field
options, rendering details, and the per-language source-tree layouts (flat vs.
src) backed by `prompticorn/configurations/source_layouts.yaml`.

```yaml
project:
  layout_style: "flat"        # "flat" (default) | "src"
  database: "PostgreSQL"
  orm: "SQLAlchemy"
  error_handling: "Exceptions"
  commit_style: "Conventional Commits"
  pr_size: "400"
  deploy_target: "AWS Lambda"
```

Empty values render as `_(not specified)_` in the conventions.

---

## Persona Configuration

Personas control which agents are generated. Available personas are defined in
`prompticorn/personas/personas.yaml`; `init` and `swap` present them
interactively.

```yaml
active_personas:
  - "software_engineer"
  - "qa_tester"
  - "devops_engineer"
  - "security_engineer"
  - "architect"
  - "data_engineer"
  - "data_scientist"
  - "technical_writer"
  - "product_manager"
```

> The role-specific personas
> `backend_software_engineer`, `frontend_software_engineer`, and
> `fullstack_software_engineer` are also available; prefer these over the
> generic `software_engineer` where it fits your team.

### Universal agents

A small set of agents is **always generated** regardless of persona selection:

- `ask` — Q&A and explanations
- `debug` — debugging assistance
- `explain` — code walkthroughs and onboarding
- `plan` — planning and task breakdown
- `orchestrator` — workflow coordination

### Custom persona creation

Edit `prompticorn/personas/personas.yaml`:

```yaml
personas:
  my_custom_persona:
    display_name: "My Custom Role"
    description: "Custom role for a specific workflow"
    primary_agents:
      - "code"
      - "test"
    secondary_agents:
      - "review"
    workflows:
      - "feature"
    skills:
      - "debugging-methodology"
```

Then reference it:

```yaml
active_personas:
  - "my_custom_persona"
```

---

## Variant Selection

Choose between **minimal** (efficient) and **verbose** (detailed) agent prompts.
The variant is global — all agents use the same one.

```yaml
variant: "minimal"   # lightweight prompts, fewer tokens, lower cost
# or
variant: "verbose"   # detailed prompts with more examples and explanation
```

---

## Supported AI Tools

`init` and `switch` generate configuration for one tool at a time. The five
supported AI assistants are **Kilo, Cline, Claude, Cursor, and Copilot** (Kilo
offers both a CLI and an IDE target):

| Tool (menu) | Normalized name | Output |
|-------------|-----------------|--------|
| Kilo CLI | `kilo-cli` | `.opencode/rules/` (collapsed mode files) |
| Kilo IDE | `kilo-ide` | `.kilo/agents/` (individual agent files) |
| Claude | `claude` | `.claude/` directory (Markdown agents) + `CLAUDE.md` |
| Cline | `cline` | `.clinerules` (single concatenated file) |
| Cursor | `cursor` | `.cursor/rules/` directory + `.cursorrules` |
| Copilot | `copilot` | `.github/copilot-instructions.md` |

Switching tools removes the previous tool's generated artifacts before writing
the new ones.

```bash
prompticorn init             # interactive first-time setup
prompticorn switch claude    # regenerate for Claude using existing config
prompticorn switch cline     # switch to Cline
```

---

## How Conventions Are Generated

The generated core conventions (`.claude/conventions/core/general.md`, or the
equivalent for your tool) are produced from Jinja2 templates under
`prompticorn/agents/core/` (`system.md`, `conventions.md`, `session.md`) plus a
per-language `conventions-<language>.md`.

Two code paths render them:

- `prompticorn/builders/convention_generator.py` —
  `generate_core_convention()` and `generate_language_convention()`.
- `prompticorn/ir/loaders/core_files_loader.py` —
  `CoreFilesLoader.get_core_files()` / `_template_content()`.

They substitute your actual choices into the templates, including:

- `spec` values: `language`, `runtime`, `package_manager`, `test_framework`,
  `linter`/`linters`, `formatter`, `abstract_class_style`, and the `coverage`
  targets (exposed to the coverage macros).
- `project` values: `database`, `orm`, `error_handling`, `commit_style`,
  `pr_size`, `deploy_target`.
- `repository.type` (as `repository_type`).
- `source_layout` — the per-language standard source-tree layout, chosen by
  `project.layout_style` (`flat` default, `src` selectable) via
  `get_source_layout()` in `prompticorn/source_layouts.py`, with data from
  `prompticorn/configurations/source_layouts.yaml`.

Empty values render as `_(not specified)_`, so the conventions always read
cleanly even before everything is decided.

---

## Configuration Validation

`validate` checks the **agent registry structure** (discovered from the bundled
`agents/` directory), not a flat `prompts/` layout. It verifies that each agent
has a base `prompt.md` (or minimal/verbose variants), that each subagent has
`minimal/` and `verbose/` variant directories with `prompt.md`, and that all
discovered agents load cleanly.

```bash
prompticorn validate
```

Output on success:

```
▶ Validating agent registry...

  ✓ Registry valid: N agents, M subagents.
```

To list discovered agents, their subagents, and variants:

```bash
prompticorn list
```

To sanity-check your YAML syntax independently:

```bash
python -c "import yaml; yaml.safe_load(open('.prompticorn/.prompticorn.yaml'))"
```

---

## Best Practices

### Commit the config, ignore the generated artifacts

Commit `.prompticorn/.prompticorn.yaml` so the whole team shares the same
configuration:

```bash
git add .prompticorn/.prompticorn.yaml
git commit -m "Add prompticorn config"
```

Ignore the per-tool generated files:

```gitignore
.kilo/
.opencode/
.clinerules
.cursor/
.cursorrules
.github/copilot-instructions.md
```

### Start minimal, expand later

Begin with `language`, `runtime`, and `package_manager`, then fill in the rest
of `spec` and `project` as your team standardises.

### Keep personas focused

Select only the personas your team actually uses — every persona expands the set
of generated agents.

### Regenerate after edits

After editing `.prompticorn/.prompticorn.yaml`, regenerate so the rendered
conventions and agents pick up the change:

```bash
prompticorn switch <tool>   # or: prompticorn init
```

---

## Reference

- [PROJECT_SETTINGS.md](./user-guide/PROJECT_SETTINGS.md) — the `project`
  section and source-tree layouts in depth.
- [GETTING_STARTED.md](./user-guide/GETTING_STARTED.md) — first-run walkthrough.

---

**Last Updated:** 2026-06-22

> Version: prompticorn uses a **dynamic** version. `pyproject.toml` declares
> `dynamic = ["version"]` sourced from `prompticorn/__about__.py`; CI/CD injects
> the real `MAJOR.MINOR.PATCH` at build time. Local/editable installs report
> `0.0.0.dev0`.
