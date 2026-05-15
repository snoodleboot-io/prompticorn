"""Test that mimics the exact init command flow."""

import shutil
import unittest
from pathlib import Path

from prompticorn.artifacts import ArtifactManager
from prompticorn.cli_utils import normalize_tool_name
from prompticorn.prompt_builder import get_prompt_builder


class TestInitFlow(unittest.TestCase):
    """Test the exact flow of the init command."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(".test_init_flow")
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(parents=True)

    def tearDown(self):
        """Clean up test artifacts."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_exact_init_flow_switch_kilo_to_claude(self):
        """Test exact flow: init with Kilo, then switch to Claude via init."""
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": ["software_engineer"],
        }

        # INITIAL: Build with Kilo IDE
        print("\n=== INITIAL: Build with Kilo IDE ===")
        kilo_builder = get_prompt_builder("kilo-ide")
        actions = kilo_builder.build(self.test_dir, config, dry_run=False)
        print(f"Built {len(actions)} artifacts")

        # Verify Kilo state
        self.assertTrue((self.test_dir / ".kilo").exists())
        print("✓ .kilo/ exists")

        # NOW SIMULATE SECOND INIT WITH CLAUDE
        print("\n=== SIMULATING SECOND INIT: Switch to Claude ===")

        # Step 1: User selects "Claude" in init
        selected_tool = "Claude"  # What the UI returns
        print(f"User selected: '{selected_tool}'")

        # Step 2: Normalize tool name (init does this)
        normalized_tool = normalize_tool_name(selected_tool)
        print(f"Normalized tool: '{normalized_tool}'")

        # Step 3: Detect current tool
        manager = ArtifactManager(self.test_dir)
        current_tool = manager.current_tool
        print(f"Current tool detected: '{current_tool}'")

        # Step 4: Check if switching
        print(f"Comparing: current_tool='{current_tool}' vs selected_tool='{selected_tool}'")
        if selected_tool and current_tool and current_tool != selected_tool:
            print("→ Different tools, removing old artifacts...")

            # This is what init does - but it should compare canonical names!
            # The bug might be in the comparison itself
            removal_actions = manager.remove_artifacts_created_by(current_tool)
            print(f"Removed: {removal_actions}")

            self.assertFalse((self.test_dir / ".kilo").exists(), ".kilo/ should be removed")
        else:
            print("→ Same tool or tool already removed")

        # Step 5: Build with selected tool (init does this)
        print(f"\nBuilding with {normalized_tool}...")
        builder = get_prompt_builder(normalized_tool)
        print(f"Builder tool_name: {builder.tool_name}")

        actions = builder.build(self.test_dir, config, dry_run=False)
        print(f"Built {len(actions)} artifacts")

        # Final verification
        print("\n=== FINAL STATE ===")
        kilo_exists = (self.test_dir / ".kilo").exists()
        claude_exists = (self.test_dir / ".claude").exists()

        print(f".kilo/ exists: {kilo_exists}")
        print(f".claude/ exists: {claude_exists}")

        # The critical assertions
        self.assertFalse(kilo_exists, "BUG: .kilo/ should NOT exist after switching to Claude")
        self.assertTrue(claude_exists, ".claude/ MUST exist for Claude tool")


if __name__ == "__main__":
    unittest.main()
