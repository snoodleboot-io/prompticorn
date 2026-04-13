"""Content validator for all Phase 1 agents, workflows, and skills."""

from pathlib import Path


class ContentValidator:
    """Validates content quality and consistency across Phase 1 deliverables."""

    def __init__(self, project_root: Path):
        """Initialize validator."""
        self.project_root = project_root
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.agents_dir = project_root / "promptosaurus" / "agents"
        self.workflows_dir = project_root / "promptosaurus" / "workflows"
        self.skills_dir = project_root / "promptosaurus" / "skills"

    def validate_all(self) -> tuple[int, int]:
        """Run all validations."""
        self.errors = []
        self.warnings = []

        # Validate Phase 1 agents
        self._validate_agents(["data", "observability", "incident"])

        # Validate Phase 1 workflows
        phase1_workflows = [
            "data-pipeline",
            "data-quality",
            "schema-migration",
            "observability",
            "slo-sli",
            "capacity-planning",
            "incident-response",
            "postmortem",
        ]
        self._validate_workflows(phase1_workflows)

        return len(self.errors), len(self.warnings)

    def _validate_agents(self, agent_names: list[str]) -> None:
        """Validate agent files."""
        for agent_name in agent_names:
            agent_file = self.agents_dir / agent_name / "prompt.md"
            if not agent_file.exists():
                self.errors.append(f"Agent not found: {agent_name}")
                continue

            with open(agent_file) as f:
                content = f.read()

            # Check for required sections
            required = ["Purpose", "Responsibilities", "Capabilities", "subagent"]
            for section in required:
                if section not in content and section.lower() not in content.lower():
                    self.warnings.append(f"{agent_name}: Missing '{section}' section")

            # Check minimum length
            lines = len(content.strip().split("\n"))
            if lines < 20:
                self.errors.append(f"{agent_name}: Too short ({lines} lines, min 20)")

    def _validate_workflows(self, workflow_names: list[str]) -> None:
        """Validate workflow files."""
        for workflow_name in workflow_names:
            workflow_dir = self.workflows_dir / workflow_name
            if not workflow_dir.exists():
                self.errors.append(f"Workflow not found: {workflow_name}")
                continue

            # Check both variants exist
            for variant in ["minimal", "verbose"]:
                variant_file = workflow_dir / variant / "prompt.md"
                if not variant_file.exists():
                    self.errors.append(f"{workflow_name}: Missing {variant} variant")
                    continue

                with open(variant_file) as f:
                    content = f.read()

                # Check minimum length
                lines = len(content.strip().split("\n"))
                min_lines = 20 if variant == "minimal" else 100
                if lines < min_lines:
                    self.warnings.append(
                        f"{workflow_name}/{variant}: Too short ({lines} lines, min {min_lines})"
                    )

                # Check for purpose
                if "purpose" not in content.lower():
                    self.warnings.append(f"{workflow_name}/{variant}: Missing purpose section")

    def validate_subagent_coverage(self) -> dict[str, set[str]]:
        """Validate that all subagents exist."""
        expected = {
            "data": ["pipeline", "warehouse", "quality", "governance", "streaming"],
            "observability": ["metrics", "logging", "tracing", "alerting", "dashboards"],
            "incident": ["triage", "postmortem", "runbook", "oncall"],
        }

        missing = {}
        for agent, subagents in expected.items():
            missing_list = []
            for subagent in subagents:
                subagent_dir = self.agents_dir / agent / "subagents" / subagent
                if not subagent_dir.exists():
                    missing_list.append(subagent)
                    self.errors.append(f"Missing subagent: {agent}/{subagent}")
                else:
                    # Check both variants
                    for variant in ["minimal", "verbose"]:
                        variant_file = subagent_dir / variant / "prompt.md"
                        if not variant_file.exists():
                            self.errors.append(f"Missing variant: {agent}/{subagent}/{variant}")

            if missing_list:
                missing[agent] = set(missing_list)

        return missing

    def report(self) -> str:
        """Generate validation report."""
        lines = [
            "=" * 60,
            "Content Validation Report",
            "=" * 60,
            f"\nErrors: {len(self.errors)}",
            f"Warnings: {len(self.warnings)}\n",
        ]

        if self.errors:
            lines.append("ERRORS:")
            for error in self.errors:
                lines.append(f"  ✗ {error}")

        if self.warnings:
            lines.append("\nWARNINGS:")
            for warning in self.warnings:
                lines.append(f"  ⚠ {warning}")

        lines.extend(
            ["\n" + "=" * 60, f"Status: {'✓ PASS' if not self.errors else '✗ FAIL'}", "=" * 60]
        )

        return "\n".join(lines)
