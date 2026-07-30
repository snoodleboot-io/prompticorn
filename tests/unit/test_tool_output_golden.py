"""Fast golden slice: every tool/variant on the default config (PRO-60 / PRO-102).

Builds every tool id for both variants against the single-language python config
and asserts the generated file tree matches the recorded baseline byte-for-byte
(path + sha256, with ISO dates normalized).

This is the *fast* slice — one config, ~35s — so an output regression fails in the
unit job rather than waiting for the slow job. The full
tool x variant x repository-type x language matrix lives in
``tests/slow/test_golden_corpus_matrix.py``; both read the same corpus.

Regenerate the corpus (only when output changes intentionally)::

    uv run python -m tests.golden_corpus

Do NOT regenerate to make a failing refactor pass — read the diff first.
"""

import unittest

from tests.golden_corpus import (
    build_manifest,
    corpus_keys,
    describe_difference,
    load,
    split_key,
)

_FAST_CONFIG = "python-single"


class TestToolOutputGolden(unittest.TestCase):
    """Every tool/variant build matches the recorded byte-for-byte baseline."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load()

    def test_corpus_covers_the_fast_config(self) -> None:
        """The fixture must actually contain the slice this test asserts on."""
        expected = {k for k in corpus_keys() if k.startswith(f"{_FAST_CONFIG}::")}
        missing = sorted(expected - self.corpus.keys())
        self.assertFalse(missing, f"corpus is missing entries: {missing}")

    def test_all_tools_match_golden_baseline(self) -> None:
        for key in sorted(self.corpus):
            config_id, tool_id, variant = split_key(key)
            if config_id != _FAST_CONFIG:
                continue
            with self.subTest(tool=tool_id, variant=variant):
                actual = build_manifest(key)
                expected = self.corpus[key]
                if actual != expected:
                    self.fail(
                        f"output for {key} diverged from the golden corpus:\n"
                        + describe_difference(expected, actual)
                    )


if __name__ == "__main__":
    unittest.main()
