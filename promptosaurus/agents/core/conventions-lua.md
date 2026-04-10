<!-- path: promptosaurus/prompts/agents/core/core-conventions-lua.md -->
# Core Conventions Lua

Language:             {{ language }} e.g., Lua 5.4
Runtime:              {{ runtime }} e.g., LuaJIT, Lua VM
Package Manager:      {{ package_manager }} e.g., LuaRocks
Linter:               {{ linter }} e.g., luacheck
Formatter:           {{ formatter }} e.g., lua-format

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
Framework:       [Template variable]        e.g., busted
Coverage tool:  [Template variable]              e.g., luacov
