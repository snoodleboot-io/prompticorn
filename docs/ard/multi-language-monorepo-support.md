# Architecture Decision Record: Multi-Language Monorepo Support

**Document Version:** 1.0  
**Date:** 2026-03-10  
**Status:** Draft  
**Author:** AI Assistant  
**Related PRD:** multi-language-monorepo-support.md

---

## 1. Context

### 1.1 What is the issue we're addressing?

The current implementation of multi-language support only stores the repository type but doesn't provide:
- Interactive folder setup
- Per-folder language configuration
- Support for hierarchical folder structures

### 1.2 What are the forces at play?

**Technical forces:**
- Existing config structure uses a single `spec` object for language settings
- Need to maintain backward compatibility with single-language configs
- Builders need to understand folder-specific configuration

**User forces:**
- Users want quick setup via presets
- Users need flexibility for custom folder structures
- Users expect each folder to have appropriate tool defaults

**Project forces:**
- Must fit within existing CLI architecture
- Should minimize changes to existing code paths

---

## 2. Decision

### 2.1 Primary Decision

**Convert `spec` from a single object to a list when `repository.type = "multi-language-monorepo"`**

```yaml
# For single-language:
spec:
  language: "python"
  runtime: "3.12"
  ...

# For multi-language-monorepo:
spec:
  - folder: "frontend"
    language: "typescript"
    ...
  - folder: "backend"
    language: "python"
    ...
```

### 2.2 Detection Strategy

**Dual detection:** Both `repository.type` and spec structure determine the mode.

- `repository.type = "single-language"` → spec is a dict
- `repository.type = "multi-language-monorepo"` → spec is a list

Validation: Ensure spec structure matches repository.type.

---

## 3. Alternatives Considered

### Alternative 1: Separate `folder_specs` Key

Keep `spec` as-is and add a new `folder_specs` key.

**Pros:**
- Complete backward compatibility
- Clear separation of concerns

**Cons:**
- Redundant storage
- More complex validation
- Two places to look for language config

**Decision:** Rejected - adds unnecessary complexity

### Alternative 2: Nested Under `repository.folders`

Store folder configs under `repository.folders` key.

**Pros:**
- Logical grouping with `repository.type`

**Cons:**
- Moves language config away from other spec fields
- Inconsistent with existing config structure

**Decision:** Rejected - breaks consistency with existing API

### Alternative 3: Spec Becomes List (Selected)

Replace `spec` object with `spec` list for multi-language-monorepo.

**Pros:**
- Consistent API: `spec` always contains language config
- Simple validation: check if dict (single) or list (multi)
- Easy to iterate in builders

**Cons:**
- Breaking change for existing configs (requires migration)
- Need to update all code that accesses `spec`

**Decision:** Accepted - cleanest API, straightforward implementation

---

## 4. Consequences

### 4.1 Positive Consequences

1. **Clean API:** Single field `spec` always contains language configuration
2. **Easy iteration:** Builders can loop through folders uniformly
3. **Type safety:** Can validate structure based on repository.type
4. **Extensible:** Easy to add more folder properties in future

### 4.2 Negative Consequences / Tradeoffs

1. **Migration required:** Existing multi-language-folder configs must be manually migrated
2. **Code updates:** All code accessing `spec` must handle both dict and list
3. **Validation complexity:** Need to ensure spec structure matches repository.type

### 4.3 Observations

- The rename from "multi-language-folder" to "multi-language-monorepo" clarifies intent
- Standard presets (frontend/backend) provide quick setup while custom provides flexibility
- Hierarchical folder support enables complex monorepo structures

---

## 5. Implementation Notes

### 5.1 SOLID Principles

Following SOLID principles for this change:

- **Single Responsibility**: Each class has one job:
  - `FolderSpec` - represents a single folder's configuration
  - `SpecHandler` - handles spec as dict or list based on repo type
  - `FolderSetupQuestion` - handles interactive folder creation

- **Open/Closed**: System is open for extension:
  - New folder types can be added without modifying existing code
  - Preset configurator can be extended with new presets

- **Liskov Substitution**: `FolderSpec` objects are interchangeable in lists

- **Interface Segregation**: Separate interfaces for:
  - Reading specs (`SpecReader`)
  - Writing specs (`SpecWriter`)
  - Validating specs (`SpecValidator`)

- **Dependency Inversion**: High-level modules depend on abstractions:
  - CLI depends on `SpecHandler` protocol, not concrete implementation

### 5.2 Files to Create

| File | Description |
|------|-------------|
| `questions/base/folder_spec.py` | FolderSpec dataclass |
| `questions/base/spec_handler.py` | SpecHandler protocol and implementation |
| `questions/base/preset_configurator.py` | PresetConfigurator class |

### 5.3 Files to Modify

| File | Change |
|------|--------|
| `config_handler.py` | Update DEFAULT_CONFIG_TEMPLATE, create_default_config() |
| `config_options.py` | Add folder-spec related options |
| `cli.py` | Implement interactive folder setup flow |
| `questions/base/` | Add folder configuration questions |
| `builders/` | Update to handle spec as list |

### 5.4 New Components

| Component | Type | Responsibility |
|-----------|------|----------------|
| `FolderSpec` | Dataclass | Represents a single folder's configuration |
| `SpecHandler` | Protocol | Abstracts spec handling (dict vs list) |
| `FolderSetupQuestion` | Class | Handles interactive folder creation |
| `PresetConfigurator` | Class | Applies defaults based on type/subtype |

### 5.3 Testing Strategy

- Unit tests for config handling (spec as dict vs list)
- Integration tests for CLI flow
- Validation tests for folder structure

---

## 6. Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-------------|
| Migration failures | Medium | High | Clear documentation, error messages |
| Builder compatibility | Low | High | Update all builders to handle list |
| Performance with many folders | Low | Low | Specs are small, iteration is fast |

---

## 7. Related Documents

- PRD: [multi-language-monorepo-support.md](../prd/multi-language-monorepo-support.md)
- Related ARDs: session-context-persistence.md, cli-switch-update-commands.md
