"""Schema validator for agents, workflows, and skills."""

from pathlib import Path


class SchemaValidator:
    """Validates document schema and structure."""

    AGENT_REQUIRED_SECTIONS = ["Purpose", "Responsibilities", "Capabilities", "Subagent"]

    SUBAGENT_REQUIRED_SECTIONS = [
        "Purpose",
        "Key Concepts",
        "Example",
        "Patterns",
        "Best Practices",
    ]

    WORKFLOW_REQUIRED_SECTIONS = ["Purpose", "Steps", "Success Criteria"]

    SKILL_REQUIRED_SECTIONS = ["Purpose", "Core Concepts", "Example", "Best Practices"]

    def __init__(self, project_root: Path):
        """Initialize validator."""
        self.project_root = project_root
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate_agent(self, file_path: Path) -> bool:
        """Validate agent file."""
        with open(file_path) as f:
            content = f.read()

        missing = [s for s in self.AGENT_REQUIRED_SECTIONS if s not in content]
        if missing:
            self.errors.append(f"{file_path}: Missing sections: {missing}")
            return False

        if len(content.strip().split("\n")) < 20:
            self.warnings.append(f"{file_path}: Too short (<20 lines)")

        return True

    def validate_subagent(self, file_path: Path) -> bool:
        """Validate subagent file."""
        with open(file_path) as f:
            content = f.read()

        # Check for minimal vs verbose
        lines = len(content.strip().split("\n"))
        if "minimal" in str(file_path) and lines < 40:
            self.warnings.append(f"{file_path}: Minimal variant too short (<40 lines)")
        elif "verbose" in str(file_path) and lines < 200:
            self.warnings.append(f"{file_path}: Verbose variant too short (<200 lines)")

        return True

    def validate_workflow(self, file_path: Path) -> bool:
        """Validate workflow file."""
        with open(file_path) as f:
            content = f.read()

        missing = [s for s in self.WORKFLOW_REQUIRED_SECTIONS if s not in content]
        if missing:
            self.errors.append(f"{file_path}: Missing sections: {missing}")
            return False

        if len(content.strip().split("\n")) < 50:
            self.warnings.append(f"{file_path}: Too short (<50 lines)")

        return True

    def validate_skill(self, file_path: Path) -> bool:
        """Validate skill file."""
        with open(file_path) as f:
            content = f.read()

        if len(content.strip().split("\n")) < 40:
            self.warnings.append(f"{file_path}: Too short (<40 lines)")

        return True

    def validate_all(self) -> tuple[int, int]:
        """Validate all files."""
        agents_dir = self.project_root / "promptosaurus" / "agents"
        workflows_dir = self.project_root / "promptosaurus" / "workflows"
        skills_dir = self.project_root / "promptosaurus" / "skills"

        validated = 0
        failed = 0

        # Validate agents
        for agent_file in agents_dir.glob("*/prompt.md"):
            if self.validate_agent(agent_file):
                validated += 1
            else:
                failed += 1

        # Validate subagents
        for subagent_file in agents_dir.glob("*/subagents/*/*/prompt.md"):
            if self.validate_subagent(subagent_file):
                validated += 1
            else:
                failed += 1

        # Validate workflows
        for workflow_file in workflows_dir.glob("*/*/workflow.md"):
            if self.validate_workflow(workflow_file):
                validated += 1
            else:
                failed += 1

        # Validate skills
        for skill_file in skills_dir.glob("*/*/SKILL.md"):
            if self.validate_skill(skill_file):
                validated += 1
            else:
                failed += 1

        return validated, failed

    def report(self) -> str:
        """Generate validation report."""
        lines = ["=== Validation Report ==="]

        if self.errors:
            lines.append(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors[:10]:
                lines.append(f"  - {error}")
        else:
            lines.append("\n✅ No errors")

        if self.warnings:
            lines.append(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:5]:
                lines.append(f"  - {warning}")

        return "\n".join(lines)


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    validator = SchemaValidator(project_root)
    validated, failed = validator.validate_all()
    print(validator.report())
    print(f"\nValidated: {validated}, Failed: {failed}")
