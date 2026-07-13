"""Integration tests for tool switching during init."""

import shutil
import unittest
from pathlib import Path

from prompticorn.artifacts import ArtifactManager
from prompticorn.prompt_builder import get_prompt_builder


class TestToolSwitching(unittest.TestCase):
    """Test tool selection and switching behavior."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(".test_switching")
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(parents=True)

    def tearDown(self):
        """Clean up test artifacts."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_get_prompt_builder_for_claude(self):
        """Test that get_prompt_builder returns correct builder for claude."""
        builder = get_prompt_builder("claude")
        self.assertIsNotNone(builder)
        # The tool_name should be "claude"
        self.assertEqual(builder.tool_name, "claude")

    def test_get_prompt_builder_for_kilo_ide(self):
        """Test that get_prompt_builder returns correct builder for kilo-ide."""
        builder = get_prompt_builder("kilo-ide")
        self.assertIsNotNone(builder)
        # The tool_name should be "kilo" (internal name)
        self.assertEqual(builder.tool_name, "kilo")

    def test_builder_creates_correct_artifacts_claude(self):
        """Test that claude builder creates .claude/ not .kilo/."""
        builder = get_prompt_builder("claude")
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }

        # Build
        _actions = builder.build(self.test_dir, config, dry_run=False)

        # Check what was created
        claude_exists = (self.test_dir / ".claude").exists()
        kilo_exists = (self.test_dir / ".kilo").exists()
        claude_md_exists = (self.test_dir / "CLAUDE.md").exists()

        # Verify: Claude artifacts should exist
        self.assertTrue(claude_exists, ".claude/ should exist for claude tool")
        self.assertTrue(claude_md_exists, "CLAUDE.md should exist for claude tool")

        # Verify: Kilo artifacts should NOT exist
        self.assertFalse(kilo_exists, ".kilo/ should NOT exist for claude tool")

    def test_builder_creates_correct_artifacts_kilo_ide(self):
        """Test that kilo-ide builder creates .kilo/ not .claude/."""
        builder = get_prompt_builder("kilo-ide")
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }

        # Build
        _actions = builder.build(self.test_dir, config, dry_run=False)

        # Check what was created
        kilo_exists = (self.test_dir / ".kilo").exists()
        claude_exists = (self.test_dir / ".claude").exists()
        custom_exists = (self.test_dir / "custom_instructions").exists()

        # Verify: Kilo artifacts should exist
        self.assertTrue(kilo_exists, ".kilo/ should exist for kilo-ide tool")

        # Verify: Claude artifacts should NOT exist
        self.assertFalse(claude_exists, ".claude/ should NOT exist for kilo-ide tool")
        self.assertFalse(custom_exists, "custom_instructions/ should NOT exist for kilo-ide tool")

        # Verify AGENTS.md was created
        agents_md = self.test_dir / "AGENTS.md"
        self.assertTrue(agents_md.exists(), "AGENTS.md should be created")

    def test_switching_kilo_to_claude_cleans_kilo(self):
        """Test that switching from kilo-ide to claude removes .kilo/ and creates .claude/."""
        # Step 1: Build with kilo-ide
        kilo_builder = get_prompt_builder("kilo-ide")
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }
        kilo_builder.build(self.test_dir, config, dry_run=False)

        # Verify kilo artifacts exist
        self.assertTrue((self.test_dir / ".kilo").exists())
        self.assertFalse((self.test_dir / ".claude").exists())

        # Step 2: Clean up old artifacts (simulate init removal)
        manager = ArtifactManager(self.test_dir)
        current = manager.current_tool
        self.assertEqual(current, "kilo-ide")

        manager.remove_artifacts_created_by(current)

        # Verify kilo is removed
        self.assertFalse((self.test_dir / ".kilo").exists())

        # Step 3: Build with claude
        claude_builder = get_prompt_builder("claude")
        claude_builder.build(self.test_dir, config, dry_run=False)

        # Verify final state: Only claude exists
        self.assertTrue((self.test_dir / ".claude").exists())
        self.assertTrue((self.test_dir / "CLAUDE.md").exists())
        self.assertFalse((self.test_dir / ".kilo").exists())

    def test_builder_creates_correct_artifacts_roo(self):
        """Roo builder creates .roomodes + .roo/, detectable and cleanable."""
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }
        get_prompt_builder("roo").build(self.test_dir, config, dry_run=False)

        # Roo artifacts exist; other tools' do not
        self.assertTrue((self.test_dir / ".roomodes").exists())
        self.assertTrue((self.test_dir / ".roo").exists())
        self.assertFalse((self.test_dir / ".kilo").exists())
        self.assertFalse((self.test_dir / ".claude").exists())

        # Detected as the current tool
        manager = ArtifactManager(self.test_dir)
        self.assertEqual(manager.current_tool, "roo")

        # Switching away removes Roo's artifacts
        manager.remove_artifacts_created_by("roo")
        self.assertFalse((self.test_dir / ".roomodes").exists())
        self.assertFalse((self.test_dir / ".roo").exists())

    def test_switching_claude_to_roo_cleans_claude(self):
        """Switching from claude to roo removes .claude/CLAUDE.md and creates Roo files."""
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }
        get_prompt_builder("claude").build(self.test_dir, config, dry_run=False)
        self.assertTrue((self.test_dir / ".claude").exists())

        manager = ArtifactManager(self.test_dir)
        manager.remove_artifacts_created_by(manager.current_tool)
        self.assertFalse((self.test_dir / ".claude").exists())
        self.assertFalse((self.test_dir / "CLAUDE.md").exists())

        get_prompt_builder("roo").build(self.test_dir, config, dry_run=False)
        self.assertTrue((self.test_dir / ".roomodes").exists())
        self.assertFalse((self.test_dir / ".claude").exists())

    def test_builder_creates_correct_artifacts_junie(self):
        """Junie builder creates .junie/ (agents), detectable and cleanable."""
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }
        get_prompt_builder("junie").build(self.test_dir, config, dry_run=False)

        self.assertTrue((self.test_dir / ".junie" / "agents").exists())
        self.assertFalse((self.test_dir / ".kilo").exists())
        self.assertFalse((self.test_dir / ".claude").exists())

        manager = ArtifactManager(self.test_dir)
        self.assertEqual(manager.current_tool, "junie")

        manager.remove_artifacts_created_by("junie")
        self.assertFalse((self.test_dir / ".junie").exists())

    def test_switching_junie_to_roo_cleans_junie(self):
        """Switching from junie to roo removes .junie/ and creates Roo files."""
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }
        get_prompt_builder("junie").build(self.test_dir, config, dry_run=False)
        self.assertTrue((self.test_dir / ".junie").exists())

        manager = ArtifactManager(self.test_dir)
        manager.remove_artifacts_created_by(manager.current_tool)
        self.assertFalse((self.test_dir / ".junie").exists())

        get_prompt_builder("roo").build(self.test_dir, config, dry_run=False)
        self.assertTrue((self.test_dir / ".roomodes").exists())
        self.assertFalse((self.test_dir / ".junie").exists())

    def test_builder_creates_correct_artifacts_zed(self):
        """Zed builder creates .agents/skills/, detectable and cleanable."""
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }
        get_prompt_builder("zed").build(self.test_dir, config, dry_run=False)

        self.assertTrue((self.test_dir / ".agents" / "skills").exists())
        self.assertFalse((self.test_dir / ".junie").exists())
        self.assertFalse((self.test_dir / ".claude").exists())

        manager = ArtifactManager(self.test_dir)
        self.assertEqual(manager.current_tool, "zed")

        manager.remove_artifacts_created_by("zed")
        self.assertFalse((self.test_dir / ".agents").exists())

    def test_switching_zed_to_junie_cleans_zed(self):
        """Switching from zed to junie removes .agents/ and creates .junie/."""
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }
        get_prompt_builder("zed").build(self.test_dir, config, dry_run=False)
        self.assertTrue((self.test_dir / ".agents").exists())

        manager = ArtifactManager(self.test_dir)
        manager.remove_artifacts_created_by(manager.current_tool)
        self.assertFalse((self.test_dir / ".agents").exists())

        get_prompt_builder("junie").build(self.test_dir, config, dry_run=False)
        self.assertTrue((self.test_dir / ".junie").exists())
        self.assertFalse((self.test_dir / ".agents").exists())

    def test_builder_creates_correct_artifacts_gemini(self):
        """Gemini builder creates .gemini/ (agents + settings), detectable and cleanable."""
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }
        get_prompt_builder("gemini").build(self.test_dir, config, dry_run=False)

        self.assertTrue((self.test_dir / ".gemini" / "agents").exists())
        self.assertTrue((self.test_dir / ".gemini" / "settings.json").exists())
        self.assertFalse((self.test_dir / ".junie").exists())
        self.assertFalse((self.test_dir / ".claude").exists())

        manager = ArtifactManager(self.test_dir)
        self.assertEqual(manager.current_tool, "gemini")

        manager.remove_artifacts_created_by("gemini")
        self.assertFalse((self.test_dir / ".gemini").exists())

    def test_switching_gemini_to_claude_cleans_gemini(self):
        """Switching from gemini to claude removes .gemini/ and creates .claude/."""
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }
        get_prompt_builder("gemini").build(self.test_dir, config, dry_run=False)
        self.assertTrue((self.test_dir / ".gemini").exists())

        manager = ArtifactManager(self.test_dir)
        manager.remove_artifacts_created_by(manager.current_tool)
        self.assertFalse((self.test_dir / ".gemini").exists())

        get_prompt_builder("claude").build(self.test_dir, config, dry_run=False)
        self.assertTrue((self.test_dir / ".claude").exists())
        self.assertFalse((self.test_dir / ".gemini").exists())

    def test_builder_creates_correct_artifacts_amazonq(self):
        """Amazon Q creates .amazonq/ (no AGENTS.md), detectable and cleanable."""
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }
        get_prompt_builder("amazonq").build(self.test_dir, config, dry_run=False)

        self.assertTrue((self.test_dir / ".amazonq" / "cli-agents").exists())
        self.assertTrue((self.test_dir / ".amazonq" / "rules").exists())
        # Amazon Q does not read AGENTS.md — it must not be emitted.
        self.assertFalse((self.test_dir / "AGENTS.md").exists())
        self.assertFalse((self.test_dir / ".claude").exists())

        manager = ArtifactManager(self.test_dir)
        self.assertEqual(manager.current_tool, "amazonq")

        manager.remove_artifacts_created_by("amazonq")
        self.assertFalse((self.test_dir / ".amazonq").exists())

    def test_switching_amazonq_to_kilo_cleans_amazonq(self):
        """Switching from amazonq to kilo-ide removes .amazonq/ and creates .kilo/."""
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }
        get_prompt_builder("amazonq").build(self.test_dir, config, dry_run=False)
        self.assertTrue((self.test_dir / ".amazonq").exists())

        manager = ArtifactManager(self.test_dir)
        manager.remove_artifacts_created_by(manager.current_tool)
        self.assertFalse((self.test_dir / ".amazonq").exists())

        get_prompt_builder("kilo-ide").build(self.test_dir, config, dry_run=False)
        self.assertTrue((self.test_dir / ".kilo").exists())
        self.assertFalse((self.test_dir / ".amazonq").exists())

    def test_builder_creates_correct_artifacts_windsurf(self):
        """Windsurf creates .windsurf/ (no AGENTS.md), detectable and cleanable."""
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }
        get_prompt_builder("windsurf").build(self.test_dir, config, dry_run=False)

        self.assertTrue((self.test_dir / ".windsurf" / "rules").exists())
        self.assertTrue((self.test_dir / ".windsurf" / "skills").exists())
        # Windsurf conventions live in .windsurf/rules/, not AGENTS.md (char budget).
        self.assertFalse((self.test_dir / "AGENTS.md").exists())
        self.assertFalse((self.test_dir / ".claude").exists())

        manager = ArtifactManager(self.test_dir)
        self.assertEqual(manager.current_tool, "windsurf")

        manager.remove_artifacts_created_by("windsurf")
        self.assertFalse((self.test_dir / ".windsurf").exists())

    def test_switching_windsurf_to_cursor_cleans_windsurf(self):
        """Switching from windsurf to cursor removes .windsurf/ and creates cursor files."""
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }
        get_prompt_builder("windsurf").build(self.test_dir, config, dry_run=False)
        self.assertTrue((self.test_dir / ".windsurf").exists())

        manager = ArtifactManager(self.test_dir)
        manager.remove_artifacts_created_by(manager.current_tool)
        self.assertFalse((self.test_dir / ".windsurf").exists())

        get_prompt_builder("cursor").build(self.test_dir, config, dry_run=False)
        self.assertTrue((self.test_dir / ".cursorrules").exists())
        self.assertFalse((self.test_dir / ".windsurf").exists())

    def test_builder_creates_correct_artifacts_continue(self):
        """Continue creates .continue/ (no AGENTS.md), detectable and cleanable."""
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }
        get_prompt_builder("continue").build(self.test_dir, config, dry_run=False)

        self.assertTrue((self.test_dir / ".continue" / "rules").exists())
        self.assertTrue((self.test_dir / ".continue" / "prompts").exists())
        # Continue conventions live in .continue/rules/, not AGENTS.md.
        self.assertFalse((self.test_dir / "AGENTS.md").exists())
        self.assertFalse((self.test_dir / ".claude").exists())

        manager = ArtifactManager(self.test_dir)
        self.assertEqual(manager.current_tool, "continue")

        manager.remove_artifacts_created_by("continue")
        self.assertFalse((self.test_dir / ".continue").exists())

    def test_switching_continue_to_cline_cleans_continue(self):
        """Switching from continue to cline removes .continue/ and creates .clinerules."""
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }
        get_prompt_builder("continue").build(self.test_dir, config, dry_run=False)
        self.assertTrue((self.test_dir / ".continue").exists())

        manager = ArtifactManager(self.test_dir)
        manager.remove_artifacts_created_by(manager.current_tool)
        self.assertFalse((self.test_dir / ".continue").exists())

        get_prompt_builder("cline").build(self.test_dir, config, dry_run=False)
        self.assertTrue((self.test_dir / ".clinerules").exists())
        self.assertFalse((self.test_dir / ".continue").exists())


if __name__ == "__main__":
    unittest.main()

    def test_subagents_only_written_for_kilo(self):
        """Test that subagents are ONLY written for Kilo, not for other tools."""
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }

        # Build with Claude
        claude_builder = get_prompt_builder("claude")
        claude_builder.build(self.test_dir, config, dry_run=False)

        # Check: .kilo/agents should NOT exist
        kilo_agents = self.test_dir / ".kilo" / "agents"
        self.assertFalse(
            kilo_agents.exists(),
            "BUG: .kilo/agents/ should NOT be created when building for Claude",
        )

        # Check: .claude/ should exist
        claude_dir = self.test_dir / ".claude"
        self.assertTrue(claude_dir.exists(), ".claude/ should exist for Claude")

        # Build with Kilo (separate test dir to avoid conflicts)
        kilo_test_dir = Path(".test_kilo_subagents")
        if kilo_test_dir.exists():
            shutil.rmtree(kilo_test_dir)
        kilo_test_dir.mkdir()

        try:
            kilo_builder = get_prompt_builder("kilo-ide")
            kilo_builder.build(kilo_test_dir, config, dry_run=False)

            # Check: .kilo/agents SHOULD exist
            kilo_agents = kilo_test_dir / ".kilo" / "agents"
            self.assertTrue(
                kilo_agents.exists(), ".kilo/agents/ MUST be created when building for Kilo"
            )

            # Verify some subagents exist
            subagent_files = list(kilo_agents.glob("*/*.md"))
            self.assertTrue(
                len(subagent_files) > 0,
                "Kilo should have subagent files in .kilo/agents/{agent}/{subagent}.md",
            )
        finally:
            if kilo_test_dir.exists():
                shutil.rmtree(kilo_test_dir)
