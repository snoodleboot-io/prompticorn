# PRD: Core vs Fungible Language Configuration

## Problem Statement

Currently, when setting up a multi-language monorepo, promptosaurus asks all language questions for each folder, regardless of whether the answer should be the same across the entire repo or can differ per folder/workspace.

This leads to unnecessary repetition when:
- Multiple folders use the same language (e.g., Python)
- Some configurations are inherently the same (e.g., linter, formatter)
- But other configurations can legitimately differ (e.g., framework: fastapi vs flask)

## Goals

1. **Distinguish core vs fungible questions**: Core = same across repo, Fungible = can differ per folder
2. **Ask core questions ONCE per language**: Reduce redundancy
3. **Ask fungible questions for EACH folder**: Enable customization per workspace - THIS IS CRITICAL
4. **Make framework questions CONTEXT-AWARE**: Based on folder type (api, library, worker, cli, ui, e2e)

---

## Folder Type Definitions

### Backend Types:
- **api**: REST/gRPC API server
- **library**: Reusable library/package
- **worker**: Background worker/task queue
- **cli**: Command-line tool

### Frontend Types:
- **ui**: Web/mobile UI application
- **library**: Reusable UI component library
- **e2e**: End-to-end test suite

---

## Fungible Questions by Language + Folder Type

The key insight is that framework questions are CONTEXT-AWARE based on folder type:

### TypeScript / JavaScript

| Folder Type | Fungible Questions |
|-------------|------------------|
| frontend/ui | **Framework**: react, vue, svelte, next.js, angular, remix, nuxt |
| frontend/e2e | **Test Framework**: playwright, cypress |
| frontend/library | (none) |
| backend/api | **Framework**: express, fastify, nestjs, hono, koa |
| backend/worker | (none - same as api) |
| backend/library | (none) |
| backend/cli | (none) |

### Python

| Folder Type | Fungible Questions |
|-------------|------------------|
| frontend/ui | **Framework**: dash, streamlit, reflex, nicegui, shiny |
| frontend/e2e | **Test Framework**: playwright, cypress |
| frontend/library | (none) |
| backend/api | **Framework**: fastapi, flask, django, starlette |
| backend/worker | **Task Queue**: celery, huey, dramatiq,rq |
| backend/library | (none) |
| backend/cli | (none) |

### Go

| Folder Type | Fungible Questions |
|-------------|------------------|
| frontend/* | (Go not used for frontend) |
| backend/api | **Framework**: gin, echo, fiber, chi, iris |
| backend/worker | (none - stdlib sufficient) |
| backend/library | (none) |
| backend/cli | **CLI Framework**: cobra, urfave/cli, click (bubbletea for TUI) |

### Rust

| Folder Type | Fungible Questions |
|-------------|------------------|
| frontend/* | (Rust not typically used for frontend) |
| backend/api | **Web Framework**: axum, actix, rocket, warp |
| backend/worker | (none) |
| backend/library | (none) |
| backend/cli | **CLI Framework**: clap, structopt |

### Java

| Folder Type | Fungible Questions |
|-------------|------------------|
| frontend/* | (Java not used for frontend) |
| backend/api | **Framework**: spring-boot, quarkus, micronaut, jakartaee |
| backend/worker | (same as api) |
| backend/library | (none) |
| backend/cli | (none - use spring shell) |

### C#

| Folder Type | Fungible Questions |
|-------------|------------------|
| frontend/* | (Blazor rare) |
| backend/api | **Framework**: aspnet-core, minimal-api |
| backend/worker | (same as api) |
| backend/library | (none) |
| backend/cli | (none) |

### Ruby

| Folder Type | Fungible Questions |
|-------------|------------------|
| frontend/* | (Rails handles both) |
| backend/api | **Framework**: rails, sinatra, grape, rodakase |
| backend/worker | **Task Queue**: sidekiq, resque, delayed-job |
| backend/library | (none) |
| backend/cli | (none) |

### PHP

| Folder Type | Fungible Questions |
|-------------|------------------|
| frontend/* | (PHP not used for frontend) |
| backend/api | **Framework**: laravel, symfony, slim, lumen, flight |
| backend/worker | (same as api + supervisor) |
| backend/library | (none) |
| backend/cli | (none) |

### Kotlin

| Folder Type | Fungible Questions |
|-------------|------------------|
| frontend/* | (Kotlin/JS rare) |
| backend/api | **Framework**: ktor, spring-boot, javalin |
| backend/worker | (same as api) |
| backend/library | (none) |
| backend/cli | (none) |

### Scala

| Folder Type | Fungible Questions |
|-------------|------------------|
| frontend/* | (Scala.js rare) |
| backend/api | **Framework**: play, akka-http, http4s, finatra |
| backend/worker | (same as api) |
| backend/library | (none) |
| backend/cli | (none) |

### Swift

| Folder Type | Fungible Questions |
|-------------|------------------|
| frontend/* | (SwiftUI for Apple only) |
| backend/api | **Framework**: vapor, hummingbird (note: Kitura deprecated) |
| backend/worker | (none) |
| backend/library | (none) |
| backend/cli | (none - native) |

### Ruby, PHP, etc. - similar patterns

---

## Languages With NO Fungible Questions

These languages don't have framework-like concepts - they're either:
- Infrastructure/scripting: shell, terraform, sql
- Academic/statistical: r, julia
- Niche: lua, dart, elm, elixir, clojure, fsharp, groovy, haskell

For these, ALL questions are core (same across repo).

---

## Implementation Approach

### 1. Update question_pipelines.yaml

Structure by language with core/fungible sections:
```yaml
python:
  core:
    - PythonRuntimeQuestion
    - PythonPackageManagerQuestion
    # ... all core questions
  fungible:
    backend/api:
      - PythonFrameworkQuestion  # fastapi, flask, django
    backend/worker:
      - PythonWorkerFrameworkQuestion  # celery, huey
    frontend/ui:
      - PythonUIFrameworkQuestion  # dash, streamlit
    frontend/e2e:
      - PythonE2ETestFrameworkQuestion  # playwright, cypress

typescript:
  core:
    - TypeScriptVersionQuestion
    - TypeScriptPackageManagerQuestion
  fungible:
    frontend/ui:
      - TypeScriptFrameworkQuestion  # react, vue, next.js
    frontend/e2e:
      - TypeScriptE2ETestFrameworkQuestion  # playwright, cypress
    backend/api:
      - TypeScriptBackendFrameworkQuestion  # express, nestjs
```

### 2. Context-Aware Question Factory

The system needs to know:
1. The folder type (api, library, worker, cli, ui, e2e)
2. The language (python, typescript, etc.)
3. Return the appropriate fungible questions

### 3. Config Storage

```yaml
repository: multi-language-monorepo

# Core config - shared per language
languages:
  python:
    runtime: "3.12"
    package_manager: uv
    linter: ruff
    formatter: ruff
    test_framework: pytest

# Fungible config - specific to each folder
folders:
  - folder: backend/api
    type: backend
    subtype: api
    language: python
    fungible:
      framework: fastapi
  - folder: backend/worker
    type: backend
    subtype: worker
    language: python
    fungible:
      task_queue: celery
  - folder: frontend/ui
    type: frontend
    subtype: ui
    language: python
    fungible:
      framework: dash
```

## Summary Table

| Language | Has Fungible? | Which Folders |
|----------|--------------|---------------|
| TypeScript/JavaScript | Yes | frontend/ui, frontend/e2e, backend/api |
| Python | Yes | frontend/ui, frontend/e2e, backend/api, backend/worker |
| Go | Yes | backend/api, backend/cli |
| Rust | Yes | backend/api, backend/cli |
| Java | Yes | backend/api |
| C# | Yes | backend/api |
| Ruby | Yes | backend/api, backend/worker |
| PHP | Yes | backend/api |
| Kotlin | Yes | backend/api |
| Scala | Yes | backend/api |
| Swift | Yes | backend/api |
| Shell | No | N/A |
| SQL | No | N/A |
| Terraform | No | N/A |
| R, Julia | No | N/A |
| Dart, Elm, Elixir, etc. | No | N/A |

## Success Metrics

- [ ] Core questions asked only once per language
- [ ] Fungible questions asked for EACH folder with context-aware options
- [ ] Config properly stores both core and fungible settings
- [ ] Builders correctly use core + fungible config per folder
