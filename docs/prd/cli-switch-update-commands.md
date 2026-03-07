# Product Requirements Document: CLI Switch and Update Commands

**Document Version:** 1.0  
**Date:** 2026-03-06  
**Status:** Draft  
**Author:** AI Assistant  

---

## 1. Executive Summary

This PRD documents two new CLI commands for the PromptCLI/Kilo Code system:

1. **`switch` command** - Switch between AI assistant tools (kilo-cli, kilo-ide, cline, cursor, copilot)
2. **`update` command** - Update configuration options interactively with visual feedback

These enhancements improve user experience by providing easy configuration management after initial setup.

---

## 2. Feature 1: switch Command

### 2.1 Problem Statement

Currently, users who want to switch from one AI tool to another must run `prompt init` again, which:
- Re-prompts all questions even for unchanged settings
- Doesn't preserve existing configuration
- Creates friction for users who want to try different AI tools

### 2.2 User Stories

**US-1.1:** As a user, I want to specify the AI tool as a command argument so I can quickly switch without interactive prompts.

**US-1.2:** As a user, I want to be presented with a menu of available AI tools if I don't specify one, so I can choose interactively.

**US-1.3:** As a user, I want tool names to be normalized automatically (remove special characters, convert to lowercase) so that typos don't prevent switching.

**US-1.4:** After switching tools, I want new AI assistant configuration artifacts to be created and old ones to be removed, so my project only has the active tool's configuration.

### 2.3 Requirements

#### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| F1.1 | Command format: `prompt switch [tool-name]` | Must |
| F1.2 | If tool-name provided: use it directly (normalized) | Must |
| F1.3 | If no tool-name: display interactive menu using `select_option_with_explain` | Must |
| F1.4 | Normalize tool names: remove special characters, convert to lowercase | Must |
| F1.5 | Validate tool name against supported tools: kilo-cli, kilo-ide, cline, cursor, copilot | Must |
| F1.6 | Generate new AI tool artifacts using appropriate builder | Must |
| F1.7 | Remove old AI tool artifacts (files specific to previous tool) | Must |
| F1.8 | Preserve existing configuration (repository type, language, etc.) | Must |
| F1.9 | Display progress messages for file operations | Should |
| F1.10 | Handle case where config doesn't exist (prompt to run init first) | Must |

#### Normalization Rules

| Input | Normalized Output |
|-------|-------------------|
| `Kilo-CLI` | `kilo-cli` |
| `kilo_ide` | `kiloide` |
| `Cline` | `cline` |
| `Cursor` | `cursor` |
| `Copilot` | `copilot` |
| `KILO-CLI!` | `kilocli` |

#### CLI Interface

```bash
# With tool name argument
prompt switch kilo-ide
prompt switch cline
prompt switch cursor

# Without argument (interactive menu)
prompt switch

# Invalid tool
prompt switch invalid-tool
# Error: "Invalid tool 'invalid-tool'. Supported tools: kilo-cli, kilo-ide, cline, cursor, copilot"

# No config exists
prompt switch
# Error: "No configuration found. Run 'prompt init' first."
```

### 2.4 Artifacts to Manage

| AI Tool | Files to Create | Files to Remove |
|---------|-----------------|-----------------|
| kilo-cli | `.opencode/` directory | `.kilocode/`, `.clinerules`, `.cursor/`, `.github/copilot-instructions.md` |
| kilo-ide | `.kilocode/` directory | `.opencode/`, `.clinerules`, `.cursor/`, `.github/copilot-instructions.md` |
| cline | `.clinerules` | `.opencode/`, `.kilocode/`, `.cursor/`, `.github/copilot-instructions.md` |
| cursor | `.cursor/` directory + `.cursorrules` | `.opencode/`, `.kilocode/`, `.clinerules`, `.github/copilot-instructions.md` |
| copilot | `.github/copilot-instructions.md` | `.opencode/`, `.kilocode/`, `.clinerules`, `.cursor/` |

### 2.5 Success Metrics

- Users can switch tools in under 10 seconds
- Tool name normalization handles at least 90% of common input variations
- Old artifacts are completely removed in 100% of switches
- Configuration is preserved across switches

---

## 3. Feature 2: update Command

### 3.1 Problem Statement

After initial setup with `prompt init`, users may want to modify specific configuration options without rerunning the entire interactive wizard. Currently there's no way to update individual settings.

### 3.2 User Stories

**US-2.1:** As a user, I want to see all configurable options with their current values highlighted, so I know what is already set.

**US-2.2:** As a user, I want to navigate through options and change only the ones I need, so I don't have to re-enter unchanged values.

**US-2.3:** As a user, I want visual feedback showing which values are current (blue) and which are newly changed (green), so I can easily track my modifications.

**US-2.4:** Unlike switch, the update command should NOT include the AI tool option - that requires switch command.

### 3.3 Requirements

#### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| F2.1 | Command format: `prompt update` | Must |
| F2.2 | Display interactive menu with all configurable options | Must |
| F2.3 | Exclude AI tool from update options (use switch command instead) | Must |
| F2.4 | Current values displayed in blue color | Must |
| F2.5 | Changed values displayed in green color after modification | Must |
| F2.6 | Use `select_option_with_explain` for option selection | Must |
| F2.7 | Validate input for each option type | Must |
| F2.8 | Save configuration on completion | Must |
| F2.9 | Handle case where config doesn't exist (prompt to run init first) | Must |

#### Configurable Options (excluding AI tool)

| Option | Type | Current Values | Validation |
|--------|------|-----------------|------------|
| Repository Type | Single-select | single-language, multi-language-folder, mixed-collocation | Must be valid option |
| Language | Single-select | python, typescript, go, java, rust, etc. | Must be from LANGUAGE_KEYS |
| Runtime | Text | e.g., "3.12", "5.4" | Non-empty string |
| Package Manager | Single-select | poetry, npm, pip, etc. | Non-empty string |
| Test Framework | Single-select | pytest, vitest, jest, etc. | Non-empty string |
| Linter | Single-select | ruff, eslint, etc. | Non-empty string |
| Formatter | Single-select | ruff, prettier, etc. | Non-empty string |
| Coverage Targets | Composite | line: 80, branch: 70, etc. | Numeric 0-100 |

#### UI Mockup

```
============================================================
  Prompt CLI - Update Configuration
============================================================

Use ↑/↓ arrows to navigate options, Enter to modify.
Current values are shown in blue, changes in green.

> Repository Type     [single-language]  ← Current (blue)
  Language            [python]          ← Current (blue)
  Runtime             [3.12]             ← Current (blue)
  Package Manager     [poetry]           ← Current (blue)
  Test Framework     [pytest]           ← Current (blue)
  Linter              [ruff]             ← Current (blue)
  Formatter           [ruff]             ← Current (blue)
  Coverage            [line:80, branch:70]

============================================================
Select an option to modify (or press Enter to save):
```

After selecting and modifying "Language":

```
  Language            [typescript]       ← Changed (green)
```

### 3.4 Color Implementation

Using Click's styling:
- Current values: `click.style(value, fg="blue")`
- Changed values: `click.style(value, fg="green")`

### 3.5 Success Metrics

- Users can update any configuration option independently
- Visual feedback clearly distinguishes current vs changed values
- Configuration is saved correctly after update completes

---

## 4. Out of Scope

The following are explicitly out of scope for this feature:

1. **Bulk import/export** - No configuration file import/export
2. **AI tool option in update** - AI tool switching requires separate `switch` command
3. **Partial saves** - Must save complete configuration on completion
4. **Rollback** - No undo functionality for configuration changes

---

## 5. Dependencies

| Dependency | Impact |
|------------|--------|
| `promptosaurus/cli.py` | Add new commands to CLI group |
| `promptosaurus/config_handler.py` | Load/save configuration |
| `promptosaurus/builders/*` | Generate AI tool artifacts |
| `promptosaurus/ui/_selector.py` | Use `select_option_with_explain` for menus |
| Existing config structure | Must preserve and extend |

---

## 6. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Artifact removal accidentally removes user files | Low | High | Verify file ownership before deletion, use safe delete patterns |
| Color output not visible in all terminals | Medium | Low | Use both color AND text indicators (blue→current, green→changed) |
| Normalization produces invalid tool name | Low | Medium | Always validate against supported tools after normalization |
| Config corruption during save | Low | Medium | Write to temp file, then atomic rename |

---

## 7. Open Questions

1. Should the update command allow saving without exiting (apply changes incrementally)?
2. Should we track the currently selected AI tool in config so `switch` knows what to remove?
3. Should we add a `--force` flag to skip confirmation prompts?

---

## 8. Acceptance Criteria

### switch Command

- [ ] `prompt switch kilo-ide` works and generates kilo-ide artifacts
- [ ] `prompt switch` without argument shows interactive menu
- [ ] Tool name normalization: "Kilo-CLI" → "kilo-cli" works
- [ ] Invalid tool name shows error message with supported tools list
- [ ] Old artifacts are removed after switch
- [ ] Configuration is preserved (language, runtime, etc.)
- [ ] Error when no config exists

### update Command

- [ ] `prompt update` launches interactive configuration menu
- [ ] AI tool option is NOT shown in update menu
- [ ] Current values displayed in blue
- [ ] Changed values displayed in green
- [ ] Changes are saved to configuration file
- [ ] Error when no config exists

---

## 9. Related Documents

- [`promptosaurus/cli.py`](promptosaurus/cli.py:1) - CLI entry point
- [`promptosaurus/config_handler.py`](promptosaurus/config_handler.py:1) - Configuration management
- [`promptosaurus/builders/`](promptosaurus/builders/) - AI tool artifact builders
- [`docs/prd/feature-enhancements-batch-1.md`](docs/prd/feature-enhancements-batch-1.md:1) - Previous PRD for reference

---

## 10. Glossary

| Term | Definition |
|------|------------|
| Artifact | Files generated for an AI tool (e.g., .kilocode/, .clinerules) |
| Normalize | Process of converting input to standard form (lowercase, remove special chars) |
| Builder | Class that generates AI tool-specific configuration files |
