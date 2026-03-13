# Product Requirements Document: Multi-Language Monorepo Support

**Document Version:** 1.0  
**Date:** 2026-03-10  
**Status:** Draft  
**Author:** AI Assistant  
**Feature Branch:** feat/monorepo-support

---

## 1. Executive Summary

This PRD documents the multi-language monorepo support feature for the PromptCLI/Kilo Code system. This feature enables users to configure projects with different programming languages in different folders, replacing the previous "multi-language-folder" concept.

**Key Changes from Previous Implementation:**
- Renamed "multi-language-folder" to "multi-language-monorepo" for clarity
- Added interactive folder setup flow with standard presets
- Configuration now supports folder-specific language settings

---

## 2. Problem Statement

### 2.1 Current State
Currently, when users select "multi-language-folder" (now "multi-language-monorepo") as their repository type:
- The system only saves the repository type
- Language configuration remains at the single-language level
- No folder-specific customization is available
- Users see a placeholder message: "Folder mappings will be configured in a future step."

### 2.2 Problems Being Solved
1. **No folder-specific configuration:** Users cannot specify different languages for different folders
2. **No interactive setup:** No guided flow for configuring monorepo folder structure
3. **Inconsistent naming:** "multi-language-folder" doesn't clearly describe the feature

### 2.3 Why This Is Worth Solving Now
- Users have been asking for multi-language project support
- The existing placeholder in the CLI needs to be replaced with actual functionality
- The rename provides clearer terminology for users

---

## 3. Goals and Non-Goals

### 3.1 Primary Goals (Max 3)

1. **Interactive Folder Setup Flow**  
   Provide a guided workflow for users to configure monorepo folders with presets or custom options.

2. **Folder-Aware Configuration**  
   Enable per-folder language, runtime, and tool configuration (package manager, test framework, linter, formatter).

3. **Hierarchical Folder Support**  
   Support nested folder structures like `services/auth/api`, not just top-level folders.

### 3.2 Explicit Non-Goals

- **Mixed-collocation support:** Multiple languages in the same folder (NOT in scope)
- **Automatic folder detection:** Users must explicitly configure folders
- **Migration tooling:** Existing configs require manual migration to new format

---

## 4. User Stories

### 4.1 Interactive Setup

**US-1:** As a user, I want to choose from standard folder presets so I can quickly set up common monorepo structures.

**US-2:** As a user, I want to create custom folders with my own paths so I can model any folder structure.

**US-3:** As a user, I want to specify a description for each folder so I can document the folder's purpose.

**US-4:** As a user, I want to add multiple folders in one session so I can set up the entire monorepo at once.

### 4.2 Configuration

**US-5:** As a user, I want each folder to have its own language setting so that different parts of my project use different languages.

**US-6:** As a user, I want each folder to have its own tool configuration (package manager, test framework, linter, formatter) so that each folder follows its language's best practices.

**US-7:** As a user, I want hierarchical folder paths to work (e.g., `frontend/components`, `backend/api`) so I can model nested structures.

### 4.3 Standard Presets

**US-8:** As a user, selecting a "backend" preset should auto-configure appropriate defaults based on the chosen language.

**US-9:** As a user, selecting a "frontend" preset should auto-configure appropriate defaults based on the chosen language.

---

## 5. Functional Requirements

### 5.1 Folder Type System

| Type | Subtypes |
|------|----------|
| `backend` | `api`, `library`, `worker`, `cli` |
| `frontend` | `ui`, `library`, `e2e` |
| `custom` | (user-defined, no auto-configuration) |

### 5.2 Configuration Structure

For `repository.type = "multi-language-monorepo"`, the `spec` field becomes a list:

```yaml
spec:
  - folder: "frontend"
    type: "frontend"
    subtype: "ui"
    language: "typescript"
    runtime: "5.4"
    package_manager: "npm"
    test_framework: "vitest"
    linter: "eslint"
    formatter: "prettier"
    coverage:
      line: 80
      branch: 70
      function: 90
      statement: 85
      mutation: 80
      path: 60
  - folder: "backend"
    type: "backend"
    subtype: "api"
    language: "python"
    runtime: "3.12"
    package_manager: "poetry"
    test_framework: "pytest"
    linter: "ruff"
    formatter: "ruff"
    coverage:
      line: 80
      branch: 70
      function: 90
      statement: 85
      mutation: 80
      path: 60
```

### 5.3 Interactive Flow Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| F1 | Present standard presets (frontend, backend) and custom option | Must |
| F2 | For custom folders, prompt for folder path (supports hierarchical paths) | Must |
| F3 | For custom folders, prompt for plain-language description | Must |
| F4 | Loop until user signals no more folders | Must |
| F5 | Create any folders in the path that do not exist | Must |
| F6 | Apply language-specific defaults based on type/subtype | Should |
| F7 | Allow editing folder configuration before saving | Should |

### 5.4 Validation Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| V1 | Validate folder path format (no invalid characters) | Must |
| V2 | Prevent duplicate folder paths | Must |
| V3 | Ensure at least one folder is configured | Must |

---

## 6. Acceptance Criteria

### 6.1 Core Functionality

- [ ] User can select from standard presets (frontend, backend) or custom
- [ ] User can add multiple folders in one session
- [ ] User can create hierarchical folders (e.g., `services/auth/api`)
- [ ] Each folder has its own language configuration
- [ ] Each folder has its own tool configuration (package manager, test framework, linter, formatter)
- [ ] Configuration is persisted to `.promptosaurus.yaml`

### 6.2 User Experience

- [ ] User sees clear instructions at each step
- [ ] User can exit the setup at any point
- [ ] User can add more folders after initial setup
- [ ] Standard presets auto-configure appropriate defaults

### 6.3 Edge Cases

- [ ] Empty folder path is rejected
- [ ] Duplicate folder paths are rejected
- [ ] Invalid characters in folder path are rejected
- [ ] Setup works correctly with zero folders (cancelled)

---

## 7. Success Metrics

### 7.1 Quantifiable Metrics

| Metric | Target |
|--------|--------|
| CLI init completion rate for monorepo setup | > 90% |
| Average time to complete monorepo setup | < 2 minutes |
| Number of configuration errors during setup | 0 |

### 7.2 Qualitative Metrics

- Users can successfully configure a multi-language monorepo without documentation
- Configuration correctly generates AI assistant prompts for each folder
- The feature is discoverable in the CLI

---

## 8. Timeline

- **Target Date:** TBD
- **Milestones:**
  1. PRD/ARD Approval: Day 1
  2. Folder-aware config implementation: Day 2-3
  3. Interactive setup flow: Day 4-5
  4. Tests and validation: Day 6
  5. Integration testing: Day 7

---

## 9. Open Questions

1. Should there be a maximum number of folders? (Suggestion: No limit) - **ANSWERED: No limit**
2. Should folder paths be relative to project root only? (Yes, for simplicity) - **ANSWERED: Yes, root only**
3. Should we support removing/editing folders after initial setup? (Deferred to future) - **ANSWERED: Deferred to future**
