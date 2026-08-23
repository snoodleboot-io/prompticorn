"""What the golden corpus normalizes away, and why (PRO-112).

The corpus is only a baseline if two clean checkouts agree about it. Anything in
the output that moves without the build having changed has to be normalized out
before hashing, and every one of these has cost a red CI run at some point.

The other direction matters just as much, and PRO-116 moved the line: a mask
that is no longer needed is not free, because it also hides the thing coming
back. Dates were masked while CLAUDE.md stamped one; now that nothing does, they
are hashed, and the corpus fails if a timestamp reappears.
"""

import unittest

from prompticorn.provenance import OutputFormat, ProvenanceHeader, ProvenanceRecord
from tests.golden_corpus import digest, normalize

_SIDECAR = ".prompticorn/provenance.json"

_RECORD = ProvenanceRecord(
    unit="agent/code", layer="builtin", version="0.5.0", digest="a" * 64
)


def _sidecar(digest_value: str, version: str = "0.5.0") -> bytes:
    return (
        b'{\n  "CLAUDE.md": {\n'
        b'    "digest": "' + digest_value.encode() + b'",\n'
        b'    "layer": "builtin",\n'
        b'    "unit": "generated/claude-md",\n'
        b'    "version": "' + version.encode() + b'"\n'
        b"  }\n}\n"
    )


class TestSidecarNormalization(unittest.TestCase):
    def test_a_moved_digest_does_not_move_the_corpus(self) -> None:
        """CLAUDE.md used to stamp datetime.now() into a "Last Updated" line.
        The corpus masked that date at the file level, but the sidecar records a
        digest *of* the dated bytes, so without masking it too the corpus went
        red at every day boundary — it did, in CI, where a single machine could
        not have caught it.

        PRO-116 removed the timestamp, so that reason is gone. The mask stays
        because a sidecar digest only restates content the corpus already hashes
        per file, and this test stays because the mask does."""
        one = normalize(_sidecar("a" * 64), _SIDECAR)
        another = normalize(_sidecar("b" * 64), _SIDECAR)

        self.assertEqual(one, another)

    def test_the_artifact_version_does_not_move_the_corpus(self) -> None:
        """A release build stamps the version into __about__.py; a clean checkout
        has not."""
        released = normalize(_sidecar("a" * 64, version="1.4.7"), _SIDECAR)
        clean = normalize(_sidecar("a" * 64, version="0.0.0-dev.0"), _SIDECAR)

        self.assertEqual(released, clean)

    def test_unit_attribution_is_still_pinned(self) -> None:
        """The masking must not go so far that the corpus stops noticing a file
        being credited to the wrong source unit — that is the one thing the
        sidecar adds to the corpus."""
        original = normalize(_sidecar("a" * 64), _SIDECAR)
        remapped = normalize(
            _sidecar("a" * 64).replace(b"generated/claude-md", b"agent/wrong"), _SIDECAR
        )

        self.assertNotEqual(original, remapped)

    def test_the_layer_is_still_pinned(self) -> None:
        original = normalize(_sidecar("a" * 64), _SIDECAR)
        relayered = normalize(_sidecar("a" * 64).replace(b"builtin", b"local"), _SIDECAR)

        self.assertNotEqual(original, relayered)


class TestHeaderNormalization(unittest.TestCase):
    def test_adding_a_header_does_not_move_a_files_hash(self) -> None:
        """Why the corpus did not need re-baselining when provenance landed."""
        body = "# Body\n"
        headed = ProvenanceHeader.render(body, _RECORD, OutputFormat.MARKDOWN)

        self.assertEqual(
            normalize(headed.encode(), "a.md"), normalize(body.encode(), "a.md")
        )

    def test_a_header_below_frontmatter_is_normalized_out_too(self) -> None:
        body = "---\nname: x\n---\n\n# Body\n"
        headed = ProvenanceHeader.render(body, _RECORD, OutputFormat.MARKDOWN)

        self.assertEqual(
            normalize(headed.encode(), "a.md"), normalize(body.encode(), "a.md")
        )

    def test_content_is_still_pinned(self) -> None:
        """The header masking must not swallow the body it sits on."""
        one = ProvenanceHeader.render("# One\n", _RECORD, OutputFormat.MARKDOWN)
        two = ProvenanceHeader.render("# Two\n", _RECORD, OutputFormat.MARKDOWN)

        self.assertNotEqual(normalize(one.encode(), "a.md"), normalize(two.encode(), "a.md"))

    def test_a_comment_that_is_not_ours_is_left_alone(self) -> None:
        body = "<!-- someone else's comment -->\n# Body\n"

        self.assertEqual(normalize(body.encode(), "a.md"), body.encode())


class TestDigestEntryPoint(unittest.TestCase):
    def test_a_changed_date_now_moves_the_corpus(self) -> None:
        """Dates were masked before hashing while CLAUDE.md stamped one. PRO-116
        removed the last build-time timestamp and the mask went with it, which is
        what lets the corpus *notice* one being reintroduced — a mask would hide
        that by construction, and hiding it is how the instability survived two
        releases.

        `tests/unit/test_output_determinism.py` is the guard that makes dropping
        the mask safe: it asserts nothing in the emit path reads the clock."""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "first.md"
            second = root / "second.md"
            first.write_text("Released: 2026-08-21\n", encoding="utf-8")
            second.write_text("Released: 2026-08-22\n", encoding="utf-8")

            self.assertNotEqual(digest(first, "first.md"), digest(second, "second.md"))


if __name__ == "__main__":
    unittest.main()
