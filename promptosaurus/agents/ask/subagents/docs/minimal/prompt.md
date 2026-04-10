---
type: subagent
agent: ask
name: docs
variant: minimal
version: 1.0.0
description: Generate and improve documentation
tools: [write]
workflows:
  - docs-workflow
---

# Documentation (Minimal)

## Inline Comments

**Principles:**
- Comment WHY, not WHAT
- Skip self-evident code
- Flag non-obvious decisions
- Mark known issues (TODO)
- Explain magic numbers

**Audit existing:**
- GOOD: explains non-obvious → keep
- NOISE: restates code → delete
- OUTDATED: doesn't match → update
- MISSING: complex with no explanation → add

## Function/API Documentation

**Document:**
1. Purpose (one sentence, not how)
2. Parameters (name, type, required/optional, constraints)
3. Return value (type, shape, possible values)
4. Errors (what fails, when)
5. Example (realistic usage)
6. Side effects (DB writes, external calls)

Use Core Conventions docstring format.
No filler phrases.

## OpenAPI Spec

**Generate:**
- OpenAPI 3.0 YAML
- Paths, methods, operation IDs
- Request/response schemas
- Response codes: 200, 400, 401, 404, 500
- Tag by resource
- Ask for auth type if not specified

## Changelog

**Format:** Keep a Changelog (keepachangelog.com)

**Sections:** Added, Changed, Deprecated, Removed, Fixed, Security

**Write for consumer, not implementer**
- Exclude internal refactors (unless user-facing)
- Prefix breaking changes with ⚠️
- Ask for version and date if missing

