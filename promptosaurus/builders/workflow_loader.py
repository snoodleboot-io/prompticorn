"""Utility for loading workflow content from the workflows/ directory."""

from pathlib import Path


class WorkflowLoader:
    """Loader for workflow content from bundled workflows directory."""

    @staticmethod
    def load_workflow(workflow_name: str, variant: str = "minimal") -> str | None:
        """Load workflow content from workflows/ directory.

        Args:
            workflow_name: Name of the workflow
            variant: Variant (minimal/verbose), defaults to minimal

        Returns:
            Workflow content as string, or None if not found
        """
        # Get workflows directory (relative to this file)
        # promptosaurus/builders/workflow_loader.py -> promptosaurus/workflows
        workflows_dir = Path(__file__).parent.parent / "workflows"

        workflow_file = workflows_dir / workflow_name / variant / "workflow.md"

        if not workflow_file.exists():
            # Try other variant as fallback
            other_variant = "verbose" if variant == "minimal" else "minimal"
            workflow_file = workflows_dir / workflow_name / other_variant / "workflow.md"

        if workflow_file.exists():
            return workflow_file.read_text(encoding="utf-8")

        return None

    @staticmethod
    def format_workflow_content(workflow_content: str, include_frontmatter: bool = False) -> str:
        """Format workflow content for output.

        Args:
            workflow_content: Raw workflow markdown content
            include_frontmatter: Whether to include YAML frontmatter

        Returns:
            Formatted workflow content
        """
        if not include_frontmatter:
            # Strip YAML frontmatter
            lines = workflow_content.split("\n")
            if lines and lines[0].strip() == "---":
                # Find closing ---
                for i, line in enumerate(lines[1:], start=1):
                    if line.strip() == "---":
                        # Return content after frontmatter
                        return "\n".join(lines[i + 1 :]).strip()

        return workflow_content.strip()
