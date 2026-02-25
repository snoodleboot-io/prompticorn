# core-conventions.md
# Project coding standards. EDIT THIS FILE for each project.
# All mode-specific rules inherit from this file.

## Language & Runtime

Primary Language:    {{LANGUAGE}}           e.g., TypeScript 5.x
Runtime:             {{RUNTIME}}            e.g., Node 20, Python 3.12, Go 1.22
Package Manager:     {{PKG_MANAGER}}        e.g., pnpm, poetry, go mod
Linter:              {{LINTER}}             e.g., ESLint, Ruff, golangci-lint
Formatter:           {{FORMATTER}}          e.g., Prettier, Black, gofmt

## Naming Conventions

Files:               {{kebab-case | snake_case | PascalCase}}
Variables:           {{camelCase | snake_case}}
Constants:           {{UPPER_SNAKE | PascalCase}}
Classes/Types:       {{PascalCase}}
Functions:           {{camelCase | snake_case}}
Database tables:     {{snake_case | PascalCase}}
Environment vars:    UPPER_SNAKE_CASE always

## File & Folder Structure

src/
└── {{your structure here}}

Rule: One export per file unless it is a barrel (index.ts).
Rule: Co-locate tests with source (auth.ts → auth.test.ts).

## Error Handling

Pattern: {{throw | return Result<T, E> | return [data, error]}}

- Never swallow errors silently
- Always include context: Error("failed to fetch user: " + userId)
- Log at the boundary where the error is handled, not where it is thrown
- Use typed errors, not generic Error or Exception

## Imports & Dependencies

- Prefer standard library over third-party where equivalent
- No circular imports
- Group imports: stdlib → third-party → internal (blank line between groups)
- Flag any new dependency before adding it

## Testing Standards

Framework:           {{TEST_FRAMEWORK}}     e.g., Jest, Pytest, Go test
Coverage target:     {{COVERAGE_%}}         e.g., 80%
Test style:          AAA                    Arrange-Act-Assert
Mocking library:     {{MOCK_LIB}}           e.g., jest.mock, unittest.mock

- Unit tests: one function or method in isolation
- Integration tests: at the service or module boundary
- No test should depend on another test's state

## Database

Database:            {{DATABASE}}           e.g., PostgreSQL, DynamoDB
ORM/Query:           {{ORM}}                e.g., Prisma, SQLAlchemy, GORM

## Git & PR Conventions

Branch naming:       feat|fix|chore|docs / ticket-id - short-description
Commit style:        {{Conventional Commits | free-form}}
PR size:             {{MAX_LINES}} lines changed (soft limit)

## Deployment

Target:              {{DEPLOYMENT_TARGET}}  e.g., AWS Lambda, Vercel, GKE

## Language-Specific Rules

### TypeScript
- strict mode always on
- No any — use unknown + type narrowing
- Prefer interface for object shapes, type for unions/intersections
- Always type function return values explicitly

### Python
- Type hints required on all public functions
- Use dataclasses or pydantic for data shapes, not raw dicts
- Async: use asyncio — no mixing sync/async without explicit bridging

### Go
- Return (T, error) — never panic in library code
- Use context.Context as first arg on all I/O functions
- Prefer table-driven tests

### SQL
- Parameterized queries always — no string interpolation
- Migrations: always include up and down
- Index any column used in WHERE or JOIN
