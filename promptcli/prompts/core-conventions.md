<!-- path: flat/core-conventions.md -->
# core-conventions.md
# Project coding standards - base conventions for all projects.
# For language-specific rules, see: core-conventions-ts.md, core-conventions-py.md, etc.
# All mode-specific rules inherit from this file.

## Repository Structure

Repository type: {{single-language | multi-language-folder | mixed-collocation}}

### If single-language:
Include: core-conventions-[LANG].md where [LANG] matches your primary language

### If multi-language-folder:
Define each language area:
- /frontend      → include: core-conventions-ts.md
- /backend       → include: core-conventions-py.md
- /shared        → include: core-conventions-go.md

### If mixed-collocation:
File extension determines which rules apply:
- *.ts, *.tsx   → TypeScript rules
- *.py           → Python rules
- *.go           → Go rules

## Shared Conventions

These conventions apply to all languages and projects:

### Naming Conventions

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

## Testing

Testing conventions are language-specific. See your language's conventions file for:
- Test framework recommendations
- Coverage targets
- Test style patterns
- Mocking approaches

## Database

Database:            {{DATABASE}}           e.g., PostgreSQL, DynamoDB
ORM/Query:           {{ORM}}                e.g., Prisma, SQLAlchemy, GORM

## Git & PR Conventions

Branch naming:       feat|fix|chore|docs / ticket-id - short-description
Commit style:        {{Conventional Commits | free-form}}
PR size:             {{MAX_LINES}} lines changed (soft limit)

## Deployment

Target:              {{DEPLOYMENT_TARGET}}  e.g., AWS Lambda, Vercel, GKE

---

# Language-Specific Conventions

For language-specific rules, include the appropriate file:
- `core-conventions-ts.md` - TypeScript/JavaScript
- `core-conventions-py.md` - Python
- `core-conventions-go.md` - Go
- `core-conventions-java.md` - Java
- `core-conventions-rust.md` - Rust
- `core-conventions-sql.md` - SQL

These files contain language-specific patterns for:
- Error handling patterns
- Type system usage
- Testing frameworks and patterns
- Module/dependency management
