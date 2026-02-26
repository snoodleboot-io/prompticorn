# Shell/Bash Conventions

Language:             {{LANGUAGE}}           e.g., Bash 5.2, Zsh
Shell:              {{SHELL}}             e.g., Bash, Zsh
Package Manager:      {{PKG_MANAGER}}        e.g., apt, yum, brew

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
Line:           {{LINE_COVERAGE_%}}          e.g., 80%

#### Test Types
- Use bats-core for testing
- Test scripts as black box

#### Framework & Tools
Framework:       {{TEST_FRAMEWORK}}        e.g., bats-core, shunit2
Linting:       {{LINT_TOOL}}           e.g., shellcheck
Coverage tool:  {{COV_TOOL}}              e.g., bashcov
