"""Unit tests for the central tool registry (PRO-30 / F2a).

Locks in that the CLI pickers, name normalization/validation, builder dispatch,
and artifact create-sets all derive from a single ToolSpec registry, and that
the derived values equal the literals they replaced.
"""

import unittest

from prompticorn.tools import (
    MENU_ORDER,
    TOOLS,
    ToolSpec,
    builder_dispatch,
    create_artifacts_by_tool,
    menu_explanations,
    menu_options,
    name_mappings,
    supported_tool_ids,
)


class TestToolRegistry(unittest.TestCase):
    """Verify the registry and everything derived from it."""

    def test_registry_keys_are_ids(self) -> None:
        for tool_id, spec in TOOLS.items():
            self.assertIsInstance(spec, ToolSpec)
            self.assertEqual(tool_id, spec.id)

    def test_supported_tool_ids(self) -> None:
        self.assertEqual(
            supported_tool_ids(),
            {
                "kilo-cli",
                "kilo-ide",
                "claude",
                "cline",
                "cursor",
                "copilot",
                "roo",
                "junie",
                "zed",
                "gemini",
                "amazonq",
                "windsurf",
            },
        )

    def test_name_mappings_match_legacy(self) -> None:
        """Normalized names resolve to canonical ids exactly as before."""
        self.assertEqual(
            name_mappings(),
            {
                "kilocli": "kilo-cli",
                "kiloide": "kilo-ide",
                "cline": "cline",
                "cursor": "cursor",
                "copilot": "copilot",
                "claude": "claude",
                "roo": "roo",
                "roocode": "roo",
                "junie": "junie",
                "zed": "zed",
                "gemini": "gemini",
                "geminicli": "gemini",
                "amazonq": "amazonq",
                "windsurf": "windsurf",
            },
        )

    def test_builder_dispatch_match_legacy(self) -> None:
        """Both kilo ids dispatch to the shared kilo builder."""
        self.assertEqual(
            builder_dispatch(),
            {
                "kilo-cli": "kilo",
                "kilo-ide": "kilo",
                "cline": "cline",
                "cursor": "cursor",
                "copilot": "copilot",
                "claude": "claude",
                "roo": "roo",
                "junie": "junie",
                "zed": "zed",
                "gemini": "gemini",
                "amazonq": "amazonq",
                "windsurf": "windsurf",
            },
        )

    def test_menu_options_order_and_labels(self) -> None:
        self.assertEqual(
            menu_options(),
            [
                "Kilo CLI",
                "Kilo IDE",
                "Claude",
                "Cline",
                "Cursor",
                "Copilot",
                "Roo Code",
                "Junie",
                "Zed",
                "Gemini CLI",
                "Amazon Q",
                "Windsurf",
            ],
        )

    def test_menu_explanations_match_legacy(self) -> None:
        self.assertEqual(
            menu_explanations(),
            {
                "Kilo CLI": "Kilo Code (CLI) - .opencode/rules/ with collapsed mode files",
                "Kilo IDE": "Kilo Code (IDE) - .kilo/agents/ individual agent files",
                "Claude": "Claude - generates .claude/ directory with Markdown agent files and CLAUDE.md",
                "Cline": "Cline - .clinerules file (concatenated rules)",
                "Cursor": "Cursor - .cursor/rules/ directory + .cursorrules",
                "Copilot": "GitHub Copilot - .github/copilot-instructions.md",
                "Roo Code": "Roo Code - .roomodes custom modes + .roo/ rules, skills, and commands",
                "Junie": "JetBrains Junie (CLI) - .junie/ agents, skills, and commands + AGENTS.md",
                "Zed": "Zed - .agents/skills/ (agents-as-skills) + AGENTS.md instructions",
                "Gemini CLI": "Google Gemini CLI - .gemini/ agents, skills, and TOML commands + AGENTS.md",
                "Amazon Q": "Amazon Q Developer CLI - .amazonq/ JSON agents, rules, and prompts",
                "Windsurf": "Windsurf / Cascade - .windsurf/ skills, glob-scoped rules, and workflows",
            },
        )

    def test_create_artifacts_match_legacy_and_order(self) -> None:
        create = create_artifacts_by_tool()
        self.assertEqual(
            create,
            {
                "kilo-cli": {".opencode/"},
                "kilo-ide": {".kilo/"},
                "cline": {".clinerules"},
                "cursor": {".cursor/", ".cursorrules"},
                "copilot": {".github/copilot-instructions.md"},
                "claude": {".claude/", "CLAUDE.md"},
                "roo": {".roomodes", ".roo/"},
                "junie": {".junie/"},
                "zed": {".agents/"},
                "gemini": {".gemini/"},
                "amazonq": {".amazonq/"},
                "windsurf": {".windsurf/"},
            },
        )
        # The six original tools keep their historical ordering so that
        # ArtifactManager.current_tool first-match detection is unchanged; new
        # tools append after them.
        self.assertEqual(
            list(create)[:6],
            ["kilo-cli", "kilo-ide", "cline", "cursor", "copilot", "claude"],
        )

    def test_menu_order_covers_every_tool(self) -> None:
        self.assertEqual(set(MENU_ORDER), set(TOOLS))

    def test_create_artifacts_are_mutable_copies(self) -> None:
        """Callers get independent mutable sets, not the frozen registry data."""
        a = create_artifacts_by_tool()
        a["claude"].add("SENTINEL")
        self.assertNotIn("SENTINEL", create_artifacts_by_tool()["claude"])


if __name__ == "__main__":
    unittest.main()
