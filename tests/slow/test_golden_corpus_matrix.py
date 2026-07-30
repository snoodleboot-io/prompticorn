"""Full golden matrix: tool x variant x repository-type x language (PRO-102).

The pre-refactor baseline for the content-resolution seam. Every later task in
that milestone moves code which produces these files, so without a snapshot taken
*before* the move, "did anything change?" is unanswerable.

136 cells (17 tools x 2 variants x 4 configs), ~2.5 minutes — hence ``tests/slow``,
which CI runs on every PR and on main. The fast single-config slice lives in
``tests/unit/test_tool_output_golden.py`` so common-path regressions still fail
early; both read the same corpus.

Regenerate (only when output changes intentionally)::

    uv run python -m tests.golden_corpus
"""

import pytest

from tests.golden_corpus import (
    CONFIGS,
    build_manifest,
    corpus_keys,
    describe_difference,
    load,
    split_key,
)


@pytest.fixture(scope="module")
def corpus():
    return load()


@pytest.mark.slow
class TestGoldenCorpusMatrix:
    def test_corpus_is_complete(self, corpus):
        """Every matrix cell is recorded, and nothing stale lingers.

        A cell silently missing from the fixture is a hole in the safety net that
        no per-cell assertion would ever report.
        """
        expected = set(corpus_keys())
        actual = set(corpus)
        assert not sorted(expected - actual), f"corpus missing cells: {sorted(expected - actual)}"
        assert not sorted(actual - expected), f"corpus has stale cells: {sorted(actual - expected)}"

    def test_matrix_covers_every_branch(self):
        """The matrix must keep exercising the branches it exists to cover — a
        config quietly dropped would shrink the net without failing anything."""
        assert "monorepo" in CONFIGS, "monorepo branch dropped from the matrix"
        languages = set()
        repo_types = set()
        for config in CONFIGS.values():
            spec = config.get("spec")
            if isinstance(spec, dict):
                languages.add(spec.get("language"))
            elif isinstance(spec, list):
                languages.update(folder.get("language") for folder in spec)
            repo_types.add((config.get("repository") or {}).get("type", ""))
        assert len(languages) >= 3, f"only {len(languages)} languages in the matrix"
        assert "multi-language-monorepo" in repo_types

    @pytest.mark.parametrize("key", corpus_keys())
    def test_cell_matches_golden(self, key, corpus):
        config_id, tool_id, variant = split_key(key)
        assert key in corpus, f"{key} is not recorded in the corpus"
        actual = build_manifest(key)
        expected = corpus[key]
        assert actual == expected, (
            f"output for {key} diverged from the golden corpus:\n"
            + describe_difference(expected, actual)
        )
