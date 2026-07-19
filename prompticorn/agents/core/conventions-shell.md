<!-- path: prompticorn/prompts/agents/core/core-conventions-shell.md -->
# Core Conventions Shell

Language:             {{ language }} e.g., Bash 5.2, Zsh
Shell:              {{ shell_type }}             e.g., Bash, Zsh
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
Line:           {{ coverage_targets.get('line', '') }}          e.g., 80%

#### Test Types
- Use bats-core for testing
- Test scripts as black box

#### Framework & Tools
Framework:       {{ test_framework }}        e.g., bats-core, shunit2
Linting:       {{ linter }}           e.g., shellcheck
Coverage tool:  {{ coverage_tool }}              e.g., bashcov
