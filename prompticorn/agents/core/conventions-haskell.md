<!-- path: prompticorn/prompts/agents/core/core-conventions-haskell.md -->
# Core Conventions Haskell

Language:             {{ language or "e.g., Haskell 9.8" }}
Compiler:             {{ compiler or "e.g., GHC" }}
Build tool:           {{ build_tool or "e.g., Cabal, Stack" }}
Linter:               {{ linter or "e.g., HLint, Stan" }}
Formatter:           {{ formatter or "e.g., Brittany, Ormolu" }}

### Naming Conventions

Files:              snake_case
Variables:          camelCase
Constants:          PascalCase
Classes/Types:      PascalCase
Functions:          snake_case (camelCase for type classes)
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## Haskell-Specific Rules

### Type System
- Use strong typing
- Use GADTs where needed
- Leverage type inference

### Error Handling
- Use Either for error handling
- Use Maybe for optional values
- Avoid exceptions in pure code

### Code Style
- Follow Haskell style guide
- Use hlint for linting

### Testing
Framework:       {{ test_framework or "e.g., HSpec, QuickCheck" }}
Property tool:           e.g., QuickCheck, Hedgehog
Coverage tool:  {{ coverage_tool or "e.g., HPC" }}
