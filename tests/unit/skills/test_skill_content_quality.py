"""Content-quality gate for skills (PRO-7).

Two failure modes shipped to users for a long time without any test noticing:

1. **Unfilled template placeholders** — files containing literal
   ``Concept 1: [Explanation]`` and ``[Step 1 description]``, emitted verbatim
   into user builds.
2. **Generic boilerplate** — 26 files sharing identical filler
   (``Understand the fundamentals``, ``Apply to real scenarios``) that says
   nothing about the skill it purports to teach.

``KNOWN_HOLLOW`` is the remaining backlog, and it may only ever shrink. A skill
absent from that set must have real content; a skill listed in it that has since
been filled must be removed from the set. That second direction is what stops
the allowlist from quietly becoming permanent.
"""

import re
from pathlib import Path

import pytest

_VARIANTS = ("minimal", "verbose")

# Literal artifacts of an unfilled template.
_PLACEHOLDER_PATTERNS = (
    re.compile(r"\[Explanation\]"),
    re.compile(r"\[Step \d"),
    re.compile(r"\[Practice"),
    re.compile(r"\[What is it\]"),
    re.compile(r"\[Name\]"),
    re.compile(r"^#+ *Concept \d", re.MULTILINE),
    re.compile(r"^- *Concept \d:", re.MULTILINE),
    re.compile(r"^- *Practice \d *$", re.MULTILINE),
    re.compile(r"^- *Importance \d *$", re.MULTILINE),
)

# Filler shared verbatim across the bulk-generated skills.
_BOILERPLATE_PHRASES = (
    "Understand the fundamentals",
    "Apply to real scenarios",
    "Can explain concepts clearly",
    "Can mentor others",
)

# Skills still awaiting real content. This set MUST only shrink — see module
# docstring. Delete this constant and the xfail branch once it reaches zero.
KNOWN_HOLLOW: frozenset[str] = frozenset(
    {
        "anomaly-detection-techniques",
        "api-versioning-strategy",
        "architecture-documentation",
        "batch-vs-realtime-scoring",
        "code-review-practices",
        "competitor-analysis",
        "compliance-assessment",
        "compliance-automation",
        "component-design-systems",
        "continuous-improvement",
        "cross-validation-strategies",
        "css-performance-optimization",
        "data-validation-pipelines",
        "data-versioning-reproducibility",
        "debugging-methodology",
        "deployment-rollback-strategies",
        "dimensionality-reduction",
        "distributed-caching-design",
        "documentation-best-practices",
        "ensemble-methods",
        "feature-engineering",
        "feature-importance-analysis",
        "feature-store-design",
        "flaky-test-remediation",
        "hyperparameter-optimization",
        "iac-best-practices",
        "imbalanced-classification",
        "incident-automation",
        "incident-response-planning",
        "infrastructure-drift-detection",
        "launch-readiness-checklist",
        "load-testing",
        "microservices-communication-patterns",
        "ml-deployment",
        "mlops-pipeline-design",
        "model-evaluation",
        "model-interpretability",
        "model-monitoring",
        "model-performance-debugging",
        "mutation-testing",
        "nosql-database-selection",
        "performance-optimization",
        "problem-decomposition",
        "product-analytics-setup",
        "quality-assurance",
        "requirements-specification",
        "responsive-design-patterns",
        "roadmap-prioritization",
        "stakeholder-communication",
        "state-management-architecture",
        "success-metrics-definition",
        "team-collaboration",
        "technical-communication",
        "technical-debt-management",
        "technical-decision-making",
        "test-data-strategies",
        "testing-strategies",
        "time-series-preprocessing",
        "user-needs-discovery",
        "user-testing-methods",
        "ux-writing-guidelines",
    }
)


def _defects(text: str) -> list[str]:
    """Return the hollow-content markers found in a skill file."""
    found = [p.pattern for p in _PLACEHOLDER_PATTERNS if p.search(text)]
    found += [f"boilerplate: {p!r}" for p in _BOILERPLATE_PHRASES if p in text]
    return found


def _skill_names(skills_dir: Path) -> list[str]:
    return sorted(path.name for path in skills_dir.iterdir() if path.is_dir())


@pytest.mark.unit
class TestSkillContentQuality:
    """No skill ships template placeholders or generic filler."""

    def test_filled_skills_have_no_placeholders(self, skills_dir):
        """Every skill outside the backlog contains real content."""
        offenders: dict[str, list[str]] = {}
        for name in _skill_names(skills_dir):
            if name in KNOWN_HOLLOW:
                continue
            for variant in _VARIANTS:
                path = skills_dir / name / variant / "SKILL.md"
                defects = _defects(path.read_text(encoding="utf-8"))
                if defects:
                    offenders[f"{name}/{variant}"] = defects
        assert not offenders, (
            "These skills contain unfilled template placeholders or generic "
            f"boilerplate and would ship as-is to users: {offenders}"
        )

    def test_backlog_only_lists_skills_that_are_still_hollow(self, skills_dir):
        """A filled skill must be removed from KNOWN_HOLLOW.

        Without this, the allowlist would silently outlive the problem and start
        exempting skills that no longer need exempting.
        """
        stale = sorted(
            name
            for name in KNOWN_HOLLOW
            if not any(
                _defects((skills_dir / name / variant / "SKILL.md").read_text(encoding="utf-8"))
                for variant in _VARIANTS
            )
        )
        assert not stale, (
            "These skills now have real content — remove them from KNOWN_HOLLOW "
            f"in this file: {stale}"
        )

    def test_backlog_entries_all_exist(self, skills_dir):
        """KNOWN_HOLLOW must not accumulate names of deleted skills."""
        unknown = sorted(KNOWN_HOLLOW - set(_skill_names(skills_dir)))
        assert not unknown, f"KNOWN_HOLLOW lists skills that no longer exist: {unknown}"
