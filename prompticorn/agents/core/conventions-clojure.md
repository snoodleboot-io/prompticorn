<!-- path: prompticorn/prompts/agents/core/core-conventions-clojure.md -->
# Core Conventions Clojure

Language:             {{ language }} e.g., Clojure 1.12
Runtime:              {{ runtime }} e.g., JVM
Build tool:           {{ build_tool }} e.g., deps.edn, Leiningen
Linter:               {{ linter }} e.g., eastwood, clj-kondo
Formatter:           {{ formatter }} e.g., cljfmt

### Naming Conventions

Files:              snake_case
Variables:          kebab-case
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase (for protocols/records)
Functions:          kebab-case
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## Clojure-Specific Rules

### Data Structures
- Use persistent data structures
- Use keywords for keys
- Prefer vectors over lists

### Error Handling
- Use exceptions for error handling
- Use either monad patterns

### Code Style
- Follow Clojure style guide
- Use meaningful names

### Testing
Framework:       {{ test_framework }}        e.g., clojure.test
Property tool:           e.g., test.check
Coverage tool:  {{ coverage_tool }}              e.g., cloverage
