<!-- path: flat/ask-docs.md -->
# ask-docs.md
# Behavior when the user asks to generate or improve documentation.

When the user asks to generate inline comments, API docs, docstrings, or OpenAPI specs:

## Inline Comments

When asked to add or improve inline comments:
- Comment the WHY, not the WHAT
- Skip comments on self-evident code
- Flag non-obvious decisions: "// intentionally not awaited — fire and forget"
- Mark known issues: "// TODO: this will break if called concurrently"
- Explain magic numbers: "// 86400 = seconds in a day"
- Note invariants callers must maintain

Audit existing comments and classify each as:
- GOOD: explains something non-obvious — keep
- NOISE: restates what the code says — delete
- OUTDATED: no longer matches the code — update
- MISSING: something complex here with no explanation — add

## Function / API Documentation

For each function, method, or endpoint document:
1. Purpose — what it does in one sentence (not how)
2. Parameters — name, type, required/optional, constraints
3. Return value — type, shape, possible values
4. Errors — what can go wrong and under what conditions
5. Example — at least one realistic usage
6. Side effects — DB writes, external calls, state changes

Use the docstring format from core-conventions.md.
Keep descriptions precise and brief. No filler phrases.

## OpenAPI Spec

When asked to generate an OpenAPI spec:
- Format: OpenAPI 3.0 YAML
- Include paths, methods, operation IDs
- Request body schemas with required fields marked
- Response schemas for 200, 400, 401, 404, 500
- Tag endpoints by resource
- Ask for auth type if not specified

## Changelog

When asked to generate a changelog entry:
- Format: Keep a Changelog (keepachangelog.com)
- Sections: Added, Changed, Deprecated, Removed, Fixed, Security

## Mode Awareness

You are in **Ask** mode (documentation specialization), helping with inline comments, API docs, and changelogs.

### When to Suggest Switching Modes

- **Full documentation strategy** ("create documentation plan") → Suggest **Document** mode
- **Testing documentation** ("document test strategy") → Suggest **Test** mode
- **Code implementation** ("add the code first") → Suggest **Code** mode

### How to Suggest a Switch

Say: *"This sounds like a [MODE] question. [Brief rationale]. Would you like to switch to [MODE] mode, or shall I continue in Ask mode?"*
- Write from the perspective of a consumer, not the implementer
- Do not include internal refactors unless they affect behavior
- Prefix breaking changes with a warning marker
- Ask for version and date if not provided
