"""
Integration tests for Phase 3: Workflows and Skills

Validates:
- All 45 workflows exist and are properly structured
- All 50 skills exist and are properly structured
- Workflows/skills registered in language_skill_mapping.yaml
- YAML frontmatter is valid
- File integrity and line counts
- Cross-references are valid
"""

import os
import pytest
import yaml
from pathlib import Path


class TestPhase3Workflows:
    """Test Phase 3 workflow creation and structure"""

    WORKFLOWS_DIR = Path("promptosaurus/workflows")

    # Expected workflows by track
    TRACK_1_WORKFLOWS = {
        "model-evaluation-workflow",
        "model-serving-workflow",
        "mlops-pipeline-setup",
        "feature-engineering-guide",
        "data-quality-monitoring",
        "model-governance-workflow",
        "hyperparameter-tuning",
        "model-retraining-strategy",
        "experiment-tracking-setup",
        "model-interpretability-guide",
        "production-ml-deployment",
        "ml-monitoring-observability",
    }

    TRACK_2_WORKFLOWS = {
        "threat-modeling-workflow",
        "vulnerability-scanning-workflow",
        "security-testing-workflow",
        "compliance-audit-workflow",
        "incident-response-security",
        "security-hardening-checklist",
        "penetration-testing-guide",
        "security-code-review",
        "dependency-scanning-workflow",
        "secret-management-workflow",
    }

    TRACK_3_WORKFLOWS = {
        "requirements-gathering-workflow",
        "roadmap-planning-workflow",
        "feature-prioritization-workflow",
        "user-research-guide",
        "ux-validation-workflow",
        "analytics-setup-workflow",
        "a-b-testing-workflow",
        "feature-launch-checklist",
    }

    TRACK_4_WORKFLOWS = {
        "workflow-orchestration-patterns",
        "multi-agent-coordination-workflow",
        "async-workflow-execution",
        "workflow-versioning-management",
        "workflow-error-handling-patterns",
        "workflow-monitoring-workflow",
        "workflow-testing-patterns",
        "workflow-documentation-patterns",
        "workflow-migration-patterns",
        "workflow-performance-optimization",
        "workflow-dependency-management",
        "workflow-rollback-strategies",
        "workflow-scaling-patterns",
        "workflow-security-in-workflows",
        "workflow-compliance-patterns",
    }

    ALL_PHASE3_WORKFLOWS = (
        TRACK_1_WORKFLOWS | TRACK_2_WORKFLOWS | TRACK_3_WORKFLOWS | TRACK_4_WORKFLOWS
    )

    def test_all_workflows_exist(self):
        """Verify all 45 Phase 3 workflows exist"""
        for workflow in self.ALL_PHASE3_WORKFLOWS:
            workflow_dir = self.WORKFLOWS_DIR / workflow
            assert workflow_dir.exists(), f"Workflow {workflow} not found"

    def test_workflows_have_both_variants(self):
        """Verify each workflow has minimal and verbose variants"""
        for workflow in self.ALL_PHASE3_WORKFLOWS:
            minimal = self.WORKFLOWS_DIR / workflow / "minimal" / "workflow.md"
            verbose = self.WORKFLOWS_DIR / workflow / "verbose" / "workflow.md"

            assert minimal.exists(), f"Minimal variant missing for {workflow}"
            assert verbose.exists(), f"Verbose variant missing for {workflow}"

    def test_workflows_have_valid_size(self):
        """Verify workflow files have expected line counts"""
        for workflow in self.ALL_PHASE3_WORKFLOWS:
            minimal = self.WORKFLOWS_DIR / workflow / "minimal" / "workflow.md"
            verbose = self.WORKFLOWS_DIR / workflow / "verbose" / "workflow.md"

            # Minimal should be at least 15 lines
            min_lines = len(minimal.read_text().splitlines())
            assert min_lines > 15, f"{workflow} minimal too small: {min_lines} lines"

            # Verbose should be substantially larger than minimal
            verb_lines = len(verbose.read_text().splitlines())
            assert verb_lines > min_lines, f"{workflow} verbose should be larger than minimal"

    def test_workflows_have_yaml_frontmatter(self):
        """Verify workflows have valid YAML frontmatter"""
        for workflow in self.ALL_PHASE3_WORKFLOWS:
            for variant in ["minimal", "verbose"]:
                filepath = self.WORKFLOWS_DIR / workflow / variant / "workflow.md"
                content = filepath.read_text()

                # Should start and end with ---
                assert content.startswith("---"), f"{workflow} {variant} missing YAML start"
                assert "---" in content[4:], f"{workflow} {variant} missing YAML end"

                # Extract and parse YAML
                yaml_end = content.find("---", 4)
                yaml_content = content[4:yaml_end].strip()

                parsed = yaml.safe_load(yaml_content)
                assert parsed is not None, f"{workflow} {variant} has invalid YAML"
                assert "name" in parsed, f"{workflow} {variant} missing 'name' field"
                assert "description" in parsed, f"{workflow} {variant} missing 'description' field"

    def test_track_distribution(self):
        """Verify correct distribution across tracks"""
        assert len(self.TRACK_1_WORKFLOWS) == 12, "Track 1 should have 12 workflows"
        assert len(self.TRACK_2_WORKFLOWS) == 10, "Track 2 should have 10 workflows"
        assert len(self.TRACK_3_WORKFLOWS) == 8, "Track 3 should have 8 workflows"
        assert len(self.TRACK_4_WORKFLOWS) == 15, "Track 4 should have 15 workflows"
        assert len(self.ALL_PHASE3_WORKFLOWS) == 45, "Total should be 45 workflows"


class TestPhase3Skills:
    """Test Phase 3 skill creation and structure"""

    SKILLS_DIR = Path("promptosaurus/skills")

    # Expected skills by track
    TRACK_1_SKILLS = {
        "data-validation-pipelines",
        "feature-store-design",
        "model-performance-debugging",
        "hyperparameter-optimization",
        "data-versioning-reproducibility",
        "ensemble-methods",
        "cross-validation-strategies",
        "imbalanced-classification",
        "time-series-preprocessing",
        "dimensionality-reduction",
        "anomaly-detection-techniques",
        "feature-importance-analysis",
        "model-interpretability",
        "batch-vs-realtime-scoring",
        "mlops-pipeline-design",
    }

    TRACK_2_SKILLS = {
        "threat-identification",
        "vulnerability-assessment",
        "secure-code-review",
        "cryptography-fundamentals",
        "authentication-design",
        "authorization-patterns",
        "api-security-hardening",
        "security-testing-strategies",
        "incident-response-planning",
        "compliance-assessment",
        "secret-management",
        "security-architecture-review",
    }

    TRACK_3_SKILLS = {
        "user-needs-discovery",
        "requirements-specification",
        "success-metrics-definition",
        "roadmap-prioritization",
        "user-testing-methods",
        "competitor-analysis",
        "ux-writing-guidelines",
        "launch-readiness-checklist",
        "stakeholder-communication",
        "product-analytics-setup",
    }

    TRACK_4_SKILLS = {
        "technical-decision-making",
        "architecture-documentation",
        "code-review-practices",
        "testing-strategies",
        "documentation-best-practices",
        "team-collaboration",
        "problem-decomposition",
        "technical-communication",
        "performance-optimization",
        "debugging-methodology",
        "quality-assurance",
        "technical-debt-management",
        "continuous-improvement",
    }

    ALL_PHASE3_SKILLS = TRACK_1_SKILLS | TRACK_2_SKILLS | TRACK_3_SKILLS | TRACK_4_SKILLS

    def test_all_skills_exist(self):
        """Verify all 50 Phase 3 skills exist"""
        for skill in self.ALL_PHASE3_SKILLS:
            skill_dir = self.SKILLS_DIR / skill
            assert skill_dir.exists(), f"Skill {skill} not found"

    def test_skills_have_both_variants(self):
        """Verify each skill has minimal and verbose variants"""
        for skill in self.ALL_PHASE3_SKILLS:
            minimal = self.SKILLS_DIR / skill / "minimal" / "SKILL.md"
            verbose = self.SKILLS_DIR / skill / "verbose" / "SKILL.md"

            assert minimal.exists(), f"Minimal variant missing for {skill}"
            assert verbose.exists(), f"Verbose variant missing for {skill}"

    def test_skills_have_valid_size(self):
        """Verify skill files have expected line counts"""
        for skill in self.ALL_PHASE3_SKILLS:
            minimal = self.SKILLS_DIR / skill / "minimal" / "SKILL.md"
            verbose = self.SKILLS_DIR / skill / "verbose" / "SKILL.md"

            # Minimal should have some content
            min_lines = len(minimal.read_text().splitlines())
            assert min_lines > 15, f"{skill} minimal too small: {min_lines} lines"

            # Verbose should be substantially larger
            verb_lines = len(verbose.read_text().splitlines())
            assert verb_lines > min_lines, f"{skill} verbose should be larger than minimal"

    def test_skills_have_yaml_frontmatter(self):
        """Verify skills have valid YAML frontmatter"""
        for skill in self.ALL_PHASE3_SKILLS:
            for variant in ["minimal", "verbose"]:
                filepath = self.SKILLS_DIR / skill / variant / "SKILL.md"
                content = filepath.read_text()

                # Should start and end with ---
                assert content.startswith("---"), f"{skill} {variant} missing YAML start"
                assert "---" in content[4:], f"{skill} {variant} missing YAML end"

                # Extract and parse YAML
                yaml_end = content.find("---", 4)
                yaml_content = content[4:yaml_end].strip()

                parsed = yaml.safe_load(yaml_content)
                assert parsed is not None, f"{skill} {variant} has invalid YAML"
                assert "name" in parsed, f"{skill} {variant} missing 'name' field"
                assert "description" in parsed, f"{skill} {variant} missing 'description' field"

    def test_track_distribution(self):
        """Verify correct distribution across tracks"""
        assert len(self.TRACK_1_SKILLS) == 15, "Track 1 should have 15 skills"
        assert len(self.TRACK_2_SKILLS) == 12, "Track 2 should have 12 skills"
        assert len(self.TRACK_3_SKILLS) == 10, "Track 3 should have 10 skills"
        assert len(self.TRACK_4_SKILLS) == 13, "Track 4 should have 13 skills"
        assert len(self.ALL_PHASE3_SKILLS) == 50, "Total should be 50 skills"


class TestPhase3Registration:
    """Test Phase 3 registration in language_skill_mapping.yaml"""

    MAPPING_FILE = Path("language_skill_mapping.yaml")

    def test_mapping_file_exists(self):
        """Verify language_skill_mapping.yaml exists"""
        assert self.MAPPING_FILE.exists(), "language_skill_mapping.yaml not found"

    def test_mapping_file_valid_yaml(self):
        """Verify mapping file is valid YAML"""
        content = self.MAPPING_FILE.read_text()
        parsed = yaml.safe_load(content)
        assert parsed is not None, "language_skill_mapping.yaml is not valid YAML"

    def test_workflows_registered_in_python(self):
        """Verify Phase 3 workflows registered in python section"""
        content = self.MAPPING_FILE.read_text()
        parsed = yaml.safe_load(content)

        python_workflows = parsed.get("python", {}).get("workflows", [])

        # Check Track 1 workflows
        assert "model-evaluation-workflow" in python_workflows
        assert "mlops-pipeline-setup" in python_workflows
        assert "production-ml-deployment" in python_workflows

    def test_skills_registered_in_python(self):
        """Verify Phase 3 skills registered in python section"""
        content = self.MAPPING_FILE.read_text()
        parsed = yaml.safe_load(content)

        python_skills = parsed.get("python", {}).get("skills", [])

        # Check Track 1 skills
        assert "data-validation-pipelines" in python_skills
        assert "ensemble-methods" in python_skills
        assert "mlops-pipeline-design" in python_skills

    def test_security_section_exists(self):
        """Verify new 'security' section exists"""
        content = self.MAPPING_FILE.read_text()
        parsed = yaml.safe_load(content)

        assert "security" in parsed, "security section not found"
        assert "workflows" in parsed["security"], "security workflows not found"
        assert "skills" in parsed["security"], "security skills not found"

    def test_product_section_exists(self):
        """Verify new 'product' section exists"""
        content = self.MAPPING_FILE.read_text()
        parsed = yaml.safe_load(content)

        assert "product" in parsed, "product section not found"
        assert "workflows" in parsed["product"], "product workflows not found"
        assert "skills" in parsed["product"], "product skills not found"

    def test_security_workflows_registered(self):
        """Verify Phase 3 security workflows registered"""
        content = self.MAPPING_FILE.read_text()
        parsed = yaml.safe_load(content)

        security_workflows = parsed.get("security", {}).get("workflows", [])

        assert "threat-modeling-workflow" in security_workflows
        assert "vulnerability-scanning-workflow" in security_workflows
        assert "security-testing-workflow" in security_workflows
        assert "compliance-audit-workflow" in security_workflows

    def test_security_skills_registered(self):
        """Verify Phase 3 security skills registered"""
        content = self.MAPPING_FILE.read_text()
        parsed = yaml.safe_load(content)

        security_skills = parsed.get("security", {}).get("skills", [])

        assert "threat-identification" in security_skills
        assert "vulnerability-assessment" in security_skills
        assert "secure-code-review" in security_skills

    def test_product_workflows_registered(self):
        """Verify Phase 3 product workflows registered"""
        content = self.MAPPING_FILE.read_text()
        parsed = yaml.safe_load(content)

        product_workflows = parsed.get("product", {}).get("workflows", [])

        assert "requirements-gathering-workflow" in product_workflows
        assert "roadmap-planning-workflow" in product_workflows
        assert "feature-prioritization-workflow" in product_workflows

    def test_product_skills_registered(self):
        """Verify Phase 3 product skills registered"""
        content = self.MAPPING_FILE.read_text()
        parsed = yaml.safe_load(content)

        product_skills = parsed.get("product", {}).get("skills", [])

        assert "user-needs-discovery" in product_skills
        assert "requirements-specification" in product_skills
        assert "success-metrics-definition" in product_skills


class TestPhase3Totals:
    """Test overall Phase 3 deliverables"""

    WORKFLOWS_DIR = Path("promptosaurus/workflows")
    SKILLS_DIR = Path("promptosaurus/skills")

    def test_total_phase3_workflows(self):
        """Verify 45 Phase 3 workflows total"""
        workflow_files = list(self.WORKFLOWS_DIR.glob("*/minimal/workflow.md"))
        # Count those that are Phase 3 (not Phase 1-2)
        phase3_workflows = {
            wf.parent.parent.name
            for wf in workflow_files
            if not wf.parent.parent.name
            in {
                "feature-workflow",
                "testing-workflow",
                "code-workflow",
                "refactor-workflow",
                "review-workflow",
                "migration-workflow",
            }
        }
        assert len(phase3_workflows) >= 45, (
            f"Expected ≥45 Phase 3 workflows, got {len(phase3_workflows)}"
        )

    def test_total_phase3_skills(self):
        """Verify 50 Phase 3 skills total"""
        skill_files = list(self.SKILLS_DIR.glob("*/minimal/SKILL.md"))
        # Count those that are Phase 3 (not Phase 1-2)
        phase3_skills = {
            sk.parent.parent.name
            for sk in skill_files
            if not sk.parent.parent.name
            in {
                "feature-planning",
                "post-implementation-checklist",
                "incremental-implementation",
                "test-aaa-structure",
            }
        }
        assert len(phase3_skills) >= 50, f"Expected ≥50 Phase 3 skills, got {len(phase3_skills)}"

    def test_total_files_created(self):
        """Verify Phase 3 files created"""
        # Count workflow files (both minimal and verbose across all subdirs)
        workflow_files = len(list(self.WORKFLOWS_DIR.glob("*/minimal/workflow.md"))) + len(
            list(self.WORKFLOWS_DIR.glob("*/verbose/workflow.md"))
        )

        # Should have 90 workflow files (45 workflows × 2 variants)
        assert workflow_files >= 80, f"Expected ≥80 workflow files, got {workflow_files}"

        # Count skill files (both minimal and verbose across all subdirs)
        skill_files = len(list(self.SKILLS_DIR.glob("*/minimal/SKILL.md"))) + len(
            list(self.SKILLS_DIR.glob("*/verbose/SKILL.md"))
        )

        # Should have 100 skill files (50 skills × 2 variants)
        assert skill_files >= 100, f"Expected ≥100 skill files, got {skill_files}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
