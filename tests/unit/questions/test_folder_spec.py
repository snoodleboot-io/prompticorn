"""Tests for promptosaurus.questions.base.folder_spec module."""

from promptosaurus.questions.base.folder_spec import FolderSpec


class TestFolderSpec:
    """Tests for FolderSpec dataclass."""

    def test_creates_basic_folder_spec(self):
        """Should create a basic folder spec with required fields."""
        spec = FolderSpec(
            folder="frontend",
            type="frontend",
            subtype="ui",
            language="typescript",
        )

        assert spec.folder == "frontend"
        assert spec.type == "frontend"
        assert spec.subtype == "ui"
        assert spec.language == "typescript"

    def test_creates_folder_spec_with_defaults(self):
        """Should create folder spec with sensible defaults."""
        spec = FolderSpec(
            folder="backend",
            type="backend",
            subtype="api",
            language="python",
        )

        # Defaults should be set
        assert spec.runtime == "3.14"
        assert spec.package_manager == "uv"
        assert spec.test_framework == "pytest"
        assert spec.linter == "ruff"
        assert spec.formatter == "ruff"
        assert spec.coverage is not None

    def test_creates_folder_spec_with_all_fields(self):
        """Should create folder spec with all fields specified."""
        spec = FolderSpec(
            folder="services/auth/api",
            type="backend",
            subtype="api",
            language="python",
            runtime="3.11",
            package_manager="pip",
            test_framework="pytest",
            linter="pylint",
            formatter="black",
            coverage={
                "line": 90,
                "branch": 80,
                "function": 95,
                "statement": 85,
                "mutation": 85,
                "path": 70,
            },
        )

        assert spec.folder == "services/auth/api"
        assert spec.type == "backend"
        assert spec.subtype == "api"
        assert spec.language == "python"
        assert spec.runtime == "3.11"
        assert spec.package_manager == "pip"
        assert spec.test_framework == "pytest"
        assert spec.linter == "pylint"
        assert spec.formatter == "black"
        assert spec.coverage["line"] == 90
        assert spec.coverage["branch"] == 80

    def test_frontend_ui_defaults_to_typescript(self):
        """Frontend UI should default to TypeScript."""
        spec = FolderSpec(
            folder="frontend",
            type="frontend",
            subtype="ui",
            language="typescript",
        )

        assert spec.language == "typescript"
        assert spec.package_manager == "pnpm"
        assert spec.test_framework == "vitest"
        assert spec.linter == "eslint"
        assert spec.formatter == "prettier"

    def test_backend_api_defaults_to_python(self):
        """Backend API should default to Python."""
        spec = FolderSpec(
            folder="backend",
            type="backend",
            subtype="api",
            language="python",
        )

        assert spec.language == "python"
        assert spec.runtime == "3.14"
        assert spec.package_manager == "uv"
        assert spec.test_framework == "pytest"
        assert spec.linter == "ruff"
        assert spec.formatter == "ruff"

    def test_hierarchical_folder_path(self):
        """Should support hierarchical folder paths."""
        spec = FolderSpec(
            folder="services/auth/api",
            type="backend",
            subtype="api",
            language="python",
        )

        assert spec.folder == "services/auth/api"

    def test_to_dict(self):
        """Should convert to dictionary."""
        spec = FolderSpec(
            folder="frontend",
            type="frontend",
            subtype="ui",
            language="typescript",
        )

        result = spec.to_dict()

        assert isinstance(result, dict)
        assert result["folder"] == "frontend"
        assert result["type"] == "frontend"
        assert result["subtype"] == "ui"
        assert result["language"] == "typescript"

    def test_from_dict(self):
        """Should create from dictionary."""
        data = {
            "folder": "backend",
            "type": "backend",
            "subtype": "api",
            "language": "python",
        }

        spec = FolderSpec.from_dict(data)

        assert spec.folder == "backend"
        assert spec.type == "backend"
        assert spec.subtype == "api"
        assert spec.language == "python"


class TestFolderSpecDefaults:
    """Tests for FolderSpec default values."""

    def test_python_defaults(self):
        """Python language should have correct defaults."""
        spec = FolderSpec(
            folder="lib",
            type="backend",
            subtype="library",
            language="python",
        )

        assert spec.runtime == "3.14"
        assert spec.package_manager == "uv"
        assert spec.test_framework == "pytest"
        assert spec.linter == "ruff"
        assert spec.formatter == "ruff"

    def test_typescript_defaults(self):
        """TypeScript language should have correct defaults."""
        spec = FolderSpec(
            folder="web",
            type="frontend",
            subtype="ui",
            language="typescript",
        )

        assert spec.runtime == "v6.0"
        assert spec.package_manager == "pnpm"
        assert spec.test_framework == "vitest"
        assert spec.linter == "eslint"
        assert spec.formatter == "prettier"

    def test_javascript_defaults(self):
        """JavaScript language should have correct defaults."""
        spec = FolderSpec(
            folder="web",
            type="frontend",
            subtype="ui",
            language="javascript",
        )

        assert spec.runtime == "v6.0"
        assert spec.package_manager == "pnpm"
        assert spec.test_framework == "vitest"
        assert spec.linter == "eslint"
        assert spec.formatter == "prettier"

    def test_go_defaults(self):
        """Go language should have correct defaults."""
        spec = FolderSpec(
            folder="api",
            type="backend",
            subtype="api",
            language="go",
        )

        assert spec.runtime == "1.21"
        assert spec.package_manager == "go mod"
        assert spec.test_framework == "go test"
        assert spec.linter == "golangci-lint"
        assert spec.formatter == "gofmt"

    def test_java_defaults(self):
        """Java language should have correct defaults."""
        spec = FolderSpec(
            folder="backend",
            type="backend",
            subtype="api",
            language="java",
        )

        assert spec.runtime == "21"
        assert spec.package_manager == "maven"
        assert spec.test_framework == "junit"
        assert spec.linter == "checkstyle"
        assert spec.formatter == "google-java-format"

    def test_coverage_defaults(self):
        """Coverage should have correct defaults."""
        spec = FolderSpec(
            folder="lib",
            type="backend",
            subtype="library",
            language="python",
        )

        assert spec.coverage["line"] == 80
        assert spec.coverage["branch"] == 70
        assert spec.coverage["function"] == 90
        assert spec.coverage["statement"] == 85
        assert spec.coverage["mutation"] == 80
        assert spec.coverage["path"] == 60
