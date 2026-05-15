"""Consistency checker for Phase 1 deliverables."""

from pathlib import Path


class ConsistencyChecker:
    """Checks consistency across agents, workflows, and subagents."""

    def __init__(self, project_root: Path):
        """Initialize checker."""
        self.project_root = project_root
        self.agents_dir = project_root / "prompticorn" / "agents"
        self.workflows_dir = project_root / "prompticorn" / "workflows"
        self.skills_dir = project_root / "prompticorn" / "skills"
        self.issues: list[str] = []

    def check_all(self) -> tuple[int, list[str]]:
        """Run all consistency checks."""
        self.issues = []

        self._check_variant_consistency()
        self._check_subagent_references()
        self._check_workflow_agent_alignment()
        self._check_naming_conventions()

        return len(self.issues), self.issues

    def _check_variant_consistency(self) -> None:
        """Check that all files have both minimal and verbose variants."""
        # Check subagents
        for agent_dir in self.agents_dir.iterdir():
            if agent_dir.is_dir() and agent_dir.name not in ["__pycache__", "core"]:
                subagents_dir = agent_dir / "subagents"
                if subagents_dir.exists():
                    for subagent_dir in subagents_dir.iterdir():
                        if subagent_dir.is_dir():
                            minimal = subagent_dir / "minimal" / "prompt.md"
                            verbose = subagent_dir / "verbose" / "prompt.md"

                            if minimal.exists() and not verbose.exists():
                                self.issues.append(
                                    f"Subagent {subagent_dir.name}: Has minimal but missing verbose"
                                )
                            elif verbose.exists() and not minimal.exists():
                                self.issues.append(
                                    f"Subagent {subagent_dir.name}: Has verbose but missing minimal"
                                )

        # Check workflows
        for workflow_dir in self.workflows_dir.iterdir():
            if workflow_dir.is_dir() and workflow_dir.name.endswith(""):
                minimal = workflow_dir / "minimal" / "prompt.md"
                verbose = workflow_dir / "verbose" / "prompt.md"

                if minimal.exists() and not verbose.exists():
                    self.issues.append(
                        f"Workflow {workflow_dir.name}: Has minimal but missing verbose"
                    )
                elif verbose.exists() and not minimal.exists():
                    self.issues.append(
                        f"Workflow {workflow_dir.name}: Has verbose but missing minimal"
                    )

    def _check_subagent_references(self) -> None:
        """Check that agents reference their subagents."""
        agent_names = {
            "data": ["pipeline", "warehouse", "quality", "governance", "streaming"],
            "observability": ["metrics", "logging", "tracing", "alerting", "dashboards"],
            "incident": ["triage", "postmortem", "runbook", "oncall"],
        }

        for agent_name, expected_subagents in agent_names.items():
            agent_file = self.agents_dir / agent_name / "prompt.md"
            if agent_file.exists():
                with open(agent_file) as f:
                    content = f.read().lower()

                for subagent in expected_subagents:
                    if subagent.lower() not in content:
                        self.issues.append(
                            f"Agent {agent_name}: Doesn't reference subagent {subagent}"
                        )

    def _check_workflow_agent_alignment(self) -> None:
        """Check that workflows align with agents."""
        alignments = {
            "data-pipeline": "data",
            "data-quality": "data",
            "schema-migration": "data",
            "observability": "observability",
            "slo-sli": "observability",
            "capacity-planning": "observability",
            "incident-response": "incident",
            "postmortem": "incident",
        }

        for workflow_name, agent_type in alignments.items():
            workflow_dir = self.workflows_dir / workflow_name
            if workflow_dir.exists():
                minimal_file = workflow_dir / "minimal" / "prompt.md"
                if minimal_file.exists():
                    with open(minimal_file) as f:
                        content = f.read().lower()

                    # Check for agent type reference
                    if agent_type.lower() not in content:
                        self.issues.append(
                            f"Workflow {workflow_name}: Doesn't reference {agent_type} agent"
                        )

    def _check_naming_conventions(self) -> None:
        """Check naming conventions are followed."""
        # Check agent directories
        for agent_dir in self.agents_dir.iterdir():
            if agent_dir.is_dir() and agent_dir.name not in ["__pycache__", "core"]:
                # Agent names should be lowercase
                if agent_dir.name != agent_dir.name.lower():
                    self.issues.append(f"Agent {agent_dir.name}: Name should be lowercase")

        # Check workflow naming (should be kebab-case with -workflow suffix)
        for workflow_dir in self.workflows_dir.iterdir():
            if workflow_dir.is_dir():
                if not workflow_dir.name.endswith(""):
                    if workflow_dir.name not in ["__pycache__"]:
                        self.issues.append(
                            f"Workflow {workflow_dir.name}: Should end with -workflow"
                        )

    def report(self) -> str:
        """Generate consistency report."""
        lines = [
            "=" * 60,
            "Consistency Check Report",
            "=" * 60,
            f"\nIssues found: {len(self.issues)}\n",
        ]

        if self.issues:
            lines.append("Issues:")
            for issue in self.issues:
                lines.append(f"  ⚠ {issue}")
        else:
            lines.append("✓ All checks passed!")

        lines.extend(
            ["\n" + "=" * 60, f"Status: {'✓ PASS' if not self.issues else '✗ FAIL'}", "=" * 60]
        )

        return "\n".join(lines)
