"""Loader for core system and convention files by language."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined


class CoreFilesLoader:
    """Loads core system, conventions, and language-specific convention files.

    Provides language-aware access to core documentation that should be
    included in all agent outputs.

    Example:
        >>> loader = CoreFilesLoader()
        >>> files = loader.get_core_files(language="python")
        >>> "conventions_python" in files
        True
        >>> system = loader.get_system_prompt()
        >>> len(system) > 0
        True
    """

    def __init__(self, core_dir: Path | str = "promptosaurus/agents/core"):
        """Initialize with path to core files directory.

        Args:
            core_dir: Path to promptosaurus/agents/core directory
        """
        self.core_dir = Path(core_dir)

        # Create Jinja2 environment with FileSystemLoader for template imports
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.core_dir)),
            undefined=StrictUndefined,
        )

    def get_core_files(
        self, language: str | None = None, config: dict | None = None
    ) -> dict[str, str]:
        """Get all core files, optionally templated with config values.

        Always includes: system.md, conventions.md, session.md
        Conditionally includes: conventions-{language}.md if language provided

        Args:
            language: Language code (e.g., 'python', 'typescript')
            config: Configuration dict with values to template (spec section)

        Returns:
            Dict with keys: system, conventions, session, language_conventions (if applicable)

        Example:
            >>> loader = CoreFilesLoader()
            >>> files = loader.get_core_files(language="python")
            >>> list(files.keys())
            ['system', 'conventions', 'session', 'conventions_python']
        """
        files = {}

        # Always include core files
        for filename in ["system.md", "conventions.md", "session.md"]:
            filepath = self.core_dir / filename
            if filepath.exists():
                files[filename.replace(".md", "")] = filepath.read_text(encoding="utf-8")

        # Conditionally include language conventions
        if language:
            lang_file = self.core_dir / f"conventions-{language}.md"
            if lang_file.exists():
                content = lang_file.read_text(encoding="utf-8")

                # If config provided, template the content
                if config:
                    content = self._template_content(content, config)

                files[f"conventions_{language}"] = content

        return files

    def _template_content(self, content: str, config: dict) -> str:
        """Template content with Jinja2 using config values.

        Args:
            content: Template content with {{ }} placeholders
            config: Config dict (should have 'spec' key)

        Returns:
            Rendered content with values filled in

        Example:
            >>> loader = CoreFilesLoader()
            >>> config = {"spec": {"language": "python", "runtime": "3.11"}}
            >>> content = "Language: {{ language }}, Runtime: {{ runtime }}"
            >>> result = loader._template_content(content, config)
            >>> result
            'Language: python, Runtime: 3.11'
        """
        spec = config.get("spec", {})

        context = {
            "language": spec.get("language", ""),
            "runtime": spec.get("runtime", ""),
            "package_manager": spec.get("package_manager", ""),
            "test_framework": spec.get("test_framework", ""),
            "linter": spec.get("linter", ""),
            "formatter": spec.get("formatter", ""),
            "coverage_tool": spec.get("coverage_tool", ""),
            "coverage_targets": spec.get("coverage", {}),
            "abstract_class_style": spec.get("abstract_class_style", "interface"),
            "config": spec,  # Also pass full config object for templates that use config.field
        }

        template = self.jinja_env.from_string(content)
        return template.render(**context)

    def get_system_prompt(self) -> str:
        """Get the system.md core file.

        Returns:
            Content of system.md

        Raises:
            FileNotFoundError: If system.md does not exist
        """
        system_file = self.core_dir / "system.md"
        if not system_file.exists():
            raise FileNotFoundError(f"system.md not found at {system_file}")
        return system_file.read_text(encoding="utf-8")

    def get_conventions(self) -> str:
        """Get the conventions.md core file.

        Returns:
            Content of conventions.md

        Raises:
            FileNotFoundError: If conventions.md does not exist
        """
        conventions_file = self.core_dir / "conventions.md"
        if not conventions_file.exists():
            raise FileNotFoundError(f"conventions.md not found at {conventions_file}")
        return conventions_file.read_text(encoding="utf-8")

    def get_session(self) -> str:
        """Get the session.md core file.

        Returns:
            Content of session.md

        Raises:
            FileNotFoundError: If session.md does not exist
        """
        session_file = self.core_dir / "session.md"
        if not session_file.exists():
            raise FileNotFoundError(f"session.md not found at {session_file}")
        return session_file.read_text(encoding="utf-8")

    def get_language_conventions(
        self, language: str, config: dict | None = None
    ) -> str | None:
        """Get language-specific conventions, optionally templated.

        Args:
            language: Language code (e.g., 'python', 'typescript')
            config: Optional config for templating

        Returns:
            Conventions content or None if not found

        Example:
            >>> loader = CoreFilesLoader()
            >>> py_conv = loader.get_language_conventions("python")
            >>> py_conv is not None
            True
            >>> ts_conv = loader.get_language_conventions("nonexistent")
            >>> ts_conv is None
            True
        """
        lang_file = self.core_dir / f"conventions-{language}.md"
        if not lang_file.exists():
            return None

        content = lang_file.read_text(encoding="utf-8")
        if config:
            content = self._template_content(content, config)

        return content
