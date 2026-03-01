#!/usr/bin/env python3
"""
Derived Version Calculator for Trunk-Based Development.

Version is calculated purely from git merge history - NO TAGS REQUIRED.
This eliminates both version file conflicts AND tag fragility.

Version Schema: MAJOR.MINOR.PATCH

- MAJOR: Human-controlled via .major-version file (breaking changes)
- MINOR: Count of feat/ branches merged to main
- PATCH: Count of bug/hotfix/security branches merged since last feat/

Branch Naming Conventions:
- feat/*, feature/*  → increments MINOR (resets PATCH to 0)
- bug/*, fix/*       → increments PATCH
- hotfix/*           → increments PATCH (priority)
- security/*         → increments PATCH (priority)

No prerelease tags, no build metadata in versions, no external dependencies.
"""

import os
import re
import subprocess
from dataclasses import dataclass


@dataclass
class BranchMerge:
    """Represents a merge commit from a branch."""

    commit_hash: str
    source_branch: str
    branch_type: str  # 'feature', 'fix', 'hotfix', 'security', 'other'
    timestamp: int  # commit timestamp for ordering


class VersionCalculator:
    """Calculates version based on git merge history - no tags needed."""

    # Branch prefixes that affect versioning
    FEATURE_PREFIXES = ("feat/", "feature/")
    FIX_PREFIXES = ("bug/", "fix/")
    HOTFIX_PREFIXES = ("hotfix/",)
    SECURITY_PREFIXES = ("security/",)

    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path

    def _run_git(self, *args: str) -> str:
        """Execute a git command and return output."""
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=True,
            cwd=self.repo_path,
        )
        return result.stdout.strip()

    def get_major_version(self) -> int:
        """
        Get the human-controlled major version from CI/CD environment.

        MAJOR_VERSION is hardcoded in the workflow file.
        Edit the workflow env to bump major version for breaking changes.
        """
        env_major = os.environ.get("MAJOR_VERSION", "0")
        try:
            return int(env_major)
        except ValueError:
            return 0

    def classify_branch(self, branch_name: str) -> str:
        """Classify a branch by its type."""
        branch_lower = branch_name.lower()

        if any(branch_lower.startswith(p) for p in self.FEATURE_PREFIXES):
            return "feature"
        if any(branch_lower.startswith(p) for p in self.HOTFIX_PREFIXES):
            return "hotfix"
        if any(branch_lower.startswith(p) for p in self.SECURITY_PREFIXES):
            return "security"
        if any(branch_lower.startswith(p) for p in self.FIX_PREFIXES):
            return "fix"
        return "other"

    def get_merged_branches(self) -> list[BranchMerge]:
        """Get list of all branches merged to main, ordered by merge time."""
        try:
            # Get merge commits with timestamp
            # Format: %H=commit hash, %ct=commit timestamp, %s=subject
            output = self._run_git(
                "log",
                "--merges",
                "--first-parent",
                "--pretty=format:%H|%ct|%s",
                "main",
            )
        except subprocess.CalledProcessError:
            # Try without specifying branch (for detached HEAD or other branches)
            try:
                output = self._run_git(
                    "log",
                    "--merges",
                    "--first-parent",
                    "--pretty=format:%H|%ct|%s",
                )
            except subprocess.CalledProcessError:
                return []

        if not output:
            return []

        merges = []
        # Pattern to extract branch name from merge commit message
        merge_patterns = [
            re.compile(r"Merge (?:branch|pull request) ['\"]?([^'\"\s]+)['\"]?"),
            re.compile(r"Merge remote-tracking branch ['\"]?([^'\"\s]+)['\"]?"),
        ]

        for line in output.split("\n"):
            parts = line.split("|", 2)
            if len(parts) != 3:
                continue

            commit_hash, timestamp_str, subject = parts

            # Extract branch name from merge message
            source_branch = None
            for pattern in merge_patterns:
                match = pattern.search(subject)
                if match:
                    source_branch = match.group(1)
                    break

            if not source_branch:
                # Fallback: try to extract from common patterns
                if "Merge branch" in subject:
                    parts = subject.split()
                    if len(parts) >= 3:
                        source_branch = parts[-1].strip("'\"")
                elif "Merge pull request" in subject:
                    # For PR merges, we can't easily get the source branch
                    # Skip these or mark as unknown
                    continue

            if not source_branch:
                continue

            branch_type = self.classify_branch(source_branch)
            merges.append(
                BranchMerge(
                    commit_hash=commit_hash,
                    source_branch=source_branch,
                    branch_type=branch_type,
                    timestamp=int(timestamp_str),
                )
            )

        # Sort by timestamp (oldest first) so we process in chronological order
        merges.sort(key=lambda m: m.timestamp)
        return merges

    def calculate_version(self) -> tuple[str, list[str]]:
        """
        Calculate version based on merged branches.

        Returns:
            Tuple of (version_string, warnings)
        """
        warnings = []
        major = self.get_major_version()
        merges = self.get_merged_branches()

        if not merges:
            # No merges yet - starting fresh
            return f"{major}.0.0", []

        # Count features and fixes
        features = [m for m in merges if m.branch_type == "feature"]
        fixes = [m for m in merges if m.branch_type in ("fix", "hotfix", "security")]

        # Calculate minor version (total features merged)
        minor = len(features)

        # Calculate patch version (fixes since last feature)
        if features:
            # Get timestamp of last feature merge
            last_feature_timestamp = features[-1].timestamp
            # Count fixes after the last feature
            patch = len([m for m in fixes if m.timestamp > last_feature_timestamp])
        else:
            # No features yet - count all fixes
            patch = len(fixes)

        version = f"{major}.{minor}.{patch}"

        # Generate warnings for unclassified branches
        other_branches = [m for m in merges if m.branch_type == "other"]
        if other_branches:
            for merge in other_branches[:3]:  # Limit warnings
                warnings.append(
                    f"Unclassified branch: {merge.source_branch} "
                    f"({merge.commit_hash[:7]}) - no version impact"
                )

        return version, warnings


def main():
    """Main entry point for CI/CD integration."""
    calculator = VersionCalculator()
    version, warnings = calculator.calculate_version()

    # Determine if this is a publishable build (only main branch)
    event_name = os.environ.get("GITHUB_EVENT_NAME", "push")
    ref = os.environ.get("GITHUB_REF", "")
    is_main = ref == "refs/heads/main" or ref == "refs/heads/master"
    should_publish = is_main and event_name == "push"

    # Output for GitHub Actions
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"version={version}\n")
            f.write(f"should_publish={str(should_publish).lower()}\n")

    print(f"Version: {version}")
    print(f"Publish: {should_publish}")

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  - {warning}")

    return version


if __name__ == "__main__":
    main()
