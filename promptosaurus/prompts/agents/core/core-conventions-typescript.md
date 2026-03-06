<!-- path: promptosaurus/prompts/agents/core/core-conventions-typescript.md -->
# Core Conventions TypeScript

Language:             {{LANGUAGE}}           e.g., TypeScript 5.x
Runtime:              {{RUNTIME}}            e.g., Node 20, Deno, Bun
Package Manager:      {{PACKAGE_MANAGER}}        e.g., npm, pnpm, yarn
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

#### Coverage Targets
Line:           {{LINE_COVERAGE_%}}          e.g., 80%
Branch:         {{BRANCH_COVERAGE_%}}        e.g., 70%
Function:       {{FUNCTION_COVERAGE_%}}       e.g., 90%
Statement:      {{STATEMENT_COVERAGE_%}}      e.g., 85%
Mutation:       {{MUTATION_COVERAGE_%}}       e.g., 80%
Path:           {{PATH_COVERAGE_%}}           e.g., 60%

#### Test Types

##### Unit Tests
- One function or method in isolation
- Mock external dependencies (APIs, filesystem, database)
- Use `describe`/`it` blocks with descriptive names
- Test behavior, not implementation

##### Integration Tests
- Test at service or module boundary
- Use real services or in-memory alternatives (msw, testcontainers)
- Test API endpoints, database queries, file operations

##### E2E Tests
- Use Playwright or Cypress for browser testing
- Test critical user flows end-to-end

##### Mutation Tests
- Use `stryker-mutator` to verify test quality
- Run after unit tests pass

##### Component Tests
- Use Testing Library (@testing-library/react, @testing-library/vue)
- Test component rendering and user interactions

#### Framework & Tools
Framework:       {{TESTING_FRAMEWORK}}        e.g., Vitest, Jest
Mocking library: {{MOCKING_LIBRARY}}              e.g., vitest/mock, jest.mock
Coverage tool:  {{COVERAGE_TOOL}}              e.g., Vitest coverage, Jest coverage
E2E tool:       {{E2E_TOOL}}             e.g., Playwright, Cypress
Mutation tool:  {{MUTATION_TOOL}}          e.g., stryker-mutator

#### Scaffolding

```bash
# Install (using pnpm)
pnpm add -D vitest @vitest/coverage-v8 @testing-library/react jest-mock-extended

# Run tests
vitest run                    # Run all tests
vitest run --coverage         # With coverage
vitest run --coverage.branch  # Line + branch

# Configuration (vitest.config.ts)
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      branches: true,
      functions: true,
      lines: true,
      statements: true,
    },
  },
})
```

##### CI Integration
```yaml
# GitHub Actions example
- name: Run tests
  run: pnpm vitest run --coverage

- name: Mutation tests
  run: |
    pnpm add -D @stryker-mutator/core
    npx stryker run
```

### Code Style
- Use ESNext features (optional chaining, nullish coalescing)
- Prefer immutable patterns — use `readonly` for arrays/objects
- Use `enum` sparingly — prefer const objects or unions
