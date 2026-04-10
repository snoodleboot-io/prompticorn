#!/usr/bin/env python3
"""
Extract workflows to top-level workflows/ directory.

Workflows are shared resources (like skills) that can be used by multiple agents.
They should not be buried in agent/subagent directories.

Structure:
    workflows/
    ├── feature-workflow/
    │   ├── minimal/workflow.md
    │   └── verbose/workflow.md
    └── data-model-workflow/
        ├── minimal/workflow.md
        └── verbose/workflow.md
"""

import shutil
from pathlib import Path


def extract_workflows():
    """Extract all workflow files to top-level workflows/ directory."""
    base_dir = Path("promptosaurus")
    agents_dir = base_dir / "agents"
    workflows_dir = base_dir / "workflows"

    # Create top-level workflows directory
    workflows_dir.mkdir(exist_ok=True)
    print(f"✓ Created {workflows_dir}")

    # Find all workflow.md files in agent directories
    workflow_files = list(agents_dir.rglob("workflow.md"))
    print(f"\n📄 Found {len(workflow_files)} workflow files\n")

    workflows_extracted = {}

    for workflow_file in workflow_files:
        # Parse workflow file to get name
        content = workflow_file.read_text()

        # Extract workflow name from frontmatter
        workflow_name = extract_workflow_name(content)

        if not workflow_name:
            print(f"  ⚠️  Skipping {workflow_file} - no name in frontmatter")
            continue

        # Determine variant (minimal or verbose)
        if "minimal" in workflow_file.parts:
            variant = "minimal"
        elif "verbose" in workflow_file.parts:
            variant = "verbose"
        else:
            print(f"  ⚠️  Skipping {workflow_file} - can't determine variant")
            continue

        # Create target directory
        target_dir = workflows_dir / workflow_name / variant
        target_dir.mkdir(parents=True, exist_ok=True)

        # Copy workflow file
        target_file = target_dir / "workflow.md"
        shutil.copy2(workflow_file, target_file)

        # Track for reporting
        if workflow_name not in workflows_extracted:
            workflows_extracted[workflow_name] = []
        workflows_extracted[workflow_name].append(variant)

        print(f"  ✓ {workflow_name}/{variant}/workflow.md")

    # Remove workflow files from agent directories
    print(f"\n🗑️  Removing workflow files from agent directories\n")
    for workflow_file in workflow_files:
        workflow_file.unlink()
        print(f"  ✓ Removed {workflow_file}")

    # Summary
    print(f"\n✅ Extraction complete!")
    print(f"\nWorkflows extracted:")
    for workflow_name, variants in sorted(workflows_extracted.items()):
        print(f"  - {workflow_name}: {', '.join(sorted(variants))}")

    print(f"\nTotal: {len(workflows_extracted)} workflows")


def extract_workflow_name(content: str) -> str | None:
    """Extract workflow name from YAML frontmatter."""
    import re

    # Look for name: in frontmatter
    match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip().strip('"').strip("'")

    return None


if __name__ == "__main__":
    extract_workflows()
