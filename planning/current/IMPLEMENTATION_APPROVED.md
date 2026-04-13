# Agent Skills & Workflows Implementation - APPROVED

**Date**: 2026-04-12
**Status**: APPROVED - Ready to implement

## User Decisions

1. ✅ **Option 2 Approved**: Create `agent_skill_mapping.yaml` as primary mapping system
2. ✅ **Loader Location**: `promptosaurus/ir/loaders/agent_skill_mapping_loader.py`
3. ✅ **File Location**: `promptosaurus/configurations/agent_skill_mapping.yaml` (NOT project root)
4. ✅ **Backwards Compatibility**: NOT needed - remove existing python/code entries
5. ✅ **Validation**: YES - add validation to ensure all 25 agents have entries
6. ✅ **Language Overrides**: Keep concept for future use, but none currently needed

## Corrected File Locations

### New Files:
1. **`promptosaurus/configurations/agent_skill_mapping.yaml`** - 25 agent entries
2. **`promptosaurus/ir/loaders/agent_skill_mapping_loader.py`** - Loader class
3. **`tests/unit/ir/loaders/test_agent_skill_mapping_loader.py`** - Unit tests
4. **`scripts/generate_agent_mapping.py`** - Generator script
5. **`scripts/validate_agent_mappings.py`** - Validation script

### Modified Files:
1. **`promptosaurus/prompt_builder.py`** - Add agent_skill_loader, update filtering
2. **`promptosaurus/ir/loaders/__init__.py`** - Export new loader
3. **`promptosaurus/configurations/language_skill_mapping.yaml`** - Remove python section
4. **`README.md`** - Document the two-tier mapping system

## Implementation Order

### Phase 1: Create Infrastructure
1. Create `promptosaurus/configurations/agent_skill_mapping.yaml`
2. Create `AgentSkillMappingLoader` class
3. Add unit tests for loader
4. Update `__init__.py` to export loader

### Phase 2: Integrate with Build System
1. Update `prompt_builder.py` to use agent_skill_loader
2. Implement priority resolution (agent → language → fallback)
3. Add validation for complete agent coverage

### Phase 3: Clean Up
1. Remove python section from `language_skill_mapping.yaml`
2. Remove python/code, python/test entries (now redundant)
3. Update documentation

### Phase 4: Test & Verify
1. Run build: `uv run prompt build kilo`
2. Verify agent files have correct skills/workflows
3. Test with multiple languages
4. Run validation script

## Next Steps

Proceed with implementation in order above.

