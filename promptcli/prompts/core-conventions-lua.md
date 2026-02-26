# Lua Conventions

Language:             {{LANGUAGE}}           e.g., Lua 5.4
Runtime:              {{RUNTIME}}            e.g., LuaJIT, Lua VM
Package Manager:      {{PKG_MANAGER}}        e.g., LuaRocks
Linter:              {{LINTER}}             e.g., luacheck
Formatter:           {{FORMATTER}}          e.g., lua-format

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
Framework:       {{TEST_FRAMEWORK}}        e.g., busted
Coverage tool:  {{COV_TOOL}}              e.g., luacov
