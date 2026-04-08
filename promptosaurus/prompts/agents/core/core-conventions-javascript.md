<!-- path: promptosaurus/prompts/agents/core/core-conventions-javascript.md -->
# Core Conventions JavaScript

Language:             {{config.language | default('javascript')}}           e.g., JavaScript ES2024
Runtime:              {{config.runtime | default('Node.js 20')}}            e.g., Node.js 20, Deno, Bun
Package Manager:      {{config.package_manager | default('npm')}}        e.g., npm, pnpm, yarn
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
Line:           {{config.coverage.line}}          e.g., 80%
Branch:         {{config.coverage.branch}}        e.g., 70%
Function:       {{config.coverage.function}}       e.g., 90%
Statement:      {{config.coverage.statement}}      e.g., 85%
Mutation:       {{config.coverage.mutation}}       e.g., 80%
Path:           {{config.coverage.path}}           e.g., 60%

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
Framework:       {{config.testing_framework}}        e.g., Jest, Vitest, Mocha
Mocking library: {{config.mocking_library}}              e.g., jest-mock, sinon
Coverage tool:  {{config.coverage_tool}}              e.g., Jest coverage, c8
E2E tool:       {{config.e2e_tool}}             e.g., Playwright, Cypress

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
