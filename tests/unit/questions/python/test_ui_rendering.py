"""Test UI rendering of Python questions to verify options and explanations display correctly.

This test suite executes the Python runtime and package manager questions through the UI
rendering pipeline to verify that:
1. Options display correctly without text concatenation errors
2. Explanations display correctly without garbling
3. The multi-line explanation fix works properly
"""

from promptosaurus.questions.python.python_runtime_question import PythonRuntimeQuestion
from promptosaurus.questions.python.python_package_manager_question import (
    PythonPackageManagerQuestion,
)
from promptosaurus.ui.domain.context import QuestionContext, PipelineContext
from promptosaurus.ui.render.vertical import VerticalLayoutRenderer
from promptosaurus.ui.render.columns import ColumnLayoutRenderer
from promptosaurus.ui.state.single_selection_state import SingleSelectionState


class TestPythonRuntimeUIRendering:
    """Test Python runtime question rendering through UI."""

    def test_runtime_options_render_correctly(self):
        """Test that runtime options display without concatenation errors."""
        q = PythonRuntimeQuestion()

        # Verify the raw options first
        assert q.options == ["3.11", "3.12", "3.13", "3.14", "pypy"]

        # Create question context for rendering
        context = QuestionContext(
            question=q.question_text,
            options=q.options,
            explanations=q.option_explanations,
            question_explanation=q.explanation,
            default_index=1,  # 3.12
            allow_multiple=False,
        )

        # Create pipeline context with initial selection on default
        # SingleSelectionState(selected_index, max_index)
        state = SingleSelectionState(selected=1, max_index=len(q.options) - 1)
        pipeline_ctx = PipelineContext(context, state, mode="select")

        # Render with vertical layout (5 options, so uses vertical not columns)
        renderer = VerticalLayoutRenderer()
        output = renderer.render(pipeline_ctx)

        # Verify all options are present and not garbled
        assert "3.11" in output
        assert "3.12" in output
        assert "3.13" in output
        assert "3.14" in output
        assert "pypy" in output

        # Verify no concatenation artifacts like "3.11sions" or "3.14pipy"
        assert "3.11sions" not in output
        assert "3.11pipy" not in output
        assert "3.12sions" not in output
        assert "3.14pipy" not in output

        print("\n=== Python Runtime Options Rendering ===")
        print("Vertical Layout Output:")
        print(output)
        print()

    def test_runtime_explanations_render_correctly(self):
        """Test that runtime option explanations display without garbling."""
        q = PythonRuntimeQuestion()

        # Check raw explanations
        expl = q.option_explanations

        expected_explanations = {
            "3.11": "Python 3.11 - Stable release with good performance and compatibility",
            "3.12": "Python 3.12 - Latest stable release with improved performance and new features",
            "3.13": "Python 3.13 - Latest features, may have some compatibility considerations",
            "3.14": "Python 3.14 - Cutting edge features, latest performance improvements",
            "pypy": "PyPy - Alternative Python implementation with JIT for faster execution",
        }

        for opt, expected_text in expected_explanations.items():
            assert opt in expl, f"Missing option {opt}"
            actual_text = expl[opt]
            assert actual_text == expected_text, (
                f"Explanation mismatch for {opt}:\n"
                f"  Expected: {expected_text}\n"
                f"  Got:      {actual_text}"
            )

            # Verify no text concatenation artifacts (like "pypy" appended to another option)
            # Note: "3.11" appears in its own explanation which is expected (as "Python 3.11 -")
            # and "sions" appears in legitimate words like "versions"
            assert "pypy" not in actual_text or opt == "pypy", (
                f"Found 'pypy' in {opt} explanation - text concatenation error"
            )

        print("\n=== Python Runtime Explanations ===")
        for opt in q.options:
            print(f"{opt}: {expl[opt]}")
        print()

    def test_runtime_question_explanation_multiline(self):
        """Test that question explanation multiline formatting is preserved."""
        q = PythonRuntimeQuestion()
        expl = q.explanation

        # Should have newlines preserved
        lines = expl.split("\n")
        assert len(lines) > 1, "Question explanation should be multiline"

        # Verify expected content - the explanation should mention versions/features
        assert "versions" in expl or "version" in expl or "features" in expl
        assert "runtimes" in expl or "runtime" in expl

        # Verify no strange concatenation (e.g., options stuck together)
        assert "3.113.12" not in expl
        assert "3.12pypy" not in expl
        assert "pypyruntimes" not in expl

        print("\n=== Python Runtime Question Explanation ===")
        print(expl)
        print()


class TestPythonPackageManagerUIRendering:
    """Test Python package manager question rendering through UI."""

    def test_package_manager_options_render_correctly(self):
        """Test that package manager options display without concatenation errors."""
        q = PythonPackageManagerQuestion()

        # Verify the raw options first
        assert q.options == ["pip", "uv", "poetry", "pipenv", "conda"]

        # Create question context for rendering
        context = QuestionContext(
            question=q.question_text,
            options=q.options,
            explanations=q.option_explanations,
            question_explanation=q.explanation,
            default_index=1,  # uv
            allow_multiple=False,
        )

        # Create pipeline context with initial selection on default
        state = SingleSelectionState(selected=1, max_index=len(q.options) - 1)
        pipeline_ctx = PipelineContext(context, state, mode="select")

        # Render with vertical layout (5 options, so uses vertical not columns)
        renderer = VerticalLayoutRenderer()
        output = renderer.render(pipeline_ctx)

        # Verify all options are present and not garbled
        assert "pip" in output
        assert "uv" in output
        assert "poetry" in output
        assert "pipenv" in output
        assert "conda" in output

        # Verify no concatenation artifacts
        assert "pipenvironment" not in output
        assert "pipvirtualenv" not in output
        assert "pippoetry" not in output
        assert "condapip" not in output

        print("\n=== Python Package Manager Options Rendering ===")
        print("Vertical Layout Output:")
        print(output)
        print()

    def test_package_manager_explanations_render_correctly(self):
        """Test that package manager explanations display without garbling."""
        q = PythonPackageManagerQuestion()

        # Check raw explanations
        expl = q.option_explanations

        expected_explanations = {
            "pip": "Simplest, built-in package manager for Python",
            "uv": "Ultra-fast modern replacement for pip, instant installations",
            "poetry": "Dependency management with lock files, publish to PyPI",
            "pipenv": "Combines pip and virtualenv, integrates environment management",
            "conda": "Cross-platform, handles non-Python dependencies",
        }

        for opt, expected_text in expected_explanations.items():
            assert opt in expl, f"Missing option {opt}"
            actual_text = expl[opt]
            assert actual_text == expected_text, (
                f"Explanation mismatch for {opt}:\n"
                f"  Expected: {expected_text}\n"
                f"  Got:      {actual_text}"
            )

            # Verify no text concatenation
            assert "environment" not in actual_text or opt == "pipenv", (
                f"Found 'environment' where not expected in {opt} explanation"
            )

        print("\n=== Python Package Manager Explanations ===")
        for opt in q.options:
            print(f"{opt}: {expl[opt]}")
        print()

    def test_package_manager_question_explanation_multiline(self):
        """Test that question explanation multiline formatting is preserved."""
        q = PythonPackageManagerQuestion()
        expl = q.explanation

        # Should have newlines preserved
        lines = expl.split("\n")
        assert len(lines) > 1, "Question explanation should be multiline"

        # Verify specific content without concatenation
        assert "Dependency resolution" in expl
        assert "Virtual environment" in expl or "environment" in expl

        print("\n=== Python Package Manager Question Explanation ===")
        print(expl)
        print()


class TestColumnLayoutRendering:
    """Test column layout rendering for questions with 6+ options."""

    def test_runtime_with_column_layout(self):
        """Test runtime question renders correctly with column layout."""
        # Note: Runtime has 5 options, so won't use columns by default,
        # but we can force it to test the renderer
        q = PythonRuntimeQuestion()

        context = QuestionContext(
            question=q.question_text,
            options=q.options,
            explanations=q.option_explanations,
            question_explanation=q.explanation,
            default_index=1,
            allow_multiple=False,
        )

        state = SingleSelectionState(selected=1, max_index=len(q.options) - 1)
        pipeline_ctx = PipelineContext(context, state, mode="select")

        # Force column layout
        renderer = ColumnLayoutRenderer()
        output = renderer.render(pipeline_ctx)

        # Verify all options present
        for opt in q.options:
            assert opt in output, f"Option {opt} missing from column layout"

        print("\n=== Python Runtime with Column Layout ===")
        print(output)
        print()

    def test_package_manager_with_column_layout(self):
        """Test package manager renders correctly with column layout."""
        q = PythonPackageManagerQuestion()

        context = QuestionContext(
            question=q.question_text,
            options=q.options,
            explanations=q.option_explanations,
            question_explanation=q.explanation,
            default_index=1,
            allow_multiple=False,
        )

        state = SingleSelectionState(selected=1, max_index=len(q.options) - 1)
        pipeline_ctx = PipelineContext(context, state, mode="select")

        # Force column layout
        renderer = ColumnLayoutRenderer()
        output = renderer.render(pipeline_ctx)

        # Verify all options present
        for opt in q.options:
            assert opt in output, f"Option {opt} missing from column layout"

        print("\n=== Python Package Manager with Column Layout ===")
        print(output)
        print()


class TestExplanationDisplay:
    """Test that explanations display correctly when option is selected."""

    def test_selected_runtime_shows_explanation(self):
        """Test explanation displays for selected runtime option."""
        q = PythonRuntimeQuestion()

        context = QuestionContext(
            question=q.question_text,
            options=q.options,
            explanations=q.option_explanations,
            question_explanation=q.explanation,
            default_index=1,
            allow_multiple=False,
        )

        # Select 3.13
        state = SingleSelectionState(selected=1, max_index=len(q.options) - 1)
        state = state.select(2)  # 3.13 is at index 2

        pipeline_ctx = PipelineContext(context, state, mode="select")
        renderer = VerticalLayoutRenderer()
        output = renderer.render(pipeline_ctx)

        # Should show 3.13 with arrow marker
        assert "→" in output
        assert "3.13" in output

        # Should include the explanation for 3.13
        expected_explanation = (
            "Python 3.13 - Latest features, may have some compatibility considerations"
        )
        assert expected_explanation in output, (
            f"Expected explanation not found in output:\n{output}"
        )

        print("\n=== Selected Runtime Option with Explanation ===")
        print(output)
        print()

    def test_selected_package_manager_shows_explanation(self):
        """Test explanation displays for selected package manager option."""
        q = PythonPackageManagerQuestion()

        context = QuestionContext(
            question=q.question_text,
            options=q.options,
            explanations=q.option_explanations,
            question_explanation=q.explanation,
            default_index=1,
            allow_multiple=False,
        )

        # Select poetry (index 2)
        state = SingleSelectionState(selected=1, max_index=len(q.options) - 1)
        state = state.select(2)

        pipeline_ctx = PipelineContext(context, state, mode="select")
        renderer = VerticalLayoutRenderer()
        output = renderer.render(pipeline_ctx)

        # Should show poetry with arrow marker
        assert "→" in output
        assert "poetry" in output

        # Should include the explanation for poetry
        expected_explanation = "Dependency management with lock files, publish to PyPI"
        assert expected_explanation in output, (
            f"Expected explanation not found in output:\n{output}"
        )

        print("\n=== Selected Package Manager Option with Explanation ===")
        print(output)
        print()
