"""Loader for core system and convention files by language."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from prompticorn.content.content_resolver import ContentResolver, default_resolver
from prompticorn.content.errors import InvalidUnitIdError
from prompticorn.content.unit_id import UnitId
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

    def __init__(self, resolver: ContentResolver | None = None):
        """Initialize with a content resolver.

        Previously this took ``core_dir`` defaulting to the **CWD-relative**
        ``"prompticorn/agents/core"``, so every core file silently vanished
        whenever the process ran from anywhere but the repository root — which
        is always, for an installed package. Content now comes from the
        resolver, which addresses the bundled tree from the package's own
        location. (PRO-105)

        Args:
            resolver: Where core conventions are read from. Defaults to the
                process-wide resolver over the bundled tree.
        """
        self._resolver = resolver if resolver is not None else default_resolver()

        # Resolve macro imports (``macros/...``) against the canonical macro
        # library under prompticorn/prompts, matching ConventionGenerator. This
        # is a Jinja template root rather than addressable content, so it stays
        # a path — but a package-relative one.
        prompts_dir = Path(__file__).resolve().parents[2] / "prompts"

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
        for name in ["system", "conventions", "session"]:
            content = self.read_core(name)
            if content is not None:
                if config:
                    content = self._template_content(content, config)
                else:
                    content = strip_source_header_comments(content)
                files[name] = content

        # Conditionally include language conventions
        if language:
            content = self.read_language(language)
            if content is not None:
                # If config provided, template the content
                if config:
                    content = self._template_content(content, config)
                else:
                    content = strip_source_header_comments(content)

                files[f"conventions_{language}"] = content

        return files

    def read_core(self, name: str) -> str | None:
        """Raw text of a core convention (``system``, ``conventions``, …).

        Returns None when absent, preserving the previous ``if path.exists()``
        semantics for callers that treat core files as optional.
        """
        return self._read(f"convention/core/{name}")

    def read_language(self, language: str) -> str | None:
        """Raw text of a language convention, or None when the language has none."""
        return self._read(f"convention/language/{language}")

    def _read(self, raw_unit_id: str) -> str | None:
        try:
            unit_id = UnitId.parse(raw_unit_id)
        except InvalidUnitIdError:
            # A config may name a language that is not a legal unit segment
            # (uppercase, punctuation). Previously that simply missed the file;
            # keep it a miss rather than raising into the build.
            return None
        return self._resolver.read_optional(unit_id)

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

        # Data-system (databases / data_access) and layout/error-handling settings
        # are per-folder/per-language spec values. Derive the scalar template vars
        # from the primary spec's multi-select lists (comma-joined).
        databases = spec.get("databases") or []
        data_access = spec.get("data_access") or []

        context = {
            "repository_type": repository_type,
            "source_layout": get_source_layout(
                spec.get("language", ""), spec.get("layout_style", "flat")
            ),
            "databases": ", ".join(databases),
            "data_access": ", ".join(data_access),
            "error_handling": spec.get("error_handling", ""),
            "commit_style": project.get("commit_style", ""),
            "pr_size": project.get("pr_size", ""),
            "deploy_target": project.get("deploy_target", ""),
            "language": spec.get("language", ""),
            "runtime": spec.get("runtime", ""),
            "engine": spec.get("engine", ""),
            "package_manager": spec.get("package_manager", ""),
            "test_framework": spec.get("test_framework", ""),
            "linter": spec.get("linter", ""),
            "linters": spec.get("linters", ""),
            "formatter": spec.get("formatter", ""),
            # Testing-tool selections (PRO-69) — rendered by the conventions.
            "test_runner": spec.get("test_runner", ""),
            "mocking_library": spec.get("mocking_library", ""),
            "coverage_tool": spec.get("coverage_tool", ""),
            "mutation_tool": spec.get("mutation_tool", ""),
            "framework": spec.get("framework", ""),
            # Language-specific identity/build selections (PRO-83).
            "compiler": spec.get("compiler", ""),
            "build_tool": spec.get("build_tool", ""),
            "sql_dialect": spec.get("sql_dialect", ""),
            "shell_type": spec.get("shell_type", ""),
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
        content = self.read_core("system")
        if content is None:
            raise FileNotFoundError("system.md not found in the resolved content")
        return content

    def get_conventions(self) -> str:
        """Get the conventions.md core file.

        Returns:
            Content of conventions.md

        Raises:
            FileNotFoundError: If conventions.md does not exist
        """
        content = self.read_core("conventions")
        if content is None:
            raise FileNotFoundError("conventions.md not found in the resolved content")
        return content

    def get_session(self) -> str:
        """Get the session.md core file.

        Returns:
            Content of session.md

        Raises:
            FileNotFoundError: If session.md does not exist
        """
        content = self.read_core("session")
        if content is None:
            raise FileNotFoundError("session.md not found in the resolved content")
        return content

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
        content = self.read_language(language)
        if content is None:
            return None

        if config:
            content = self._template_content(content, config)
        else:
            content = strip_source_header_comments(content)

        return content
