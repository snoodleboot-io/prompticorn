<!-- path: promptosaurus/prompts/agents/core/core-conventions-julia.md -->
# Core Conventions Julia

Language:             {{config.language}}           e.g., Julia 1.10
Package Manager:      {{config.package_manager}}        e.g., Pkg
Linter:              {{config.linter}}             e.g., Jet.jl, Lint.jl
Formatter:           {{config.formatter}}          e.g., JuliaFormatter

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
Framework:       {{config.testing_framework}}        e.g., Test.jl
Coverage tool:  {{config.coverage_tool}}              e.g., Coverage.jl
