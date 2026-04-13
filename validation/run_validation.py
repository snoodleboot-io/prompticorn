"""Main validation script for Phase 1 content."""

import sys
from pathlib import Path

from consistency_checker import ConsistencyChecker
from content_validator import ContentValidator
from coverage_analyzer import CoverageAnalyzer


def main():
    """Run all validations."""
    project_root = Path(__file__).parent.parent

    print("\n" + "=" * 60)
    print("PROMPTOSAURUS PHASE 1 VALIDATION SUITE")
    print("=" * 60 + "\n")

    # Run content validation
    print("1. Running Content Validation...")
    content_validator = ContentValidator(project_root)
    error_count, warning_count = content_validator.validate_all()
    content_validator.validate_subagent_coverage()
    print(content_validator.report())

    # Run consistency checks
    print("\n2. Running Consistency Checks...")
    consistency = ConsistencyChecker(project_root)
    issue_count, issues = consistency.check_all()
    print(consistency.report())

    # Run coverage analysis
    print("\n3. Running Coverage Analysis...")
    coverage = CoverageAnalyzer(project_root)
    print(coverage.report())

    # Final summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Content Validation:  {error_count} errors, {warning_count} warnings")
    print(f"Consistency Checks:  {issue_count} issues")
    print("Coverage:            See analysis above")

    # Exit code
    if error_count > 0:
        print("\n✗ VALIDATION FAILED - Please fix errors")
        return 1
    elif warning_count > 0 or issue_count > 0:
        print("\n⚠ VALIDATION PASSED WITH WARNINGS - Review recommended")
        return 0
    else:
        print("\n✓ VALIDATION PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
