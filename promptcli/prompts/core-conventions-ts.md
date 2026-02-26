# TypeScript Conventions

Language:             {{LANGUAGE}}           e.g., TypeScript 5.x
Runtime:              {{RUNTIME}}            e.g., Node 20, Deno, Bun
Package Manager:      {{PKG_MANAGER}}        e.g., npm, pnpm, yarn
Linter:               {{LINTER}}             e.g., ESLint
Formatter:           {{FORMATTER}}          e.g., Prettier

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
Framework:            {{TEST_FRAMEWORK}}     e.g., Vitest, Jest
Coverage target:      {{COVERAGE_%}}         e.g., 80%
Mocking library:     {{MOCK_LIB}}           e.g., vitest/mock, jest.mock

- Use `describe`/`it` blocks with descriptive names
- Mock at the boundary (dependencies), not internals
- Test behavior, not implementation
- Unit tests: one function or method in isolation
- Integration tests: at the service or module boundary

### Code Style
- Use ESNext features (optional chaining, nullish coalescing)
- Prefer immutable patterns — use `readonly` for arrays/objects
- Use `enum` sparingly — prefer const objects or unions
