<!-- path: promptosaurus/prompts/agents/core/core-conventions-javascript.md -->
# Core Conventions JavaScript

Language:             {{LANGUAGE}}           e.g., JavaScript ES2024
Runtime:              {{RUNTIME}}            e.g., Node.js 20, Deno, Bun
Package Manager:      {{PACKAGE_MANAGER}}        e.g., npm, pnpm, yarn
Linter:               {{LINTER}}             e.g., ESLint
Formatter:           {{FORMATTER}}          e.g., Prettier

### Naming Conventions

Files:               kebab-case
Variables:          camelCase
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          camelCase
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## JavaScript-Specific Rules

### Type System
- Use JSDoc for type annotations when not using TypeScript
- Prefer `const` over `let`, never use `var`
- Enable strict mode in all files (`"use strict";`)

### Error Handling
- Use Error objects with stack traces
- Never swallow errors silently
- Use async/await with proper try/catch

### Imports & Exports
- Use ES modules (import/export), not CommonJS
- Use path aliases configured in package.json
- Prefer named exports over default exports
- Order imports: external → internal → relative (blank lines between)

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
- One function or module in isolation
- Mock external dependencies (APIs, filesystem)
- Use `describe`/`it` blocks with descriptive names

##### Integration Tests
- Test at module boundary
- Use real services or mocks for external systems

##### E2E Tests
- Use Playwright or Cypress for browser testing

##### Mutation Tests
- Use `stryker-mutator` for JavaScript

#### Framework & Tools
Framework:       {{TESTING_FRAMEWORK}}        e.g., Jest, Vitest, Mocha
Mocking library: {{MOCKING_LIBRARY}}              e.g., jest-mock, sinon
Coverage tool:  {{COVERAGE_TOOL}}              e.g., Jest coverage, c8
E2E tool:       {{E2E_TOOL}}             e.g., Playwright, Cypress

#### Scaffolding

```bash
# Install
npm install --save-dev jest @types/jest jest-mock-extended

# Run tests
jest                           # Run tests
jest --coverage                # With coverage

# Configuration (jest.config.js)
module.exports = {
  testEnvironment: 'node',
  collectCoverage: true,
  coverageProvider: 'v8',
}
```
