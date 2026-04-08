<!-- path: promptosaurus/prompts/agents/core/core-conventions-ruby.md -->
{%- import 'macros/testing_sections.jinja2' as testing -%}
{%- import 'macros/coverage_targets.jinja2' as coverage -%}
# Core Conventions Ruby

Language:             {{config.language}}           e.g., Ruby 3.3
Runtime:              {{config.runtime}}            e.g., MRI, JRuby
Package Manager:      {{config.package_manager}}        e.g., Bundler
Linter:               {{config.linter}}             e.g., RuboCop
Formatter:           {{config.formatter}}          e.g., Rufo, RuboCop

### Naming Conventions

Files:              snake_case
Variables:          snake_case
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          snake_case (methods)
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## Ruby-Specific Rules

### Type System
- Use RBS for type signatures (Ruby 3.0+)
- Use strict typing in critical code paths

### Error Handling
- Use exceptions for error handling
- Never rescue Exception (rescue StandardError instead)
- Use begin/rescue/ensure blocks

### Code Style
- Follow Ruby style guide (RuboCop)
- Use RuboCop for linting
- Use meaningful method names

### Testing

{{ testing.render_test_types('ruby') }}

{{ coverage.render_coverage_table(
  line=config.coverage.line | default('80'),
  branch=config.coverage.branch | default('70'),
  function=config.coverage.function | default('90'),
  statement=config.coverage.statement | default('85'),
  mutation=config.coverage.mutation | default('80'),
  path=config.coverage.path | default('60')
) }}
