"""The {{PRIMARY_AGENTS_LIST}} pass must touch only emitted files (PRO-137).

`prompticorn switch` builds with ``output = Path(".")``. The substitution used to
``rglob`` that root, so it walked the user's entire repository and rewrote every
file containing the literal token — source modules and agent templates included.
Destroying the placeholder in a source template is the silent failure: builds keep
succeeding while emitting a frozen agent list.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from prompticorn.prompt_builder import get_prompt_builder

_TOKEN = "{{PRIMARY_AGENTS_LIST}}"
_CONFIG = {
    "spec": {"language": "python"},
    "active_personas": ["software_engineer"],
    "variant": "minimal",
}

# One builder per emission strategy: claude substitutes during the agent write,
# the IR-based ones rely entirely on the post-write pass (PRO-72).
_IR_BUILDERS = ["gemini", "roo", "zed", "junie", "codex", "windsurf", "continue", "copilot-chat"]


@pytest.mark.unit
class TestPrimaryAgentsTokenScope:
    def test_build_in_place_leaves_unrelated_files_untouched(self):
        """A build rooted at a repo must not rewrite files it did not emit."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Stand in for the repo files the old rglob corrupted: source modules
            # and docs that merely *mention* the token.
            bystanders = {
                root / "prompt_builder.py": f'"""Handles {_TOKEN} substitution."""\n',
                root / "CHANGELOG.md": f"- Fixed {_TOKEN} resolution\n",
                root / "src" / "nested" / "notes.md": f"see {_TOKEN} for details\n",
            }
            for path, text in bystanders.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")

            get_prompt_builder("claude").build(root, _CONFIG, dry_run=False)

            for path, original in bystanders.items():
                assert path.read_text(encoding="utf-8") == original, (
                    f"build rewrote a file it did not emit: {path.relative_to(root)}"
                )

    def test_source_agent_template_keeps_its_placeholder(self):
        """The worst case: an in-place build destroyed the placeholder in the
        *source* `prompticorn/agents/orchestrator/prompt.md`, so every later build
        emitted a frozen agent list while still reporting success.

        Models it by placing the real template inside the build root at its own
        source path — which the build never emits — and asserting it survives.
        """
        real_source = (
            Path(__file__).parent.parent.parent
            / "prompticorn"
            / "agents"
            / "orchestrator"
            / "prompt.md"
        )
        original = real_source.read_text(encoding="utf-8")
        assert _TOKEN in original, "fixture invalid: source template has no placeholder"

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            checkout = root / "prompticorn" / "agents" / "orchestrator" / "prompt.md"
            checkout.parent.mkdir(parents=True, exist_ok=True)
            checkout.write_text(original, encoding="utf-8")

            get_prompt_builder("claude").build(root, _CONFIG, dry_run=False)

            assert checkout.read_text(encoding="utf-8") == original
            assert _TOKEN in checkout.read_text(encoding="utf-8")

        # And the real one on disk is untouched by any build.
        assert real_source.read_text(encoding="utf-8") == original

    @pytest.mark.parametrize("tool", ["claude", *_IR_BUILDERS])
    def test_emitted_output_still_has_no_unresolved_token(self, tool):
        """Scoping the pass must not regress PRO-72 — every builder still resolves
        the token in what it emits."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            get_prompt_builder(tool).build(root, _CONFIG, dry_run=False)
            unresolved = [
                path.relative_to(root).as_posix()
                for path in root.rglob("*")
                if path.is_file() and _TOKEN in path.read_text(encoding="utf-8", errors="ignore")
            ]
            assert not unresolved, f"{tool}: unresolved token in {unresolved}"

    def test_emitted_file_containing_the_token_is_still_resolved(self):
        """A pre-existing file at an emitted path is rewritten (it gets
        overwritten by the build anyway) — the scoping is by path, not by
        whether the build created the file fresh."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            claude_md = root / "CLAUDE.md"
            claude_md.write_text(f"stale {_TOKEN}\n", encoding="utf-8")

            get_prompt_builder("claude").build(root, _CONFIG, dry_run=False)

            assert _TOKEN not in claude_md.read_text(encoding="utf-8")
