"""Rendering and stripping the inline provenance header (PRO-112).

``strip`` must be **exactly** inverse to ``render``. That is not a tidiness
preference — it is what makes the digest computable at all.

The self-reference problem
--------------------------

A file's digest covers its body. Write the digest into a header, prepend it, and
the file's content has changed — so the digest no longer describes the file. The
way out is to define the digest over the body *with the header stripped*, which
only works if stripping recovers the body byte-for-byte:

    render body -> strip-normalise -> digest -> render header with digest ->
    prepend -> write

If ``strip(render(body, meta)) != body`` for any input, the digest recorded in a
file stops matching the digest computed from it, and every verification of that
file fails for a reason nobody can see by reading it.
"""

from __future__ import annotations

import re

from prompticorn.content.digest import canonical_text, digest_text
from prompticorn.provenance.output_format import OutputFormat
from prompticorn.provenance.provenance_record import ProvenanceRecord

MARKER = "prompticorn:"

# One header line, in either comment syntax. Never searched for — only matched at
# the one offset :func:`_header_offset` computes, so a line further down stays
# content rather than something this module is entitled to delete.
_HEADER_RE = re.compile(r"(?:<!--\s*prompticorn:.*?-->|#\s*prompticorn:.*?)(?:\r\n|\r|\n|$)")

# A leading YAML frontmatter block: `---` on its own line, through the next such
# line. Detected without reference to the format because the question is about
# the document's first bytes, not its comment syntax.
# The closing delimiter must end in a line break. Without one the frontmatter is
# the whole document and there is no line boundary below it to insert at — and
# an insertion point that has to invent a newline is one strip cannot undo.
_FRONTMATTER_OPEN_RE = re.compile(r"---[ \t]*(?:\r\n|\r|\n)")
_FRONTMATTER_CLOSE_RE = re.compile(r"^---[ \t]*(?:\r\n|\r|\n)", re.MULTILINE)


def _header_offset(text: str) -> int:
    """Where the header goes: after any leading frontmatter, else byte 0.

    Frontmatter is a contract with the consuming tool, not content — the Agent
    Skills format requires it at the very start of a SKILL.md, so a comment
    prepended above it does not annotate the file, it invalidates it.

    There are exactly two candidate offsets and both are determined by the
    document's structure, which is what keeps :meth:`ProvenanceHeader.strip`
    an exact inverse of :meth:`ProvenanceHeader.render`: the offset computed
    from a headed file is the same one the header was written at, because
    inserting after the frontmatter leaves the frontmatter untouched.
    """
    opening = _FRONTMATTER_OPEN_RE.match(text)
    if opening is None:
        return 0
    closing = next(_FRONTMATTER_CLOSE_RE.finditer(text, opening.end()), None)
    return closing.end() if closing is not None else 0


class ProvenanceHeader:
    """Renders and strips the inline provenance comment."""

    @staticmethod
    def render(body: str, record: ProvenanceRecord, output_format: OutputFormat) -> str:
        """Write a provenance header into ``body``.

        The header goes at the top, unless the document opens with YAML
        frontmatter — see :func:`_header_offset` for why it must go below that
        rather than above it.

        JSON is returned unchanged — it has no comment syntax, and the sidecar
        carries its provenance instead.
        """
        if not output_format.supports_inline_header:
            return body

        prefix = output_format.comment_prefix
        suffix = output_format.comment_suffix
        inner = f"{MARKER} {record.to_header_body()}"
        line = f"{prefix} {inner} {suffix}".rstrip() if suffix else f"{prefix} {inner}"
        offset = _header_offset(body)
        return f"{body[:offset]}{line}\n{body[offset:]}"

    @staticmethod
    def strip(text: str, output_format: OutputFormat | None = None) -> str:
        """Remove the provenance header, if there is one.

        Exactly inverse to :meth:`render`: it looks at the one offset render
        writes to, removes the single line it would have put there — including
        the newline that separated it from the body — and nothing else. Text
        without a header is returned untouched, so the operation is safe to
        apply to anything and is idempotent on already-stripped content.

        ``output_format`` matters for one case. :meth:`render` is the identity
        for JSON, so stripping must be too — otherwise a JSON document whose
        first line happened to look like a header would come back shorter than
        it went in, and the inverse property would hold only for inputs we
        assumed rather than by construction. Omitting the format assumes a
        commentable format, which is every caller that has a header to remove.
        """
        if output_format is not None and not output_format.supports_inline_header:
            return text
        offset = _header_offset(text)
        match = _HEADER_RE.match(text, offset)
        if match is None:
            return text
        return f"{text[:offset]}{text[match.end() :]}"

    @classmethod
    def has_header(cls, text: str) -> bool:
        """Whether ``text`` carries a provenance header where render writes one."""
        return _HEADER_RE.match(text, _header_offset(text)) is not None

    @classmethod
    def parse(cls, text: str) -> ProvenanceRecord | None:
        """Read back the record a header carries, or None if there is none.

        Lets a verifier check a file against its own claim without consulting
        the sidecar — useful precisely when the two disagree.
        """
        match = _HEADER_RE.match(text, _header_offset(text))
        if match is None:
            return None

        line = match.group(0)
        _, _, tail = line.partition(MARKER)
        tail = tail.replace("-->", "").strip()

        pairs: dict[str, str] = {}
        for token in tail.split():
            key, separator, value = token.partition("=")
            if separator:
                pairs[key] = value
        try:
            return ProvenanceRecord.from_mapping(pairs)
        except KeyError:
            return None

    @classmethod
    def body_digest(cls, body: str, output_format: OutputFormat | None = None) -> str:
        """The digest a header should claim for ``body``.

        Strips first, so passing already-headed text yields the same answer as
        passing the bare body — the property that keeps a regenerated file's
        digest stable across rebuilds.
        """
        return digest_text(cls.strip(body, output_format))

    @classmethod
    def normalise(cls, body: str, output_format: OutputFormat | None = None) -> str:
        """The canonical, header-free form the digest is taken over."""
        return canonical_text(cls.strip(body, output_format))
