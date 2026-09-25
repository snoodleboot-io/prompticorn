"""Workflow content for the builders, resolved through the layer stack.

Reads through :func:`read_variant_unit` rather than the installed package
directory. It used to do the latter — ``Path(__file__).parent.parent /
"workflows"`` — which PRO-106 was meant to retire and PRO-117 made wrong: the
Claude, Cursor, Cline and Copilot builders all emit workflows through here, so a
project overriding ``workflows/{name}/{variant}/workflow.md`` got bundled text in
its output while ``prompticorn.lock`` recorded the override's digest under
``layer: project``, and `verify` accepted the pair. (PRO-165)

The variant fallback is unchanged in intent — a workflow authored in one variant
only is still emitted — but it now falls back across the whole stack rather than
within one directory, which is what makes an override of the requested variant
beat a bundled copy of the other one.
"""

from prompticorn.content.content_resolver import read_variant_unit
from prompticorn.content.unit_kind import UnitKind


class WorkflowLoader:
    """Loader for workflow content, resolved from the content layer stack."""

    @staticmethod
    def load_workflow(workflow_name: str, variant: str = "minimal") -> str | None:
        """Load workflow content for a name and variant.

        Args:
            workflow_name: Name of the workflow
            variant: Variant (minimal/verbose), defaults to minimal

        Returns:
            Workflow content as string, or None if no layer carries it
        """
        return read_variant_unit(UnitKind.WORKFLOW, workflow_name, variant)

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
