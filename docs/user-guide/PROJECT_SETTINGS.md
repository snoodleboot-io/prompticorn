# Project Settings

The `project` section of `.prompticorn/.prompticorn.yaml` captures
**language-agnostic** decisions about your codebase — the database, the ORM, the
error-handling pattern, the commit style, a soft PR-size limit, the deployment
target, and the source-tree layout style.

These settings are collected once during `prompticorn init` (after the language
questions) and are rendered directly into the generated **core conventions**
(`Core Conventions` / `.claude/conventions/core/general.md`) so every agent shares
the same project context.

> Defaults are intentionally empty (`""`). An empty value renders as the
> placeholder `_(not specified)_` in the conventions, signalling that the team
> has not standardised on a choice yet.

---

## The `project` section

```yaml
project:
  layout_style: "flat"        # "flat" (default) | "src"
  database: "PostgreSQL"      # or "" (not specified)
  orm: "SQLAlchemy"
  error_handling: "Exceptions"
  commit_style: "Conventional Commits"
  pr_size: "400"              # soft limit, lines changed
  deploy_target: "AWS Lambda"
```

Every field is optional. The default `project` block written by `init` is:

```yaml
project:
  layout_style: "flat"
  database: ""
  orm: ""
  error_handling: ""
  commit_style: ""
  pr_size: ""
  deploy_target: ""
```

(Source: `ConfigHandler.get_default_project_settings`.)

---

## Fields, options, and how they render

The `init` questions live in
`prompticorn/questions/project/project_questions.py`. They are asked in this
order. Selecting **"Not specified"** stores an empty string, which renders as
`_(not specified)_`.

### `layout_style`

- **Question:** "Which source-tree layout should the conventions document?"
- **Options:** `flat` (default), `src`
- **Effect:** Selects which per-language source-tree layout is rendered into the
  core conventions' **File & Folder Structure** section. `flat` puts the
  package/modules at the repository root; `src` nests sources under a `src/`
  directory. See [Source-tree layouts](#source-tree-layouts) below.
- **Note:** Unlike the other project fields, `layout_style` has no
  "Not specified" option — it always resolves to `flat` or `src`.

### `database`

- **Question:** "Which database does this project use?"
- **Options:** Not specified, PostgreSQL, MySQL, SQLite, MongoDB, DynamoDB, Redis
- **Renders into:** the **Database** section of the core conventions:
  ```
  Database:            PostgreSQL           e.g., PostgreSQL, DynamoDB
  ```

### `orm`

- **Question:** "Which ORM / query layer does this project use?"
- **Options:** Not specified, SQLAlchemy, Prisma, Django ORM, GORM, TypeORM, Raw SQL
- **Renders into:** the **Database** section:
  ```
  ORM/Query:           SQLAlchemy                e.g., Prisma, SQLAlchemy, GORM
  ```

### `error_handling`

- **Question:** "What error-handling pattern does this project follow?"
- **Options:** Not specified, Exceptions, Result type, Error values / codes
- **Renders into:** the **Error Handling** section:
  ```
  Pattern: Exceptions
  ```

### `commit_style`

- **Question:** "Which commit message style does this project follow?"
- **Options:** Not specified, Conventional Commits, Free-form
- **Renders into:** the **Git & PR Conventions** section:
  ```
  Commit style:        Conventional Commits  e.g., Conventional Commits, free-form
  ```

### `pr_size`

- **Question:** "What soft PR size limit (lines changed) should agents target?"
- **Options:** Not specified, 200, 400, 800
- **Renders into:** the **Git & PR Conventions** section:
  ```
  PR size:             400 lines changed (soft limit)
  ```

### `deploy_target`

- **Question:** "What is the primary deployment target?"
- **Options:** Not specified, AWS Lambda, AWS ECS, Kubernetes, GKE, Vercel,
  Heroku, On-prem
- **Renders into:** the **Deployment** section:
  ```
  Target:              AWS Lambda  e.g., AWS Lambda, Vercel, GKE
  ```

---

## How the project section reaches the conventions

The core convention template (`prompticorn/agents/core/conventions.md`) contains
Jinja2 placeholders for each project field, e.g.:

```jinja
Pattern: {{ error_handling or "_(not specified)_" }}
...
Database:            {{ database or "_(not specified)_" }}
ORM/Query:           {{ orm or "_(not specified)_" }}
...
Commit style:        {{ commit_style or "_(not specified)_" }}
PR size:             {{ pr_size or "_(not specified)_" }} lines changed (soft limit)
...
Target:              {{ deploy_target or "_(not specified)_" }}
```

Two code paths render these placeholders:

- `prompticorn/builders/convention_generator.py` —
  `generate_core_convention()` builds the render context from the `project`
  dict for the keys `database`, `orm`, `error_handling`, `commit_style`,
  `pr_size`, `deploy_target`, plus `repository_type` and the resolved
  `source_layout`.
- `prompticorn/ir/loaders/core_files_loader.py` —
  `CoreFilesLoader._template_content()` builds the same context from
  `config["project"]` when loading core files for an agent.

Both call `get_source_layout(primary_language, project.layout_style)` (from
`prompticorn/source_layouts.py`) to pick the `source_layout` block.

---

## Source-tree layouts

The core conventions' **File & Folder Structure** section is filled with the
**standard source-tree layout for your primary language**, chosen by
`layout_style`.

- **Data source:** `prompticorn/configurations/source_layouts.yaml`
- **Logic:** `prompticorn/source_layouts.py` (`get_source_layout`)
- **Default style:** `flat` (`DEFAULT_STYLE = "flat"`)

### Flat vs. src

Each entry in `source_layouts.yaml` is either:

1. A **mapping** with both `flat` and `src` keys — used when both layouts are
   idiomatic for the ecosystem, or
2. A **single string** — used when the ecosystem dictates one canonical layout
   (the chosen `layout_style` is then ignored).

Languages with both `flat` and `src` variants:

| Key | `flat` | `src` |
|-----|--------|-------|
| `default` (fallback) | ✓ | ✓ |
| `python` | ✓ | ✓ |
| `typescript` | ✓ | ✓ |
| `javascript` | ✓ | ✓ |

All other languages provide a single canonical layout (see the full list below).

### Resolution rules

`get_source_layout(language, style)` resolves as follows:

1. Look up the language entry (case-insensitive). If `language` is `None` or
   absent from the registry, fall back to the `default` entry.
2. If there is no entry at all, return the hard-coded fallback `src/\ntests/`.
3. Within the entry, prefer the requested `style`, then `flat`, then whatever
   single layout exists.

So requesting `src` for, say, Go (which only defines one canonical layout)
simply returns that canonical Go layout.

### Languages covered

`source_layouts.yaml` contains a `default` fallback plus standard layouts for
**all 29 languages** that have convention files (`conventions-*.md`):

```
c, clojure, cpp, csharp, dart, elixir, elm, fsharp, golang, groovy,
haskell, html, java, javascript, julia, kotlin, lua, objc, php, python,
r, ruby, rust, scala, shell, sql, swift, terraform, typescript
```

A language not present in `source_layouts.yaml` falls back to the `default`
entry's layout for the chosen style.

### Examples

**Python, `flat` (default):**

```
<your_package>/          # importable package at repo root (flat layout, default)
├── __init__.py
├── domain/              # entities, value objects, domain logic
├── services/            # application / business logic
├── adapters/            # external IO (db, http, filesystem)
└── settings.py          # pydantic-settings configuration
tests/
├── unit/
└── integration/
pyproject.toml
```

**Python, `src`:**

```
src/
└── <your_package>/
    ├── __init__.py
    ├── domain/          # entities, value objects, domain logic
    ├── services/        # application / business logic
    ├── adapters/        # external IO (db, http, filesystem)
    └── settings.py      # pydantic-settings configuration
tests/
├── unit/
└── integration/
pyproject.toml
```

**Go (single canonical layout — `layout_style` ignored):**

```
cmd/
└── <app>/main.go        # binary entrypoints
internal/                # private application code
pkg/                     # public, importable libraries
<package>_test.go        # tests co-located with source
```

---

## Updating project settings

- Re-run `prompticorn init` to walk the full questionnaire again, or
- Edit `.prompticorn/.prompticorn.yaml` directly and regenerate your tool's
  configuration (`prompticorn switch <tool>` or `prompticorn init`).

After any change, regenerate so the rendered core conventions pick up the new
values.

---

## Related documentation

- [ADVANCED_CONFIGURATION.md](../ADVANCED_CONFIGURATION.md) — full
  `.prompticorn.yaml` schema, including the `spec` section and personas.
- [GETTING_STARTED.md](./GETTING_STARTED.md) — first-run walkthrough.
