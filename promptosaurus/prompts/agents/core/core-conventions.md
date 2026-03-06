<!-- path: promptosaurus/prompts/agents/core/core-conventions.md -->
# Core Conventions

Project coding standards - base conventions for all projects. 

For language-specific rules, see: core-conventions-ts.md, core-conventions-py.md, etc.

All mode-specific rules inherit from this file.

## Repository Structure

Repository type: {{single-language | multi-language-folder | mixed-collocation}}

### If single-language:
Include: core-conventions-[LANG].md where [LANG] matches your primary language

### If multi-language-folder:
Define each language area:
- /frontend      → include: Core Conventions TypeScript
- /backend       → include: Core Conventions Python
- /shared        → include: Core Conventions Golang

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

### Class Organization Rules

Rule: One class per file. Each class must be in its own dedicated file.
Rule: Filename must be the snake_case version of the class name.
  - Example: `class ConfigHandler` → `config_handler.py`
  - Example: `class SelectionState` → `selection_state.py`
  - Example: `class SingleSelectState` → `single_select_state.py`
  - Example: `class RenderStage` → `render_stage.py`
  - Example: `class CommandFactory` → `command_factory.py`

This rule ensures:
- Clear file-to-class mapping for maintainability
- Easier navigation in IDEs
- Consistent naming across the codebase
- Simplified imports and dependency tracking

### SOLID Principles for OOP Components

All OOP components must follow SOLID principles:

**S - Single Responsibility Principle (SRP)**
- Each class has one reason to change
- A class should do one thing and do it well
- Split large classes into smaller, focused ones

**O - Open/Closed Principle (OCP)**
- Open for extension, closed for modification
- Use inheritance, composition, or interfaces to extend behavior
- Avoid modifying existing working code to add features

**L - Liskov Substitution Principle (LSP)**
- Subtypes must be substitutable for their base types
- Derived classes should extend behavior without changing contracts
- Breaking parent behavior in subclasses violates LSP

**I - Interface Segregation Principle (ISP)**
- Clients should not depend on interfaces they don't use
- Split large interfaces into smaller, focused ones
- Prefer multiple small interfaces over one large interface

**D - Dependency Inversion Principle (DIP)**
- Depend on abstractions, not concrete implementations
- High-level modules should not depend on low-level modules
- Both should depend on abstractions (interfaces/abstract classes)

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

For language-specific rules, include the appropriate context from:
- `Core Conventions Typescript` - TypeScript/JavaScript
- `Core Conventions Python` - Python
- `Core Conventions Golang` - Go
- `Core Conventions Java` - Java
- `Core Conventions Rust` - Rust
- `Core Conventions SQL` - SQL

These files contain language-specific patterns for:
- Error handling patterns
- Type system usage
- Testing frameworks and patterns
- Module/dependency management

## Session Context Management

All modes must follow the session management protocol defined in `core-session.md`:

1. **Check for session on startup** - Look for existing session for current branch
2. **Create session if needed** - New session if none exists for current branch
3. **Update on mode switch** - Record exit from current mode, entry to new mode
4. **Record actions** - Log significant actions with timestamps
5. **Maintain context** - Keep Context Summary current

Session files provide continuity across mode switches and persist workflow state.
See `Core Session` for complete protocol and file format specifications.
