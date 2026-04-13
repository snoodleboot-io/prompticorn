"""Tests for PromptBuilder with multi-language-monorepo configurations."""

import pytest
from pathlib import Path
from promptosaurus.prompt_builder import PromptBuilder


class TestLanguageExtraction:
    """Tests for _extract_language_from_config method."""

    def test_extract_language_single_language_config(self):
        """Should extract language from single-language config (dict spec)."""
        config = {
            "variant": "minimal",
            "spec": {
                "language": "python",
                "runtime": "3.14",
                "package_manager": "uv",
            },
        }
        
        language = PromptBuilder._extract_language_from_config(config)
        
        assert language == "python"

    def test_extract_language_multi_language_config(self):
        """Should extract primary language from multi-language-monorepo config (list spec)."""
        config = {
            "variant": "minimal",
            "repository": {"type": "multi-language-monorepo"},
            "spec": [
                {
                    "folder": "backend/api",
                    "type": "backend",
                    "subtype": "api",
                    "language": "python",
                    "runtime": "3.14",
                },
                {
                    "folder": "frontend/ui",
                    "type": "frontend",
                    "subtype": "ui",
                    "language": "typescript",
                    "runtime": "node-20",
                },
            ],
        }
        
        language = PromptBuilder._extract_language_from_config(config)
        
        # Should use first folder's language as primary
        assert language == "python"

    def test_extract_language_empty_config(self):
        """Should return None for None config."""
        language = PromptBuilder._extract_language_from_config(None)
        assert language is None

    def test_extract_language_no_spec(self):
        """Should return None for config without spec."""
        config = {"variant": "minimal"}
        language = PromptBuilder._extract_language_from_config(config)
        assert language is None

    def test_extract_language_empty_spec_dict(self):
        """Should return None for empty spec dict."""
        config = {"variant": "minimal", "spec": {}}
        language = PromptBuilder._extract_language_from_config(config)
        assert language is None

    def test_extract_language_empty_spec_list(self):
        """Should return None for empty spec list."""
        config = {"variant": "minimal", "spec": []}
        language = PromptBuilder._extract_language_from_config(config)
        assert language is None

    def test_extract_language_spec_dict_no_language(self):
        """Should return None for spec dict without language key."""
        config = {"variant": "minimal", "spec": {"runtime": "3.14"}}
        language = PromptBuilder._extract_language_from_config(config)
        assert language is None

    def test_extract_language_spec_list_first_no_language(self):
        """Should return None if first folder spec has no language."""
        config = {
            "variant": "minimal",
            "spec": [
                {"folder": "backend/api", "type": "backend"},
                {"folder": "frontend/ui", "language": "typescript"},
            ],
        }
        language = PromptBuilder._extract_language_from_config(config)
        assert language is None  # First folder has no language

    def test_extract_language_multi_language_second_folder(self):
        """Should use first folder's language even if second has different language."""
        config = {
            "variant": "minimal",
            "spec": [
                {"folder": "frontend", "language": "typescript"},
                {"folder": "backend", "language": "python"},
            ],
        }
        language = PromptBuilder._extract_language_from_config(config)
        assert language == "typescript"  # First folder's language

    def test_extract_language_with_three_folders(self):
        """Should handle multi-language-monorepo with 3+ folders."""
        config = {
            "variant": "minimal",
            "spec": [
                {"folder": "api", "language": "python"},
                {"folder": "web", "language": "typescript"},
                {"folder": "mobile", "language": "dart"},
            ],
        }
        language = PromptBuilder._extract_language_from_config(config)
        assert language == "python"  # First folder's language


class TestPromptBuilderMultiLanguage:
    """Integration tests for PromptBuilder with multi-language-monorepo."""

    @pytest.fixture
    def builder(self):
        """Create a PromptBuilder instance for testing."""
        return PromptBuilder("kilo")

    def test_build_with_single_language_config(self, builder, tmp_path):
        """Should build successfully with single-language config."""
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": [],
        }
        
        # This should not raise an exception
        actions = builder.build(tmp_path, config=config, dry_run=True)
        
        assert isinstance(actions, list)
        # dry_run=True may return empty list, just verify no exception

    def test_build_with_multi_language_config(self, builder, tmp_path):
        """Should build successfully with multi-language-monorepo config."""
        config = {
            "variant": "minimal",
            "repository": {"type": "multi-language-monorepo"},
            "spec": [
                {"folder": "backend", "language": "python"},
                {"folder": "frontend", "language": "typescript"},
            ],
            "active_personas": [],
        }
        
        # This should not raise an exception (the bug fix)
        actions = builder.build(tmp_path, config=config, dry_run=True)
        
        assert isinstance(actions, list)
        # dry_run=True may return empty list, just verify no exception

    def test_build_with_multi_language_and_personas(self, builder, tmp_path):
        """Should build successfully with multi-language config AND persona filtering."""
        config = {
            "variant": "minimal",
            "repository": {"type": "multi-language-monorepo"},
            "spec": [
                {"folder": "backend/api", "language": "python"},
                {"folder": "frontend/web", "language": "typescript"},
            ],
            "active_personas": ["software_engineer", "architect"],
        }
        
        # This tests the combination of persona filtering + multi-language
        actions = builder.build(tmp_path, config=config, dry_run=True)
        
        assert isinstance(actions, list)
        # Should have built some agents
        assert len(actions) > 0
        # Should have persona filtering messages
        persona_msgs = [a for a in actions if "Persona filtering" in a]
        assert len(persona_msgs) > 0

    def test_build_with_no_config(self, builder, tmp_path):
        """Should handle None config gracefully."""
        # This should not raise an exception
        actions = builder.build(tmp_path, config=None, dry_run=True)
        
        assert isinstance(actions, list)
        # dry_run=True may return empty list, just verify no exception

    def test_build_with_empty_spec_list(self, builder, tmp_path):
        """Should handle empty spec list gracefully."""
        config = {
            "variant": "minimal",
            "repository": {"type": "multi-language-monorepo"},
            "spec": [],  # Empty list
            "active_personas": [],
        }
        
        # This should not raise an exception
        actions = builder.build(tmp_path, config=config, dry_run=True)
        
        assert isinstance(actions, list)
