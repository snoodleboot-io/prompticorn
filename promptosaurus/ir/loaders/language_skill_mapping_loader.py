"""Loader for language-skill-workflow mappings."""

from pathlib import Path
from typing import Optional

import yaml


class LanguageSkillMappingLoader:
    """Loads language to skills/workflows mapping from YAML registry.

    Provides resolution of which skills and workflows apply to a given
    language and subagent combination. Uses a priority-based resolution
    system to determine applicability.

    Example:
        >>> loader = LanguageSkillMappingLoader()
        >>> skills = loader.get_skills_for_language("python", "code/feature")
        >>> isinstance(skills, list)
        True
        >>> workflows = loader.get_workflows_for_language("python")
        >>> isinstance(workflows, list)
        True
    """

    def __init__(self, mapping_file: Path | str = "language_skill_mapping.yaml"):
        """Initialize with path to mapping file.

        Args:
            mapping_file: Path to language_skill_mapping.yaml

        Raises:
            FileNotFoundError: If mapping file does not exist
        """
        self.mapping_file = Path(mapping_file)
        if not self.mapping_file.exists():
            raise FileNotFoundError(f"Mapping file not found: {self.mapping_file}")
        self._mapping = None

    @property
    def mapping(self) -> dict:
        """Lazy-load mapping YAML.

        Returns:
            Parsed YAML mapping dictionary
        """
        if self._mapping is None:
            with open(self.mapping_file, encoding="utf-8") as f:
                self._mapping = yaml.safe_load(f) or {}
        return self._mapping

    def get_skills_for_language(self, language: str, subagent: Optional[str] = None) -> list[str]:
        """Get skills for a language and optional subagent.

        Resolution priority:
        1. {language}/{subagent} - Most specific (exact match)
        2. {language} - Language level
        3. all - Global defaults

        Args:
            language: Language code (e.g., 'python')
            subagent: Subagent path (e.g., 'code/feature'), optional

        Returns:
            List of skill names in resolution order, deduplicated

        Example:
            >>> loader = LanguageSkillMappingLoader()
            >>> python_skills = loader.get_skills_for_language("python")
            >>> python_code_skills = loader.get_skills_for_language("python", "code/feature")
            >>> len(python_code_skills) >= len(python_skills)
            True
        """
        return self._resolve(language, subagent, "skills")

    def get_workflows_for_language(
        self, language: str, subagent: Optional[str] = None
    ) -> list[str]:
        """Get workflows for a language and optional subagent.

        Uses the same resolution priority as get_skills_for_language.

        Args:
            language: Language code (e.g., 'python')
            subagent: Subagent path (e.g., 'code/feature'), optional

        Returns:
            List of workflow names in resolution order, deduplicated

        Example:
            >>> loader = LanguageSkillMappingLoader()
            >>> workflows = loader.get_workflows_for_language("typescript")
            >>> isinstance(workflows, list)
            True
        """
        return self._resolve(language, subagent, "workflows")

    def _resolve(self, language: str, subagent: Optional[str], key: str) -> list[str]:
        """Resolve skills or workflows using priority chain.

        Priority:
        1. {language}/{subagent} - Most specific
        2. {language} - Language level
        3. all - Global defaults

        Args:
            language: Language code
            subagent: Subagent path, optional
            key: "skills" or "workflows"

        Returns:
            List of resolved items with duplicates removed, order preserved
        """
        result = []

        # Add global defaults first
        if "all" in self.mapping and key in self.mapping["all"]:
            result.extend(self.mapping["all"][key])

        # Add language-level
        if language in self.mapping and key in self.mapping[language]:
            result.extend(self.mapping[language][key])

        # Add language+subagent combination (these might override above)
        if subagent:
            full_key = f"{language}/{subagent}"
            if full_key in self.mapping and key in self.mapping[full_key]:
                # For specific combinations, use exact match instead of accumulating
                # This allows language/subagent entries to be definitive
                result = self.mapping[full_key][key]

        # Remove duplicates while preserving order
        seen = set()
        return [x for x in result if not (x in seen or seen.add(x))]

    def get_all_mappings(self) -> dict:
        """Get the entire mapping dictionary.

        Returns:
            Copy of the complete mapping dictionary

        Example:
            >>> loader = LanguageSkillMappingLoader()
            >>> mappings = loader.get_all_mappings()
            >>> "all" in mappings
            True
        """
        return self.mapping.copy()

    def has_language(self, language: str) -> bool:
        """Check if a language has specific mappings.

        Args:
            language: Language code

        Returns:
            True if language has entries in mapping
        """
        return language in self.mapping

    def has_subagent(self, language: str, subagent: str) -> bool:
        """Check if a language/subagent combination has specific mappings.

        Args:
            language: Language code
            subagent: Subagent path

        Returns:
            True if language/subagent has entries in mapping
        """
        full_key = f"{language}/{subagent}"
        return full_key in self.mapping
