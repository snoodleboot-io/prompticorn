<!-- path: promptosaurus/prompts/agents/core/core-conventions-typescript.md -->
{%- import 'macros/testing_sections.jinja2' as testing -%}
{%- import 'macros/coverage_targets.jinja2' as coverage -%}
# Core Conventions TypeScript

Language:             {{ language }} e.g., TypeScript 5.x
Runtime:              {{ runtime }} e.g., Node 20, Deno, Bun
Package Manager:      {{ package_manager }} e.g., npm, pnpm, yarn
Linter:               {{ linter }} e.g., ESLint
Formatter:           {{ formatter }} e.g., Prettier

### Naming Conventions

Files:               kebab-case
Variables:          camelCase
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          camelCase
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## TypeScript-Specific Rules

### Type System
- strict mode always on in tsconfig.json
- No `any` — use `unknown` + type narrowing
- Prefer `interface` for object shapes, `type` for unions/intersections
- Always type function return values explicitly
- Use `const` assertions (`as const`) for literal types

### Error Handling
- Use typed error unions: `function foo(): Result<T, FooError | BarError>`
- Never use `throw` in library code — return errors instead
- Use `never` for functions that don't return

### Imports & Exports
- Use path aliases (`@/`) configured in tsconfig.json
- Prefer named exports over default exports
- Use barrel files (index.ts) for clean public APIs
- Order imports: external → internal → types (with blank lines between)

### Testing

[Dynamic content - see template]

TODO

[Dynamic content - see template]

[Dynamic content - see template]

### Code Style
- Use ESNext features (optional chaining, nullish coalescing)
- Prefer immutable patterns — use `readonly` for arrays/objects
- Use `enum` sparingly — prefer const objects or unions
