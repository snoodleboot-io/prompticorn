<!-- path: promptosaurus/prompts/agents/core/core-conventions-julia.md -->
# Core Conventions Julia

Language:             {{ language }} e.g., Julia 1.10
Package Manager:      {{ package_manager }} e.g., Pkg
Linter:               {{ linter }} e.g., Jet.jl, Lint.jl
Formatter:           {{ formatter }} e.g., JuliaFormatter

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
Framework:       [Template variable]        e.g., Test.jl
Coverage tool:  [Template variable]              e.g., Coverage.jl
