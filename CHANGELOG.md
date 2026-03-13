# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Multi-Language Monorepo Support**: New configuration option for monorepo projects with multiple language-specific folders
  - Interactive CLI flow with standard presets (backend: api/library/worker/cli, frontend: ui/library/e2e)
  - Custom folder support with hierarchical paths (e.g., `services/auth/api`)
  - Folder-aware configuration (`spec` becomes a list for multi-language-monorepo)
  - Auto-creation of folders during initialization
  - Language-specific defaults for Python, TypeScript, JavaScript, Go, Java, Rust, C#

### Changed

- Renamed `multi-language-folder` to `multi-language-monorepo` throughout codebase
- Config handler now uses SpecHandler abstraction for cleaner language-specific defaults

### Fixed

- DRY violation: Removed duplicate constants in spec_handler.py (now imports from folder_spec.py)

### Documentation

- Added PRD: `docs/prd/multi-language-monorepo-support.md`
- Added ARD: `docs/ard/multi-language-monorepo-support.md`

## [1.0.0] - 2024-01-01

### Added

- Initial release of Promptosaurus
- Support for single-language repositories
- CLI commands: init, list, validate
- Builder support for: Kilo CLI, Kilo IDE, Cline, Cursor, Copilot
- Question pipeline system for interactive configuration
- Mode system for different agent types (architect, code, test, etc.)
