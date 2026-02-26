# Clojure Conventions

Language:             {{LANGUAGE}}           e.g., Clojure 1.12
Runtime:              {{RUNTIME}}            e.g., JVM
Package Manager:      {{PKG_MANAGER}}        e.g., deps.edn, Leiningen
Linter:              {{LINTER}}             e.g., eastwood, clj-kondo
Formatter:           {{FORMATTER}}          e.g., cljfmt

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
Framework:       {{TEST_FRAMEWORK}}        e.g., clojure.test
Property tool:   {{PROPERTY_TOOL}}        e.g., test.check
Coverage tool:  {{COV_TOOL}}              e.g., cloverage
