<!-- path: promptosaurus/prompts/agents/core/core-conventions-typescript.md -->
{%- import 'macros/testing_sections.jinja2' as testing -%}
{%- import 'macros/coverage_targets.jinja2' as coverage -%}
# Core Conventions TypeScript

Language:             {{config.language | default('typescript')}}           e.g., TypeScript 5.x
Runtime:              {{config.runtime | default('Node 20')}}            e.g., Node 20, Deno, Bun
Package Manager:      {{config.package_manager | default('pnpm')}}        e.g., npm, pnpm, yarn
Linter:               {{config.linter | default('eslint')}}             e.g., ESLint
Formatter:           {{config.formatter | default('prettier')}}          e.g., Prettier

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

{{ testing.render_test_types('typescript') }}

{{ coverage.render_coverage_table(
  line=config.coverage.line | default('90'),
  branch=config.coverage.branch | default('80'),
  function=config.coverage.function | default('95'),
  statement=config.coverage.statement | default('90'),
  mutation=config.coverage.mutation | default('85'),
  path=config.coverage.path | default('70')
) }}

{{ testing.render_test_scaffolding('typescript', 'pnpm') }}

{{ testing.render_ci_integration('typescript') }}

### Code Style
- Use ESNext features (optional chaining, nullish coalescing)
- Prefer immutable patterns — use `readonly` for arrays/objects
- Use `enum` sparingly — prefer const objects or unions
