"""Test configuration and fixtures."""

from pathlib import Path

import pytest


@pytest.fixture
def project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def agents_dir(project_root):
    """Get agents directory."""
    return project_root / "prompticorn" / "agents"


@pytest.fixture
def workflows_dir(project_root):
    """Get workflows directory."""
    return project_root / "prompticorn" / "workflows"


@pytest.fixture
def skills_dir(project_root):
    """Get skills directory."""
    return project_root / "prompticorn" / "skills"


@pytest.fixture
def read_file():
    """Fixture to read file contents."""

    def _read(path):
        with open(path) as f:
            return f.read()

    return _read


@pytest.fixture
def agent_structure():
    """Expected structure for agent files."""
    return {
        "required_sections": ["# ", "Purpose", "Responsibilities", "Capabilities"],
        "min_lines": 20,
    }


@pytest.fixture
def subagent_structure():
    """Expected structure for subagent files."""
    return {
        "required_sections": [
            "# ",
            "Purpose",
            "Key Concepts",
            "Examples",
        ],
        "min_lines": 40,
        "has_variants": True,  # minimal and verbose
    }


@pytest.fixture
def workflow_structure():
    """Expected structure for workflow files."""
    return {
        "required_sections": ["# ", "Purpose", "Steps", "Success Criteria"],
        "min_lines": 50,
        "has_variants": True,  # minimal and verbose
    }


@pytest.fixture
def skill_structure():
    """Expected structure for skill files."""
    return {
        "required_sections": ["# ", "Purpose", "Core Concepts", "Examples", "Best Practices"],
        "min_lines": 40,
        "has_variants": True,  # minimal and verbose
    }


# Markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: unit tests")
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "validation: validation tests")
