<!-- path: promptosaurus/prompts/agents/core/core-conventions-haskell.md -->
# Core Conventions Haskell

Language:             {{config.language}}           e.g., Haskell 9.8
Package Manager:      {{config.package_manager}}        e.g., Cabal, Stack
Linter:              {{config.linter}}             e.g., HLint, Stan
Formatter:           {{config.formatter}}          e.g., Brittany, Ormolu

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
Framework:       {{config.testing_framework}}        e.g., HSpec, QuickCheck
Property tool:   {{config.property_tool}}        e.g., QuickCheck, Hedgehog
Coverage tool:  {{config.coverage_tool}}              e.g., HPC
