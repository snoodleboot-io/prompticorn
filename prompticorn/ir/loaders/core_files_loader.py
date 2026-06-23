"""Loader for core system and convention files by language."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from prompticorn.source_layouts import get_source_layout
from prompticorn.text_utils import strip_source_header_comments


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

    def __init__(self, core_dir: Path | str = "prompticorn/agents/core"):
        """Initialize with path to core files directory.

        Args:
            core_dir: Path to prompticorn/agents/core directory
        """
        self.core_dir = Path(core_dir)

        # Resolve macro imports (``macros/...``) against the canonical macro
        # library under prompticorn/prompts, matching ConventionGenerator. (The
        # core_dir contains only stub macros; using it as the import root would
        # break convention templates that call the testing/coverage macros.)
        prompts_dir = self.core_dir.parent.parent / "prompts"

        # Create Jinja2 environment with FileSystemLoader for template imports
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(prompts_dir)),
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

        # Always include core files (templated when config is provided so macro
        # imports and {{ }} placeholders are resolved, not emitted raw).
        for filename in ["system.md", "conventions.md", "session.md"]:
            filepath = self.core_dir / filename
            if filepath.exists():
                content = filepath.read_text(encoding="utf-8")
                if config:
                    content = self._template_content(content, config)
                else:
                    content = strip_source_header_comments(content)
                files[filename.replace(".md", "")] = content

        # Conditionally include language conventions
        if language:
            lang_file = self.core_dir / f"conventions-{language}.md"
            if lang_file.exists():
                content = lang_file.read_text(encoding="utf-8")

                # If config provided, template the content
                if config:
                    content = self._template_content(content, config)
                else:
                    content = strip_source_header_comments(content)

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
        # Multi-language-monorepo configs carry a list of folder specs; use the
        # first as the primary spec (matching the builders' language extraction).
        if isinstance(spec, list):
            spec = spec[0] if spec else {}
        abstract_class_style = spec.get("abstract_class_style", "interface")
        repository_type = (config.get("repository") or {}).get("type", "")
        project = config.get("project") or {}

        context = {
            "repository_type": repository_type,
            "source_layout": get_source_layout(
                spec.get("language", ""), project.get("layout_style", "flat")
            ),
            "database": project.get("database", ""),
            "orm": project.get("orm", ""),
            "error_handling": project.get("error_handling", ""),
            "commit_style": project.get("commit_style", ""),
            "pr_size": project.get("pr_size", ""),
            "deploy_target": project.get("deploy_target", ""),
            "language": spec.get("language", ""),
            "runtime": spec.get("runtime", ""),
            "package_manager": spec.get("package_manager", ""),
            "test_framework": spec.get("test_framework", ""),
            "linter": spec.get("linter", ""),
            "formatter": spec.get("formatter", ""),
            "coverage_tool": spec.get("coverage_tool", ""),
            # Must be a dict for the testing/coverage macros; a spec may carry a
            # coverage preset *name* (string), so guard against a non-dict value.
            "coverage_targets": spec.get("coverage")
            if isinstance(spec.get("coverage"), dict)
            else {},
            "abstract_class_style": abstract_class_style,
            # Pass the spec as ``config`` for templates that use ``config.<field>``.
            # Ensure ``abstract_class_style`` is always present so the convention
            # templates' ``{% if config.abstract_class_style %}`` blocks don't fail
            # under StrictUndefined when the spec omits it.
            "config": {**spec, "abstract_class_style": abstract_class_style},
        }

        template = self.jinja_env.from_string(content)
        return strip_source_header_comments(template.render(**context))

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

    def get_language_conventions(self, language: str, config: dict | None = None) -> str | None:
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
        else:
            content = strip_source_header_comments(content)

        return content
