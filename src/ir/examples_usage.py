"""Usage examples for parsers and loaders.

This module demonstrates how to use the parser and loader infrastructure.
These are examples, not tests - see tests/ for actual test coverage.
"""

from src.ir.parsers import YAMLParser, MarkdownParser
from src.ir.loaders import SkillLoader, WorkflowLoader, ComponentLoader
from src.ir.models import Skill, Workflow


def example_yaml_parser():
    """Example: Parse YAML frontmatter from markdown content."""
    parser = YAMLParser()

    # Example markdown content with YAML frontmatter
    markdown_content = """---
name: my-skill
description: Performs analysis
tools_needed: [analyzer, validator]
---
# My Skill

This is the markdown content.
"""

    # Parse the YAML frontmatter
    metadata = parser.parse(markdown_content)
    print("YAML Parser Example:")
    print(f"  name: {metadata['name']}")
    print(f"  description: {metadata['description']}")
    print(f"  tools_needed: {metadata['tools_needed']}")
    print()


def example_markdown_parser():
    """Example: Parse markdown sections by header."""
    parser = MarkdownParser()

    markdown_content = """
## Overview
This is the overview section.

## Instructions
1. Do this first
2. Then do that

## Examples
Here are some examples.
"""

    sections = parser.parse(markdown_content)
    print("Markdown Parser Example:")
    for section_name, content in sections.items():
        print(f"  Section: {section_name}")
        print(f"    Content: {content[:50]}...")
    print()


def example_skill_loader(temp_skill_file: str | None = None):
    """Example: Load a Skill model from a file."""
    # Note: This requires an actual skill file to exist.
    # In real usage, you would have files like:
    #   src/skills/analysis.md
    #   src/skills/validation.md
    # with content like:
    # ---
    # name: analysis
    # description: Analyze input data
    # tools_needed: [analyzer]
    # ---
    # ## Instructions
    # Detailed analysis instructions.

    loader = SkillLoader()
    print("SkillLoader Example:")
    print("  Would load: src/skills/analysis.md")
    print("  Returns: Skill(name, description, instructions, tools_needed)")
    print()


def example_workflow_loader(temp_workflow_file: str | None = None):
    """Example: Load a Workflow model from a file."""
    # Note: This requires an actual workflow file to exist.
    # In real usage, you would have files like:
    #   src/workflows/analysis_flow.md
    # with content like:
    # ---
    # name: analysis_flow
    # description: Multi-step analysis workflow
    # steps:
    #   - Gather input
    #   - Analyze data
    #   - Generate report
    # ---

    loader = WorkflowLoader()
    print("WorkflowLoader Example:")
    print("  Would load: src/workflows/analysis_flow.md")
    print("  Returns: Workflow(name, description, steps)")
    print()


def example_component_loader(temp_directory: str | None = None):
    """Example: Load all component files from a directory."""
    # Note: This requires an actual directory structure:
    # src/prompts/my-agent/
    #   ├── prompt.md (required)
    #   ├── skills.md (optional)
    #   └── workflow.md (optional)

    loader = ComponentLoader()
    print("ComponentLoader Example:")
    print("  Would load from: src/prompts/my-agent/")
    print("  Returns: ComponentBundle or dict")
    print("    - prompt_content: loaded prompt data")
    print("    - skills_content: loaded skills data (optional)")
    print("    - workflow_content: loaded workflow data (optional)")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Parser and Loader Usage Examples")
    print("=" * 60)
    print()

    example_yaml_parser()
    example_markdown_parser()
    example_skill_loader()
    example_workflow_loader()
    example_component_loader()

    print("=" * 60)
    print("Note: Full examples require actual files to exist.")
    print("See tests/ for comprehensive test coverage.")
    print("=" * 60)
