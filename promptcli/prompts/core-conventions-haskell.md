# Haskell Conventions

Language:             {{LANGUAGE}}           e.g., Haskell 9.8
Package Manager:      {{PKG_MANAGER}}        e.g., Cabal, Stack
Linter:              {{LINTER}}             e.g., HLint, Stan
Formatter:           {{FORMATTER}}          e.g., Brittany, Ormolu

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
Framework:       {{TEST_FRAMEWORK}}        e.g., HSpec, QuickCheck
Property tool:   {{PROPERTY_TOOL}}        e.g., QuickCheck, Hedgehog
Coverage tool:  {{COV_TOOL}}              e.g., HPC
