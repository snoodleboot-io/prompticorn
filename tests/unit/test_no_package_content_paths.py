"""Content is resolved, never read from the package directory (PRO-166).

PRO-106 was titled "retire the `Path(__file__).parent` sites" and was marked done
with eleven of them still in the tree. Two of those eleven — `WorkflowLoader` and
`ClaudeBuilder._load_subagent_content` — were the whole of PRO-165's first
blocker: once PRO-117 added a layer stack, a module reading
`Path(__file__).parent.parent / "workflows"` silently ignored every override,
while the lock resolved the same unit through the stack and recorded a different
answer for it.

"Done" is not a property a ticket can assert about a codebase. This test is,
which is why it is the deliverable that keeps PRO-106 honest.

**The rule.** No module under ``prompticorn/`` may derive a path from
``__file__`` unless it is on the allowlist below, and every entry on that
allowlist carries the reason reading from the package is correct there. The list
is short on purpose: adding to it is a decision somebody has to write down, and a
reviewer gets to see that sentence in the diff.

Two things this deliberately does not catch, stated so nobody assumes otherwise:

* ``bedrock_builder.py`` emits an ``invoke_example.py`` whose own
  ``pathlib.Path(__file__).parent`` locates the manifest beside it **on the
  user's machine**. That is correct by construction and invisible here, because
  the code lives inside a string literal and never reaches this module's AST.
  ``tests/unit/test_explicit_encoding.py`` scans that same emitted template as
  text for its own rule; this one has no equivalent hazard to scan for.
* A module on the allowlist for one reason could later grow a second
  ``__file__`` site for a bad one. Line-level granularity would be brittle
  enough to be deleted, so the reason strings are the control, and
  ``test_every_allowlisted_module_still_uses_the_path`` at least ensures a
  module cannot stay on the list after its reason has gone.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

_PACKAGE = Path(__file__).parent.parent.parent / "prompticorn"

# Module path relative to ``prompticorn/`` -> why reading from the package is
# right there. Everything absent from this mapping must resolve through
# ``prompticorn.content.content_resolver``.
_ALLOWED: dict[str, str] = {
    "content/builtin_content_source.py": (
        "It IS the bundled layer. Something has to know where the package's own "
        "content tree is, and this is the single place that does — resolved from "
        "the module's location rather than the working directory, which is wrong "
        "whenever the process runs from outside the repository."
    ),
    "cli.py": (
        "`validate` checks the on-disk STRUCTURE of the bundled agents tree, "
        "which is a filesystem question the resolver deliberately abstracts "
        "away. Every content read in the CLI goes through the resolver."
    ),
    "registry.py": (
        "prompticorn/prompts holds the Jinja macro library and the legacy flat "
        "prompt files: template machinery with no UnitKind, so a layer has "
        "nowhere to put an override and nothing to address it by."
    ),
    "builders/claude_builder.py": (
        "The builder's own output templates, which encode the .claude/ file "
        "format. Overriding one would be overriding prompticorn's code through "
        "a data file."
    ),
    "builders/claude_md.py": (
        "The CLAUDE.md output template — this builder's format, not authored content."
    ),
    "builders/config.py": (
        "Kilo's mode schema and language file map, under "
        "prompticorn/builders/kilo/. Builder-local data outside the content "
        "layout, unaddressable as a unit."
    ),
    "builders/convention_generator.py": (
        "A Jinja LOADER ROOT, used only to resolve `{% import 'macros/...' %}`. "
        "The convention sources themselves come from `read_core_convention`; "
        "Jinja needs a directory, and the macro library is not a unit."
    ),
    "ir/loaders/core_files_loader.py": (
        "The same Jinja macro root as convention_generator, deliberately "
        "identical: two roots would let one import resolve differently in two "
        "places. Its content comes from the resolver it is constructed with."
    ),
    "ir/loaders/agent_skill_mapping_loader.py": (
        "The explicit-path constructor's default. The build reads this mapping "
        "through `from_resolver`, which layers; the path form exists for a "
        "caller that wants one named file and gets exactly that."
    ),
    "ir/loaders/language_skill_mapping_loader.py": (
        "The explicit-path constructor's default, as for the agent-skill mapping above."
    ),
    "questions/language.py": (
        "question_pipelines.yaml names Python question CLASSES that must exist "
        "in this package. An override could only name classes that do not, so "
        "it is interview implementation rather than overridable content."
    ),
}


def _module_paths() -> list[Path]:
    return sorted(_PACKAGE.rglob("*.py"))


def _relative(path: Path) -> str:
    return path.relative_to(_PACKAGE).as_posix()


def _uses_dunder_file(path: Path) -> bool:
    """Whether this module's own code reads ``__file__``.

    Parsed rather than grepped: a docstring or comment that mentions `__file__`
    — including the ones this change added to explain the conversions — is prose,
    not a filesystem read, and a text scan would count it.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return any(isinstance(node, ast.Name) and node.id == "__file__" for node in ast.walk(tree))


@pytest.mark.unit
class TestNoUnallowlistedPackagePaths:
    def test_no_module_resolves_content_from_the_package_directory(self) -> None:
        offenders = sorted(
            _relative(path)
            for path in _module_paths()
            if _uses_dunder_file(path) and _relative(path) not in _ALLOWED
        )
        assert not offenders, (
            "these modules derive a path from __file__ and so read the installed "
            "package instead of the content layer stack, which makes every "
            "project and user override invisible to them: "
            f"{offenders}. Resolve through prompticorn.content.content_resolver, "
            "or add the module to _ALLOWED with the reason reading from the "
            "package is correct."
        )

    def test_every_allowlisted_module_still_uses_the_path(self) -> None:
        """Stale entries are how an allowlist stops describing the code. A module
        that no longer reads ``__file__`` must come off the list, or the next one
        added for a bad reason inherits its plausibility."""
        stale = sorted(
            relative
            for relative in _ALLOWED
            if not (_PACKAGE / relative).is_file() or not _uses_dunder_file(_PACKAGE / relative)
        )
        assert not stale, f"allowlist entries no longer needed: {stale}"

    def test_every_allowlist_entry_gives_a_reason(self) -> None:
        """The reason is the whole control. An entry with a placeholder for one is
        an exemption nobody has justified."""
        unexplained = sorted(key for key, reason in _ALLOWED.items() if len(reason.split()) < 8)
        assert not unexplained, f"allowlist entries without a real reason: {unexplained}"


@pytest.mark.unit
class TestTheDetectorDetects:
    """A guard that cannot see the thing it guards against passes for ever."""

    def test_a_planted_package_path_is_found(self, tmp_path: Path) -> None:
        planted = tmp_path / "offender.py"
        planted.write_text(
            'from pathlib import Path\n\nD = Path(__file__).parent / "agents"\n',
            encoding="utf-8",
        )

        assert _uses_dunder_file(planted)

    def test_os_path_dirname_is_found_too(self, tmp_path: Path) -> None:
        """The obvious way around a scan that only knew `Path(__file__)`."""
        planted = tmp_path / "sneaky.py"
        planted.write_text("import os\n\nD = os.path.dirname(__file__)\n", encoding="utf-8")

        assert _uses_dunder_file(planted)

    def test_prose_mentioning_the_name_is_not_found(self, tmp_path: Path) -> None:
        """The conversions this test guards left comments explaining what they
        replaced. A text scan would report every one of them."""
        planted = tmp_path / "prose.py"
        planted.write_text(
            '"""It used to read Path(__file__).parent, which ignored the stack."""\n'
            "\n"
            "# Not Path(__file__) any more.\n"
            "VALUE = 1\n",
            encoding="utf-8",
        )

        assert not _uses_dunder_file(planted)

    def test_the_converted_modules_are_clean(self) -> None:
        """Named explicitly rather than left to the sweep, so a revert of any one
        of them fails a test that says which. These are the sites PRO-106 claimed
        to have retired and PRO-165/PRO-166 actually did."""
        converted = [
            "builders/workflow_loader.py",
            "builders/template_handlers/primary_agents_handler.py",
            "questions/base/folder_spec.py",
        ]
        offenders = [relative for relative in converted if _uses_dunder_file(_PACKAGE / relative)]
        assert not offenders, f"converted back to a package path: {offenders}"
