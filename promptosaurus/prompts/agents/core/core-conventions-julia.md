<!-- path: promptosaurus/prompts/agents/core/core-conventions-julia.md -->
# Core Conventions Julia

Language:             {{LANGUAGE}}           e.g., Julia 1.10
Package Manager:      {{PACKAGE_MANAGER}}        e.g., Pkg
Linter:              {{LINTER}}             e.g., Jet.jl, Lint.jl
Formatter:           {{FORMATTER}}          e.g., JuliaFormatter

### Naming Conventions

Files:              snake_case
Variables:          snake_case
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          snake_case
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## Julia-Specific Rules

### Type System
- Use multiple dispatch effectively
- Type annotations where performance matters
- Use abstract types for interfaces

### Error Handling
- Use exceptions for error handling
- Use try/catch for exception handling

### Code Style
- Follow Julia style guide
- Use descriptive function names

### Testing
Framework:       {{TESTING_FRAMEWORK}}        e.g., Test.jl
Coverage tool:  {{COVERAGE_TOOL}}              e.g., Coverage.jl
