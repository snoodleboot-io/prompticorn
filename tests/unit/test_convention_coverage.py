"""Convention-coverage invariants (PRO-93).

Language conventions resolve by filename: ``conventions-{language}.md``
(``convention_generator.generate_language_convention``). A supported language
whose convention file is misnamed silently ships with **no** language
conventions — exactly the go/golang mismatch that left every Go project
convention-less, with nothing guarding it (same species as PRO-89's SKILL.md
casing bug). These tests pin both directions so it can't recur.
"""

from pathlib import Path

import pytest

from prompticorn.questions.language import LanguageRegistry

_CORE = Path(__file__).parent.parent.parent / "prompticorn" / "agents" / "core"

# Convention files that match no supported language. This set may only SHRINK:
# wire the language into languages.yaml, or delete the file — never add entries.
# (c/cpp/objc have conventions authored but are not offered by the picker.)
KNOWN_UNSELECTABLE = frozenset({"c", "cpp", "objc"})


def _convention_languages() -> set[str]:
    return {p.stem.replace("conventions-", "") for p in _CORE.glob("conventions-*.md")}


@pytest.mark.unit
class TestConventionCoverage:
    """Every supported language resolves a convention; no silent orphans."""

    def test_every_supported_language_has_a_convention(self):
        """The go/golang guard: each supported language must resolve its file."""
        supported = set(LanguageRegistry.get_supported_languages())
        missing = sorted(
            lang for lang in supported if not (_CORE / f"conventions-{lang}.md").is_file()
        )
        assert not missing, (
            "These supported languages have no conventions-<lang>.md and would ship "
            f"with zero language conventions (the PRO-93 go/golang class): {missing}"
        )

    def test_no_orphan_conventions_outside_the_allowlist(self):
        """Every convention file is selectable, or explicitly allow-listed."""
        supported = set(LanguageRegistry.get_supported_languages())
        orphans = sorted(_convention_languages() - supported - KNOWN_UNSELECTABLE)
        assert not orphans, (
            "These convention files match no supported language and aren't allow-listed. "
            f"Add the language to languages.yaml or delete the file: {orphans}"
        )

    def test_allowlist_entries_are_still_unselectable(self):
        """If an allow-listed language becomes supported, drop it from the set."""
        supported = set(LanguageRegistry.get_supported_languages())
        stale = sorted(KNOWN_UNSELECTABLE & supported)
        assert not stale, (
            f"These are now supported languages — remove from KNOWN_UNSELECTABLE: {stale}"
        )

    def test_allowlist_names_real_files(self):
        """KNOWN_UNSELECTABLE must not accumulate names of deleted conventions."""
        missing = sorted(
            name for name in KNOWN_UNSELECTABLE if not (_CORE / f"conventions-{name}.md").is_file()
        )
        assert not missing, f"KNOWN_UNSELECTABLE names a nonexistent convention: {missing}"


@pytest.mark.unit
class TestLanguageDefaultRuntimes:
    """Guard the runtime pins in language_defaults.yaml (PRO-94)."""

    def _defaults(self):
        import yaml

        path = (
            Path(__file__).parent.parent.parent
            / "prompticorn"
            / "configurations"
            / "language_defaults.yaml"
        )
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return {k: v for k, v in data.items() if isinstance(v, dict) and "runtime" in v}

    def test_every_pinned_language_has_a_nonempty_runtime(self):
        blank = sorted(k for k, v in self._defaults().items() if not str(v["runtime"]).strip())
        assert not blank, f"languages with a blank runtime pin: {blank}"

    def test_js_and_ts_runtimes_name_a_real_runtime(self):
        """JS/TS `runtime` must name an execution runtime, not a bare version.

        Regression guard for PRO-94, where both were pinned to a nonsensical
        `v6.0` (a compiler-ish version in a field the convention renders as
        "Runtime:", whose hint is Node/Deno/Bun).
        """
        recognized = ("node", "deno", "bun")
        offenders = {
            lang: v["runtime"]
            for lang, v in self._defaults().items()
            if lang in ("javascript", "typescript")
            and not any(tok in str(v["runtime"]).lower() for tok in recognized)
        }
        assert not offenders, (
            f"JS/TS runtime pins must name a real runtime (Node/Deno/Bun): {offenders}"
        )
