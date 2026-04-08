<!-- path: promptosaurus/prompts/agents/core/core-conventions-lua.md -->
# Core Conventions Lua

Language:             {{config.language}}           e.g., Lua 5.4
Runtime:              {{config.runtime}}            e.g., LuaJIT, Lua VM
Package Manager:      {{config.package_manager}}        e.g., LuaRocks
Linter:              {{config.linter}}             e.g., luacheck
Formatter:           {{config.formatter}}          e.g., lua-format

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
Framework:       {{config.testing_framework}}        e.g., busted
Coverage tool:  {{config.coverage_tool}}              e.g., luacov
