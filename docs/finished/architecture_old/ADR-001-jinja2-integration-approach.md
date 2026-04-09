# ADR-001: Jinja2 Template Renderer Integration Approach

**Date:** 2026-04-03  
**Status:** Proposed  
**Deciders:** Engineering Team  
**Context:** Jinja2 migration infrastructure is complete but core Builder integration is missing

## Context

The Jinja2 template migration has built extensive infrastructure including:
- Jinja2TemplateRenderer with full Jinja2 feature support
- Template validation and error handling
- Comprehensive test coverage (90%+)
- Migration documentation and task breakdown

However, the core Builder._substitute_template_variables() method still uses legacy string replacement instead of the new Jinja2 renderer. This creates an inconsistent architecture where powerful Jinja2 capabilities exist but aren't utilized.

## Problem

The template system has two competing implementations:
1. Legacy: Simple string replacement with limited {{VARIABLE}} syntax
2. New: Full Jinja2 with conditionals, loops, filters, inheritance

This inconsistency prevents users from leveraging Jinja2's advanced features and creates maintenance burden. The migration was marked "complete" but the core integration step was omitted.

## Decision Drivers

- **Consistency**: All templates should use same powerful syntax
- **Maintainability**: Single template system reduces code complexity  
- **User Experience**: Unlock Jinja2 features (conditionals, loops, filters)
- **Backward Compatibility**: Existing templates should continue working
- **Performance**: Jinja2 caching provides better performance than string replacement

## Options Considered

### Option 1: Complete Integration with Handler Compatibility
**Approach:** Replace Builder string replacement with Jinja2 renderer, maintain handler registry pattern. Collect handler-provided variables into Jinja2 context dict.

**Pros:**
- Maintains existing handler architecture
- Backward compatible with current variable resolution
- Gradual migration path for complex handlers
- Preserves extensibility for custom variable logic

**Cons:**
- Mixed architecture (handlers + Jinja2 context)
- Potential variable name conflicts
- Handler logic still needed for complex variables
- More complex integration

**Effort:** Medium (1-2 days)
**Risk:** Medium - handler/Jinja2 interaction edge cases

### Option 2: Pure Jinja2 Context Injection  
**Approach:** Eliminate handler registry, pass all variables directly to Jinja2. Convert handlers to context builders or eliminate them entirely.

**Pros:**
- Clean architecture - single template system
- Maximum Jinja2 power (filters, macros, inheritance)
- Simpler code - no dual variable resolution
- Better performance - direct context injection

**Cons:**
- Breaking change for handler-based variable logic
- Migration complexity for custom handlers
- Loss of dynamic handler registration
- Requires converting all handlers to context functions

**Effort:** High (3-5 days)  
**Risk:** High - potential breaking changes

### Option 3: Hybrid Approach with Feature Flags
**Approach:** Add feature flag to enable Jinja2 per-builder or per-template. Allow gradual migration with fallback to string replacement.

**Pros:**
- Zero-risk migration path
- Can test Jinja2 in production safely
- Gradual rollout prevents breaking changes
- Easy rollback if issues found

**Cons:**
- Prolonged dual maintenance
- Configuration complexity
- User confusion about which syntax to use
- Delayed benefits realization

**Effort:** High (2-3 days for feature flag, ongoing for dual maintenance)
**Risk:** Low - can rollback anytime

## Decision

**Chosen:** Option 1 - Complete Integration with Handler Compatibility

We will replace the Builder's string replacement logic with Jinja2 rendering while preserving the existing handler registry pattern. Handler-provided variables will be collected into a context dict passed to Jinja2.

## Rationale

This approach balances architectural purity with practical migration constraints:

1. **Maintains backward compatibility** - existing handlers continue working
2. **Enables Jinja2 features** - users can use advanced templating immediately  
3. **Reduces risk** - no breaking changes to variable resolution logic
4. **Provides migration path** - handlers can be gradually converted to pure Jinja2 context if desired
5. **Acceptable complexity** - integration is straightforward, maintains existing patterns

The handler registry provides valuable extensibility that would be complex to recreate purely in Jinja2 context. Option 2's "pure" approach would require significant rework of how variables are resolved, while Option 3 delays the benefits indefinitely.

## Consequences

**Positive:**
- Immediate access to Jinja2 features (conditionals, loops, filters)
- Better performance through Jinja2 caching
- Consistent template syntax across the system
- Maintains existing extensibility patterns

**Negative / Trade-offs:**
- Mixed architecture with both handlers and Jinja2 context
- Potential for variable name conflicts (mitigated by clear naming conventions)
- Continued maintenance of handler pattern alongside Jinja2
- Slight performance overhead from handler resolution before Jinja2 rendering

**Risks:**
- Edge cases where handler variables conflict with Jinja2 context
- Handler logic might not translate perfectly to Jinja2 expectations
- Testing complexity with dual variable resolution paths

**Mitigation:**
- Comprehensive testing of handler variable resolution
- Clear documentation of variable precedence rules
- Error handling for conflicts with helpful messages
- Gradual rollout with extensive testing

## Implementation Plan

1. **Phase 1 - Core Integration (Day 1):**
   - Add Jinja2 imports to Builder
   - Create Jinja2 environment in Builder.__init__
   - Instantiate Jinja2TemplateRenderer
   - Modify _substitute_template_variables to collect handler variables and call renderer.handle()

2. **Phase 2 - Testing & Validation (Day 1-2):**
   - Update existing unit tests to work with Jinja2
   - Test handler variable resolution in Jinja2 context
   - Validate Jinja2 features work (filters, conditionals)
   - End-to-end testing with real templates

3. **Phase 3 - Documentation & Migration (Day 2):**
   - Update migration guide with integration details
   - Document handler/Jinja2 interaction rules
   - Create examples of advanced Jinja2 usage

## Success Criteria

- [ ] Builder._substitute_template_variables() uses Jinja2 renderer
- [ ] All existing handler variables resolve correctly in Jinja2 context  
- [ ] Jinja2 features work ({{var | filter}}, {% if %}, {% for %})
- [ ] All existing tests pass
- [ ] No performance regression
- [ ] Templates using advanced Jinja2 syntax work correctly

## Review Date

2026-06-03 - Review after 2 months of production usage to assess if handler pattern should be simplified.

