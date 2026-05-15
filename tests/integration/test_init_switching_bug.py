"""Test to reproduce the init tool switching bug."""

import shutil
import unittest
from pathlib import Path

from prompticorn.artifacts import ArtifactManager
from prompticorn.prompt_builder import get_prompt_builder


class TestInitSwitchingBug(unittest.TestCase):
    """Reproduce: Running init to switch from Kilo to Claude."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(".test_init_bug")
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(parents=True)

    def tearDown(self):
        """Clean up test artifacts."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_init_kilo_then_init_claude(self):
        """Reproduce the bug: Init with Kilo, then init with Claude.

        Expected:
        1. First init creates .kilo/ files only
        2. Second init removes .kilo/ and creates .claude/ files only
        3. Final state: .claude/ and custom_instructions/ exist, .kilo/ does not

        Bug:
        Both .kilo/ and .claude/ exist after second init
        """
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }

        # STEP 1: Initialize with Kilo IDE
        print("\n=== STEP 1: Init with Kilo IDE ===")
        kilo_builder = get_prompt_builder("kilo-ide")
        kilo_builder.build(self.test_dir, config, dry_run=False)

        # Verify Kilo artifacts exist
        kilo_exists = (self.test_dir / ".kilo").exists()
        claude_exists = (self.test_dir / ".claude").exists()
        custom_exists = (self.test_dir / "custom_instructions").exists()

        print(
            f"After Kilo init: .kilo/={kilo_exists}, .claude/={claude_exists}, custom_instructions/={custom_exists}"
        )
        self.assertTrue(kilo_exists, ".kilo/ should exist")
        self.assertFalse(claude_exists, ".claude/ should NOT exist yet")
        self.assertFalse(custom_exists, "custom_instructions/ should NOT exist yet")

        # STEP 2: Detect current tool and remove its artifacts (like init does)
        print("\n=== STEP 2: Detect tool and remove old artifacts ===")
        manager = ArtifactManager(self.test_dir)
        current_tool = manager.current_tool
        print(f"Detected current tool: {current_tool}")

        self.assertEqual(current_tool, "kilo-ide", "Should detect kilo-ide")

        # Remove old artifacts
        removal_actions = manager.remove_artifacts_created_by(current_tool)
        print(f"Removal actions: {removal_actions}")

        # Verify kilo is removed
        kilo_exists = (self.test_dir / ".kilo").exists()
        print(f"After removal: .kilo/={kilo_exists}")
        self.assertFalse(kilo_exists, ".kilo/ should be removed")

        # STEP 3: Build with Claude (like init does after removing old artifacts)
        print("\n=== STEP 3: Build with Claude ===")
        claude_builder = get_prompt_builder("claude")
        claude_builder.build(self.test_dir, config, dry_run=False)

        # STEP 4: Final verification
        print("\n=== STEP 4: Final state ===")
        kilo_exists = (self.test_dir / ".kilo").exists()
        claude_exists = (self.test_dir / ".claude").exists()
        claude_md_exists = (self.test_dir / "CLAUDE.md").exists()

        print(
            f"Final state: .kilo/={kilo_exists}, .claude/={claude_exists}, CLAUDE.md={claude_md_exists}"
        )

        # Assertions
        self.assertFalse(kilo_exists, "BUG: .kilo/ should NOT exist after switching to Claude")
        self.assertTrue(claude_exists, ".claude/ should exist for Claude")
        self.assertTrue(claude_md_exists, "CLAUDE.md should exist for Claude")

        # Check that only Claude agents exist
        kilo_agents = (
            list((self.test_dir / ".kilo").glob("*")) if (self.test_dir / ".kilo").exists() else []
        )
        self.assertEqual(len(kilo_agents), 0, "No .kilo files should exist")


if __name__ == "__main__":
    unittest.main()
