# Migration Guide for Promptosaurus

Guide for migrating between Promptosaurus versions.

## Overview

### What This Guide Covers
This migration guide helps users upgrade Promptosaurus between versions, covering:
- Configuration file updates
- Agent and workflow format changes
- Builder output modifications
- Deprecation notices and removal schedules
- Validation and testing procedures

### When You Need It
Use this guide when:
- Upgrading from one Promptosaurus version to another
- Encountering deprecation warnings in your setup
- Planning version upgrades for production environments
- Troubleshooting compatibility issues after an update

### Backward Compatibility Policy
Promptosaurus follows [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH):
- **PATCH** releases (e.g., 0.1.1): Backward-compatible bug fixes
- **MINOR** releases (e.g., 0.2.0): Backward-compatible new features
- **MAJOR** releases (e.g., 1.0.0): May contain breaking changes

For version 0.x.y (pre-1.0):
- MINOR versions may introduce breaking changes as we refine the API
- We will document all breaking changes in advance
- Upgrade paths will be provided for all changes
- Deprecations will be announced at least one MINOR version before removal

## Breaking Changes (Future)

### Placeholder for Future Breaking Changes
This section will be populated as breaking changes are introduced in future releases.

### How Breaking Changes Will Be Communicated
1. **Advance Notice**: Breaking changes announced in release notes at least one MINOR version prior
2. **Deprecation Warnings**: Runtime warnings when using deprecated features
3. **Migration Documentation**: Detailed guides in this MIGRATION_GUIDE.md
4. **Changelog Entries**: Specific breaking changes listed in CHANGELOG.md
5. **Community Notifications**: Announcements via GitHub releases and community channels

### Version Numbering
Promptosaurus uses Semantic Versioning:
- Format: MAJOR.MINOR.PATCH
- MAJOR: Incompatible API changes
- MINOR: Backward-compatible functionality
- PATCH: Backward-compatible bug fixes
- Pre-release tags (e.g., 0.1.0-alpha.1) may be used for experimental features

## Current Version (0.1.0)

### Initial Release Notes
Promptosaurus 0.1.0 is the initial release featuring:
- Core agent framework with 9 specialized agents
- 49 workflows for common development tasks
- 58 specialized skills for domain expertise
- Integration templates for Kilo, Cline, Cursor, and Copilot
- Configuration system via `.promptosaurus.yaml`
- Session management for context persistence
- Comprehensive test suite (98.3% coverage)

### Known Limitations
As an early release (0.1.0), users should be aware of:
1. **Limited IDE Integrations**: Only Kilo, Cline, Cursor, and Copilot configurations provided
2. **Configuration Schema**: May evolve in future 0.x releases
3. **Agent Format**: Prompt instruction formats may be refined
4. **Workflow Execution**: Verbose/minimal variants may see adjustments
5. **Documentation Coverage**: Some advanced features may have limited documentation

### Experimental Features
Features marked as experimental in 0.1.0:
- None - all features in 0.1.0 are considered stable for this early release
- Future experimental features will be clearly marked in documentation
- Experimental features may change without following standard deprecation policy

## Migration Checklist Template

### Generic Migration Steps
Follow these steps for any Promptosaurus version upgrade:

1. **Review Release Notes**
   - Read CHANGELOG.md for target version
   - Check for breaking changes and deprecations
   - Note any required action items

2. **Backup Current Setup**
   - Backup `.promptosaurus/` directory
   - Backup custom agents/workflows/skills
   - Backup project-specific configurations

3. **Update Promptosaurus**
   - Update via your preferred method (git pull, package manager, etc.)
   - Verify version with `promptosaurus --version` (if available)
   - Or check git tag/commit for manual installations

4. **Apply Configuration Updates**
   - Check for `.promptosaurus.yaml` schema changes
   - Update configuration as needed
   - Validate configuration syntax

5. **Test Custom Content**
   - Verify custom agents/workflows/skills still function
   - Update any deprecated syntax or formats
   - Run your standard test suite

6. **Validate Integration**
   - Test IDE integration (Kilo/Cline/Cursor/Copilot)
   - Verify agent activation and context loading
   - Check session management functionality

### Backup Recommendations
Before upgrading:
```bash
# Backup .promptosaurus directory
cp -r .promptosaurus .promptosaurus.backup-$(date +%Y%m%d-%H%M%S)

# Backup custom content (if stored separately)
# Example: cp -r custom_agents/ custom_agents.backup-$(date +%Y%m%d-%H%M%S)

# Document current version
git log -1 --oneline > version-backup-$(date +%Y%m%d-%H%M%S).txt
# Or for non-git installations:
promptosaurus --version > version-backup-$(date +%Y%m%d-%H%M%S).txt
```

### Validation Steps
After upgrading:
1. **Configuration Validation**
   - Run: `promptosaurus config validate` (if available)
   - Or manually verify `.promptosaurus.yaml` against schema

2. **Functionality Testing**
   - Test agent activation: Try switching between agents
   - Test workflow execution: Run a simple workflow
   - Test skill loading: Verify skills are accessible

3. **Integration Testing**
   - Verify IDE plugin loads correctly
   - Check session file creation in `.promptosaurus/sessions/`
   - Test context persistence across mode switches

4. **Regression Testing**
   - Run your project's standard test suite
   - Verify custom extensions still work
   - Check that no new warnings/errors appear

### Rollback Procedures
If issues occur after upgrade:
1. **Identify the Problem**
   - Note error messages and symptoms
   - Check if issue is in your configuration or Promptosaurus core
   - Determine if rollback is necessary or if fix is available

2. **Restore Backup**
   ```bash
   # Remove current installation
   rm -rf .promptosaurus
   
   # Restore from backup
   mv .promptosaurus.backup-YYYYMMDD-HHMMSS .promptosaurus
   
   # Restore custom content if needed
   # mv custom_agents.backup-YYYYMMDD-HHMMSS custom_agents
   ```

3. **Verify Rollback**
   - Confirm previous version is restored
   - Verify functionality is restored
   - Document issue for future reference

## Configuration File Changes

### How to Detect Config Changes Needed
1. **Release Notes**: Check CHANGELOG.md for configuration changes
2. **Startup Warnings**: Promptosaurus may warn about deprecated settings
3. **Schema Validation**: Use validation tools if available
4. **Documentation Diff**: Compare config examples between versions

### How to Update `.promptosaurus.yaml`
1. **Backup Current Config**
   ```bash
   cp .promptosaurus.yaml .promptosaurus.yaml.backup-$(date +%Y%m%d-%H%M%S)
   ```

2. **Review Schema Changes**
   - Check for new/removed/renamed fields
   - Note changes in allowed values or formats
   - Identify deprecated settings

3. **Apply Updates**
   - Edit `.promptosaurus.yaml` with required changes
   - Maintain customizations in active sections
   - Preserve comments and structure where possible

4. **Validate Changes**
   - Start Promptosaurus and check for errors
   - Verify all features work as expected
   - Compare behavior against backup if needed

### Config Schema Versioning
The `.promptosaurus.yaml` file includes an implicit schema version:
- Current schema version for 0.1.0: `version: '1.0'` (top-level field)
- Schema changes will be indicated by updating this version number
- Backward compatibility will be maintained within same major schema version
- Migration guides will detail schema version upgrade paths

Example schema evolution:
- 0.1.0: `version: '1.0'` (initial release)
- 0.2.0: `version: '1.1'` (backward-compatible additions)
- 0.3.0: `version: '2.0'` (may require migration steps)

## Agent Format Changes

### IR Model Evolution
The Intermediate Representation (IR) model for agents may evolve:
- **Current 0.1.0 IR**: YAML frontmatter + markdown sections
- **Future Changes**: May include typed fields, validation schemas
- **Migration Path**: Automatic conversion tools may be provided
- **Backward Compatibility**: Older formats will be supported with warnings

### Prompt File Format Changes
Agent instruction files (`*.md`) may see format refinements:
- **Current Format**: Markdown with specific section headers
- **Potential Changes**: Standardized section ordering, required fields
- **Deprecation Strategy**: Warnings → Errors → Removal over versions
- **Validation**: Format validators may be introduced

### Skill/Workflow Format Changes
Skills and workflows follow similar formats to agents:
- **Current Structure**: Consistent with agent format conventions
- **Future Evolution**: May adopt more structured formats
- **Migration Approach**: Similar to agent format changes
- **Documentation**: Changes will be documented in respective references

## Builder Output Changes

### Changes to Generated Files
Output from workflows and skills may change:
- **Template Updates**: Jinja2 or other template improvements
- **Format Refinements**: Output structure improvements
- **Configuration Options**: New customization parameters
- **Backward Compatibility**: Existing templates will remain functional

### Tool-Specific Migration Notes
For each supported IDE integration:

#### Kilo
- Configuration lives in `.kilo/` directory
- Watch for changes to rule file locations or formats
- Mode-specific rule updates may occur

#### Cline
- May use different configuration mechanisms
- Check for updates to custom instruction formats

#### Cursor
- Rule placement and naming conventions may evolve
- Verify compatibility after updates

#### Copilot
- May adjust to Copilot's evolving extension model
- Watch for changes to activation triggers

## Getting Help

### Where to Report Issues
1. **GitHub Issues**: https://github.com/your-org/promptosaurus/issues
   - Use bug report template for reproducible issues
   - Use feature request template for new functionality
   - Include version, environment, and reproduction steps

2. **Configuration Problems**
   - Check `.promptosaurus/sessions/` for context
   - Review session files for recent actions
   - Enable verbose logging if available

3. **Integration Issues**
   - Verify IDE plugin installation and activation
   - Check IDE logs for Promptosaurus-related errors
   - Test with minimal configuration to isolate problems

### Community Resources
1. **Documentation**
   - Main docs: `/docs/` directory in repository
   - API reference: Generated documentation
   - Tutorials: Look in `/docs/developer-guide/` and `/docs/user-guide/`

2. **Examples**
   - See `/examples/` directory for usage patterns
   - Check `/promptosaurus/examples/` for runnable examples

3. **Community Discussions**
   - GitHub Discussions: For questions and idea sharing
   - Stack Overflow: Tag `promptosaurus` for technical questions

### Support Channels
1. **Official Support**
   - GitHub Issues: Primary channel for bug reports and features
   - Documentation: Self-help for common questions

2. **Community Support**
   - GitHub Discussions: Peer-to-peer help and suggestions
   - Example repositories: See how others use Promptosaurus

3. **Enterprise Support**
   - For commercial support options, check the repository
   - Contact maintainers for SLA-based support inquiries

---

*This migration guide is forward-looking for Promptosaurus 0.1.0 and will be updated as new versions are released.*
*Last updated: 2026-04-13*
