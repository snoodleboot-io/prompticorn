"""Coverage analyzer for Phase 1 content."""

from pathlib import Path


class CoverageAnalyzer:
    """Analyzes coverage of Phase 1 agents, subagents, workflows, and skills."""

    def __init__(self, project_root: Path):
        """Initialize analyzer."""
        self.project_root = project_root
        self.agents_dir = project_root / "promptosaurus" / "agents"
        self.workflows_dir = project_root / "promptosaurus" / "workflows"
        self.skills_dir = project_root / "promptosaurus" / "skills"

    def analyze_all(self) -> dict[str, dict]:
        """Analyze coverage of all Phase 1 content."""
        return {
            "agents": self._analyze_agents(),
            "subagents": self._analyze_subagents(),
            "workflows": self._analyze_workflows(),
            "skills": self._analyze_skills(),
        }

    def _analyze_agents(self) -> dict[str, int]:
        """Analyze agent coverage."""
        phase1_agents = ["data", "observability", "incident"]
        coverage = {}

        for agent in phase1_agents:
            agent_file = self.agents_dir / agent / "prompt.md"
            coverage[agent] = 1 if agent_file.exists() else 0

        return coverage

    def _analyze_subagents(self) -> dict[str, dict[str, int]]:
        """Analyze subagent coverage."""
        expected = {
            "data": ["pipeline", "warehouse", "quality", "governance", "streaming"],
            "observability": ["metrics", "logging", "tracing", "alerting", "dashboards"],
            "incident": ["triage", "postmortem", "runbook", "oncall"],
        }

        coverage = {}
        for agent, subagents in expected.items():
            coverage[agent] = {}
            for subagent in subagents:
                subagent_dir = self.agents_dir / agent / "subagents" / subagent
                minimal = subagent_dir / "minimal" / "prompt.md"
                verbose = subagent_dir / "verbose" / "prompt.md"

                if minimal.exists() and verbose.exists():
                    coverage[agent][subagent] = 2  # Both variants
                elif minimal.exists() or verbose.exists():
                    coverage[agent][subagent] = 1  # One variant
                else:
                    coverage[agent][subagent] = 0  # Missing

        return coverage

    def _analyze_workflows(self) -> dict[str, int]:
        """Analyze workflow coverage."""
        phase1_workflows = {
            "data-pipeline": 2,
            "data-quality": 2,
            "schema-migration": 2,
            "observability": 2,
            "slo-sli": 2,
            "capacity-planning": 2,
            "incident-response": 2,
            "postmortem": 2,
        }

        coverage = {}
        for workflow_name, _expected_variants in phase1_workflows.items():
            workflow_dir = self.workflows_dir / workflow_name
            found_variants = 0

            for variant in ["minimal", "verbose"]:
                if (workflow_dir / variant / "prompt.md").exists():
                    found_variants += 1

            coverage[workflow_name] = found_variants

        return coverage

    def _analyze_skills(self) -> dict[str, int]:
        """Analyze skill coverage."""
        phase1_skills = [
            "sql-optimization",
            "dimensional-modeling",
            "data-partitioning",
            "idempotency-patterns",
            "slowly-changing-dimensions",
            "prometheus-query-patterns",
            "slo-sli-definition",
            "distributed-tracing-instrumentation",
            "grafana-dashboard-design",
            "incident-timeline-creation",
            "root-cause-five-whys",
        ]

        coverage = {}
        for skill in phase1_skills:
            skill_dir = self.skills_dir / skill
            minimal = skill_dir / "minimal" / "prompt.md"
            verbose = skill_dir / "verbose" / "prompt.md"

            if minimal.exists() and verbose.exists():
                coverage[skill] = 2
            elif minimal.exists() or verbose.exists():
                coverage[skill] = 1
            else:
                coverage[skill] = 0

        return coverage

    def calculate_coverage_percentage(self, coverage_data: dict) -> dict[str, float]:
        """Calculate coverage percentages."""
        percentages = {}

        # Agents: 3 expected
        agents_found = sum(1 for v in coverage_data["agents"].values() if v > 0)
        percentages["agents"] = (agents_found / 3) * 100

        # Subagents: 14 expected (5 + 5 + 4)
        subagent_count = sum(len(subs) for subs in coverage_data["subagents"].values())
        subagent_found = sum(
            1
            for agent_subs in coverage_data["subagents"].values()
            for count in agent_subs.values()
            if count > 0
        )
        percentages["subagents"] = (subagent_found / 14) * 100 if subagent_count > 0 else 0

        # Workflows: 8 expected
        workflow_found = sum(1 for v in coverage_data["workflows"].values() if v == 2)
        percentages["workflows"] = (workflow_found / 8) * 100

        # Skills: 11 expected
        skill_found = sum(1 for v in coverage_data["skills"].values() if v > 0)
        percentages["skills"] = (skill_found / 11) * 100

        return percentages

    def report(self) -> str:
        """Generate coverage report."""
        coverage = self.analyze_all()
        percentages = self.calculate_coverage_percentage(coverage)

        lines = ["=" * 60, "Phase 1 Coverage Analysis Report", "=" * 60, ""]

        # Agents
        lines.append(f"AGENTS: {percentages['agents']:.1f}%")
        for agent, exists in coverage["agents"].items():
            status = "✓" if exists else "✗"
            lines.append(f"  {status} {agent}")

        # Subagents
        lines.append(f"\nSUBAGENTS: {percentages['subagents']:.1f}%")
        for agent, subagents in coverage["subagents"].items():
            lines.append(f"  {agent.upper()}:")
            for subagent, count in subagents.items():
                if count == 2:
                    status = "✓✓"  # Both variants
                elif count == 1:
                    status = "⚠"  # One variant
                else:
                    status = "✗"  # Missing
                lines.append(f"    {status} {subagent}")

        # Workflows
        lines.append(f"\nWORKFLOWS: {percentages['workflows']:.1f}%")
        for workflow, count in coverage["workflows"].items():
            if count == 2:
                status = "✓✓"
            elif count == 1:
                status = "⚠"
            else:
                status = "✗"
            lines.append(f"  {status} {workflow}")

        # Skills
        lines.append(f"\nSKILLS: {percentages['skills']:.1f}%")
        for skill, count in coverage["skills"].items():
            if count == 2:
                status = "✓✓"
            elif count == 1:
                status = "⚠"
            else:
                status = "✗"
            lines.append(f"  {status} {skill}")

        # Summary
        lines.extend(
            [
                "\n" + "=" * 60,
                "SUMMARY",
                f"  Agents:     {percentages['agents']:.1f}%",
                f"  Subagents:  {percentages['subagents']:.1f}%",
                f"  Workflows:  {percentages['workflows']:.1f}%",
                f"  Skills:     {percentages['skills']:.1f}%",
                f"  OVERALL:    {sum(percentages.values()) / 4:.1f}%",
                "=" * 60,
            ]
        )

        return "\n".join(lines)
