<!-- path: promptosaurus/prompts/agents/core/core-conventions-shell.md -->
# Core Conventions Shell

Language:             {{ language }} e.g., Bash 5.2, Zsh
Shell:              {{ shell }}             e.g., Bash, Zsh
Package Manager:      {{ package_manager }} e.g., apt, yum, brew

### Naming Conventions

Files:              snake_case
Variables:          snake_case (or SCREAMING_SNAKE for env vars)
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          snake_case
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## Shell-Specific Rules

### Error Handling
- Use `set -e` to exit on error
- Use `set -u` to exit on undefined variable
- Check return values of commands

### Code Style
- Use shellcheck for linting
- Use meaningful variable names
- Quote variables

### Testing

#### Coverage Targets
Line:           [Template variable]          e.g., 80%

#### Test Types
- Use bats-core for testing
- Test scripts as black box

#### Framework & Tools
Framework:       [Template variable]        e.g., bats-core, shunit2
Linting:       [Template variable]           e.g., shellcheck
Coverage tool:  [Template variable]              e.g., bashcov
