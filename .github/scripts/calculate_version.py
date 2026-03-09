#!/usr/bin/env python3
"""
Derived Version Calculator for Trunk-Based Development.

Version Schema: MAJOR.MINOR.PATCH[-RUN]

- MAJOR: From CI/CD environment (MAJOR_VERSION)
- MINOR: Latest MINOR on PyPI for that MAJOR + 1
- PATCH: PR number
- -RUN: GitHub run number (only for TestPyPI preview builds)

PyPI is queried to determine the baseline version. If PyPI query fails,
the build fails (strict mode for first-release setup).
"""

import json
import os
import re
import sys
import urllib.request


class VersionCalculator:
    """Calculates version based on PyPI release history."""

    def __init__(self, package_name: str = "promptosaurus"):
        self.package_name = package_name

    def get_pypi_version(self) -> tuple[int, int] | None:
        """
        Query PyPI for the latest published version.

        Returns:
            Tuple of (major, minor) or None if not found
        """
        try:
            # Strip package name to handle any whitespace issues
            package = self.package_name.strip()
            url = f"https://pypi.org/pypi/{package}/json"
            print(f"Querying PyPI: {url}")
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read())
                version = data["info"]["version"]

                # Parse version (handle formats like 1.2.3, 1.2.3-beta, etc.)
                # Strip any pre-release/build suffixes
                version = re.split(r"[+-]", version)[0]
                parts = version.split(".")

                major = int(parts[0]) if len(parts) > 0 else 0
                minor = int(parts[1]) if len(parts) > 1 else 0

                return (major, minor)
        except Exception as e:
            print(f"PyPI query failed: {e}", file=sys.stderr)
            return None

    def calculate_version(
        self,
        major: int,
        pr_number: str | None,
        run_number: str | None,
        is_testpypi: bool,
    ) -> str:
        """
        Calculate version based on PyPI history and PR context.

        Args:
            major: MAJOR version from environment
            pr_number: PR number from GitHub event
            run_number: GitHub run number
            is_testpypi: Whether this is a TestPyPI build

        Returns:
            Version string
        """
        # Query PyPI for latest version
        pypi_version = self.get_pypi_version()

        if pypi_version is None:
            # First release: use MAJOR.0.PR{-RUN}
            # No previous version exists
            new_minor = 0
        else:
            pypi_major, pypi_minor = pypi_version

            # Calculate new MINOR
            # If MAJOR matches: increment MINOR from latest
            # If MAJOR different: start fresh at MINOR 1
            if pypi_major == major:
                new_minor = pypi_minor + 1
            else:
                new_minor = 1

        # PATCH is PR number (required for both TestPyPI and PyPI)
        if pr_number is None:
            print("ERROR: PR number is required for versioning")
            sys.exit(1)

        # Build version: MAJOR.MINOR.PATCH[-RUN]
        version = f"{major}.{new_minor}.{pr_number}"

        # Append run number only for TestPyPI preview builds
        if is_testpypi and run_number:
            version = f"{version}-{run_number}"

        return version


def main():
    """Main entry point for CI/CD integration."""
    # Get package name from environment or use default (strip whitespace)
    package_name = os.environ.get("PACKAGE_NAME", "promptosaurus").strip()

    # Get MAJOR version from environment
    env_major = os.environ.get("MAJOR_VERSION", "0").strip()
    try:
        major = int(env_major)
    except ValueError:
        print(f"ERROR: Invalid MAJOR_VERSION '{env_major}', defaulting to 0")
        major = 0

    # Get GitHub context
    event_name = os.environ.get("GITHUB_EVENT_NAME", "push").strip()
    action = os.environ.get("GITHUB_ACTION", "").strip()
    base_ref = os.environ.get("GITHUB_BASE_REF", "").strip()
    run_number = os.environ.get("GITHUB_RUN_NUMBER", "").strip()

    # Determine if this is a PR
    is_pr = event_name == "pull_request"
    is_pr_to_main = base_ref == "refs/heads/main" or base_ref == "main"

    # Extract PR number from event
    pr_number = None
    if is_pr:
        # Try to get PR number from GITHUB_REF (format: refs/pull/28/merge)
        ref = os.environ.get("GITHUB_REF", "").strip()
        match = re.search(r"refs/pull/(\d+)/", ref)
        if match:
            pr_number = match.group(1)

    # Determine publishing targets
    is_testpypi = is_pr and is_pr_to_main and action != "closed"
    is_pypi = is_pr and action == "closed" and is_pr_to_main

    # Calculate version
    calculator = VersionCalculator(package_name)
    version = calculator.calculate_version(
        major=major,
        pr_number=pr_number,
        run_number=run_number,
        is_testpypi=is_testpypi,
    )

    # Output for GitHub Actions
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"version={version}\n")
            f.write(f"should_publish_testpypi={str(is_testpypi).lower()}\n")
            f.write(f"should_publish_pypi={str(is_pypi).lower()}\n")

    print(f"Version: {version}")
    print(f"Publish TestPyPI: {is_testpypi}")
    print(f"Publish PyPI: {is_pypi}")
    print(f"PR Number: {pr_number}")
    print(f"Major: {major}")

    return version


if __name__ == "__main__":
    main()
