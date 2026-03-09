<!-- path: promptosaurus/prompts/agents/core/core-conventions-lua.md -->
# Core Conventions Lua

Language:             {{LANGUAGE}}           e.g., Lua 5.4
Runtime:              {{RUNTIME}}            e.g., LuaJIT, Lua VM
Package Manager:      {{PACKAGE_MANAGER}}        e.g., LuaRocks
Linter:              {{LINTER}}             e.g., luacheck
Formatter:           {{FORMATTER}}          e.g., lua-format

### Naming Conventions

Files:              snake_case
Variables:          snake_case
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          snake_case
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## Lua-Specific Rules

### Type System
- Use tables for all data structures
- Use metamethods for operator overloading

### Error Handling
- Use pcall for error handling
- Use assert sparingly

### Code Style
- Follow Lua style guide
- Use meaningful variable names

### Testing
Framework:       {{TESTING_FRAMEWORK}}        e.g., busted
Coverage tool:  {{COVERAGE_TOOL}}              e.g., luacov
