"""Inline provenance headers, and the inverse property they depend on (PRO-112).

AC 1 is the load-bearing one. If `strip(render(body, meta)) != body` for any
input, the digest recorded inside a file stops matching the digest computed from
it — and every verification of that file fails for a reason nobody can see by
reading it.
"""

import itertools

import pytest

from prompticorn.provenance import MARKER, OutputFormat, ProvenanceHeader, ProvenanceRecord

RECORD = ProvenanceRecord(unit="agent/code", layer="builtin", version="0.5.0", digest="a" * 64)

# Body shapes chosen for the ways a naive strip breaks: empty input, missing and
# doubled trailing newlines, leading blank lines, content that merely *looks*
# like a comment, and content that starts with a header of our own.
_BODIES = [
    "",
    "\n",
    "\n\n",
    "x",
    "x\n",
    "x\n\n",
    "line one\nline two\n",
    "line one\nline two",
    "\nleading blank\n",
    "# a yaml comment\n",
    "<!-- someone else's comment -->\nbody\n",
    "---\nfrontmatter: true\n---\nbody\n",
    # Frontmatter shapes the offset calculation has to survive: empty, nothing
    # after it, never closed, only an opener, and delimiters that are content
    # rather than frontmatter because they do not start the document.
    "---\n---\nbody\n",
    "---\nname: x\n---\n",
    "---\nname: x\n---",
    "---\nnever: closed\nbody\n",
    "---\n",
    "prose\n---\nnot frontmatter\n---\n",
    '{\n  "a": 1\n}\n',
    "  indented\n",
    "trailing spaces   \n",
    f"# {MARKER} not really ours but shaped like it\nbody\n",
]


@pytest.mark.parametrize(
    ("output_format", "body"), list(itertools.product(list(OutputFormat), _BODIES))
)
def test_strip_is_exactly_inverse_to_render(output_format: OutputFormat, body: str) -> None:
    """AC 1: the property, across all four formats and every awkward body."""
    rendered = ProvenanceHeader.render(body, RECORD, output_format)

    assert ProvenanceHeader.strip(rendered, output_format) == body


def test_the_inverse_holds_for_json_bodies_shaped_like_a_header() -> None:
    """Why `strip` takes the format at all.

    `render` is the identity for JSON, so `strip` must be too. Without that the
    property would hold only for inputs we assumed — not by construction.
    """
    body = f"# {MARKER} unit=x layer=y version=z digest=w\n{{}}\n"

    assert ProvenanceHeader.strip(body, OutputFormat.JSON) == body
    assert ProvenanceHeader.strip(body, OutputFormat.MARKDOWN) != body


@pytest.mark.parametrize("body", _BODIES)
def test_stripping_untouched_text_changes_nothing(body: str) -> None:
    """Safe to apply to anything — a file that never had a header is unharmed."""
    if ProvenanceHeader.has_header(body):
        pytest.skip("body deliberately begins with a header")
    assert ProvenanceHeader.strip(body) == body


def test_stripping_is_idempotent() -> None:
    once = ProvenanceHeader.strip(ProvenanceHeader.render("body\n", RECORD, OutputFormat.MARKDOWN))

    assert ProvenanceHeader.strip(once) == once


# ── AC 2: JSON carries no inline header ────────────────────────────────────────


@pytest.mark.parametrize("body", ['{"a": 1}', "{}", '{"nested": {"b": 2}}\n'])
def test_json_is_returned_untouched(body: str) -> None:
    """A comment would be a syntax error; a `_prompticorn` key would pollute a
    schema the consuming tool validates."""
    assert ProvenanceHeader.render(body, RECORD, OutputFormat.JSON) == body


def test_json_does_not_support_an_inline_header() -> None:
    assert not OutputFormat.JSON.supports_inline_header
    assert all(f.supports_inline_header for f in OutputFormat if f is not OutputFormat.JSON)


# ── AC 3: the header names all four fields ────────────────────────────────────


@pytest.mark.parametrize(
    "output_format", [OutputFormat.MARKDOWN, OutputFormat.YAML, OutputFormat.TOML]
)
def test_the_header_names_unit_layer_version_and_digest(output_format: OutputFormat) -> None:
    header = ProvenanceHeader.render("body\n", RECORD, output_format).splitlines()[0]

    assert "unit=agent/code" in header
    assert "layer=builtin" in header
    assert "version=0.5.0" in header
    assert f"digest={'a' * 64}" in header


def test_markdown_uses_an_html_comment() -> None:
    header = ProvenanceHeader.render("b\n", RECORD, OutputFormat.MARKDOWN).splitlines()[0]

    assert header.startswith("<!--")
    assert header.endswith("-->")


@pytest.mark.parametrize("output_format", [OutputFormat.YAML, OutputFormat.TOML])
def test_line_comment_formats_use_a_hash(output_format: OutputFormat) -> None:
    header = ProvenanceHeader.render("b\n", RECORD, output_format).splitlines()[0]

    assert header.startswith("# ")
    assert not header.endswith("-->")


def test_the_header_occupies_exactly_one_line() -> None:
    rendered = ProvenanceHeader.render("a\nb\n", RECORD, OutputFormat.MARKDOWN)

    assert len(rendered.splitlines()) == 3


def test_field_order_is_fixed() -> None:
    """Reordering would rewrite every generated file in the repository."""
    header = ProvenanceHeader.render("b\n", RECORD, OutputFormat.MARKDOWN)

    positions = [header.index(f"{key}=") for key in ("unit", "layer", "version", "digest")]
    assert positions == sorted(positions)


# ── where the header goes ─────────────────────────────────────────────────────


def test_the_header_goes_below_frontmatter() -> None:
    """The Agent Skills format requires frontmatter at the very start of a
    SKILL.md, so a comment above it does not annotate the file — it invalidates
    it for the tool that reads it."""
    body = "---\nname: code-review-practices\n---\n\n# Body\n"

    rendered = ProvenanceHeader.render(body, RECORD, OutputFormat.MARKDOWN)

    assert rendered.startswith("---\nname: code-review-practices\n---\n")
    assert rendered.splitlines()[3].startswith("<!--")


def test_frontmatter_still_parses_as_frontmatter_afterwards() -> None:
    body = "---\nname: x\ndescription: y\n---\n\n# Body\n"

    rendered = ProvenanceHeader.render(body, RECORD, OutputFormat.MARKDOWN)

    _, _, after_open = rendered.partition("---\n")
    frontmatter, delimiter, _ = after_open.partition("\n---\n")
    assert delimiter
    assert MARKER not in frontmatter


def test_the_header_goes_first_when_there_is_no_frontmatter() -> None:
    rendered = ProvenanceHeader.render("# Body\n", RECORD, OutputFormat.MARKDOWN)

    assert rendered.startswith("<!--")


def test_an_unclosed_opener_is_not_frontmatter() -> None:
    """Three dashes with no closing delimiter is content, so the header belongs
    above it — and, either way, strip has to undo exactly what render did."""
    body = "---\nnever: closed\n"

    rendered = ProvenanceHeader.render(body, RECORD, OutputFormat.MARKDOWN)

    assert rendered.startswith("<!--")
    assert ProvenanceHeader.strip(rendered, OutputFormat.MARKDOWN) == body


def test_a_header_below_frontmatter_is_read_back() -> None:
    body = "---\nname: x\n---\nbody\n"

    rendered = ProvenanceHeader.render(body, RECORD, OutputFormat.MARKDOWN)

    assert ProvenanceHeader.has_header(rendered)
    assert ProvenanceHeader.parse(rendered) == RECORD


def test_frontmatter_alone_is_not_mistaken_for_a_header() -> None:
    assert not ProvenanceHeader.has_header("---\nname: x\n---\nbody\n")


def test_the_digest_is_unchanged_by_where_the_header_sits() -> None:
    """The digest covers the body with the header stripped, so moving the
    insertion point below frontmatter must not move the digest."""
    body = "---\nname: x\n---\nbody\n"

    rendered = ProvenanceHeader.render(body, RECORD, OutputFormat.MARKDOWN)

    assert ProvenanceHeader.body_digest(rendered, OutputFormat.MARKDOWN) == (
        ProvenanceHeader.body_digest(body, OutputFormat.MARKDOWN)
    )


# ── reading it back ───────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "output_format", [OutputFormat.MARKDOWN, OutputFormat.YAML, OutputFormat.TOML]
)
def test_a_rendered_header_parses_back_to_the_record(output_format: OutputFormat) -> None:
    """Lets a verifier check a file against its own claim, without the sidecar —
    useful precisely when the two disagree."""
    rendered = ProvenanceHeader.render("body\n", RECORD, output_format)

    assert ProvenanceHeader.parse(rendered) == RECORD


def test_parsing_text_without_a_header_yields_none() -> None:
    assert ProvenanceHeader.parse("just a body\n") is None


def test_parsing_an_incomplete_header_yields_none() -> None:
    """A truncated header is not a record, and must not be half-believed."""
    assert ProvenanceHeader.parse(f"<!-- {MARKER} unit=agent/code -->\nbody\n") is None


def test_has_header_detects_only_our_own() -> None:
    assert ProvenanceHeader.has_header(
        ProvenanceHeader.render("b\n", RECORD, OutputFormat.MARKDOWN)
    )
    assert not ProvenanceHeader.has_header("<!-- someone else -->\nb\n")
    assert not ProvenanceHeader.has_header("# a comment\n")


# ── the self-reference rule ───────────────────────────────────────────────────


def test_writing_the_digest_into_the_header_does_not_change_the_digest() -> None:
    """The problem this whole module is shaped around.

    Naively: digest the file, write it into a header, prepend — and the file has
    changed, so the digest no longer describes it. Digesting the *stripped* body
    is what closes the loop.
    """
    body = "generated body\n"
    digest = ProvenanceHeader.body_digest(body)

    headed = ProvenanceHeader.render(
        body, ProvenanceRecord("agent/code", "builtin", "0.5.0", digest), OutputFormat.MARKDOWN
    )

    assert ProvenanceHeader.body_digest(headed) == digest


def test_the_digest_survives_a_rebuild() -> None:
    """Re-rendering over an already-headed file must not move the digest."""
    body = "generated body\n"
    digest = ProvenanceHeader.body_digest(body)
    once = ProvenanceHeader.render(
        body, ProvenanceRecord("agent/code", "builtin", "0.5.0", digest), OutputFormat.MARKDOWN
    )

    twice = ProvenanceHeader.render(
        ProvenanceHeader.strip(once),
        ProvenanceRecord("agent/code", "builtin", "0.5.0", ProvenanceHeader.body_digest(once)),
        OutputFormat.MARKDOWN,
    )

    assert twice == once


def test_the_digest_agrees_with_the_shared_canonical_digest() -> None:
    """One definition of canonical in the codebase, not two that can drift."""
    from prompticorn.content import digest_text

    assert ProvenanceHeader.body_digest("body\n") == digest_text("body\n")


def test_line_ending_style_does_not_change_the_digest() -> None:
    """Inherited from the canonicalisation PRO-104 established."""
    assert ProvenanceHeader.body_digest("a\r\nb\r\n") == ProvenanceHeader.body_digest("a\nb\n")


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("CLAUDE.md", OutputFormat.MARKDOWN),
        (".cursor/rules/x.mdc", OutputFormat.MARKDOWN),
        (".aider.conf.yml", OutputFormat.YAML),
        ("config.yaml", OutputFormat.YAML),
        ("pyproject.toml", OutputFormat.TOML),
        (".amazonq/cli-agents/a.json", OutputFormat.JSON),
        ("NOEXTENSION", OutputFormat.MARKDOWN),
    ],
)
def test_format_is_classified_by_extension(path: str, expected: OutputFormat) -> None:
    assert OutputFormat.of(path) is expected


def test_an_unknown_extension_never_guesses_json() -> None:
    """Guessing JSON would *omit* the header rather than add a harmless one."""
    assert OutputFormat.of("mystery.xyz") is not OutputFormat.JSON
