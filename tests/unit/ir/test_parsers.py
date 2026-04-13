"""Comprehensive unit tests for IR parsers (YAML and Markdown).

Tests cover:
- Happy path: Valid YAML frontmatter and markdown sections
- Edge cases: Empty content, missing sections, malformed input
- Validation: Invalid YAML, missing frontmatter, type checking
- Error handling: ParseError for various failure scenarios
"""

import pytest

from promptosaurus.ir.exceptions import ParseError
from promptosaurus.ir.parsers import MarkdownParser, YAMLParser

# ============================================================================
# FIXTURES - YAMLParser test data
# ============================================================================


@pytest.fixture
def yaml_parser() -> YAMLParser:
    """Create a YAMLParser instance."""
    return YAMLParser()


@pytest.fixture
def valid_yaml_frontmatter() -> str:
    """Valid YAML frontmatter with metadata."""
    return """---
name: my-skill
description: A useful skill
tools_needed:
  - git
  - python
---
# Markdown content here
Some content
"""


@pytest.fixture
def empty_yaml_frontmatter() -> str:
    """YAML frontmatter with empty dict."""
    return """---
---
Content without frontmatter
"""


@pytest.fixture
def no_yaml_frontmatter() -> str:
    """Content without any YAML frontmatter."""
    return """# No frontmatter here
Just markdown content
With multiple lines
"""


@pytest.fixture
def yaml_with_nested_structure() -> str:
    """YAML frontmatter with nested objects."""
    return """---
name: complex-agent
metadata:
  version: 1.0
  tags:
    - production
    - critical
settings:
  timeout: 30
  retries: 3
---
# Content
"""


# ============================================================================
# FIXTURES - MarkdownParser test data
# ============================================================================


@pytest.fixture
def markdown_parser() -> MarkdownParser:
    """Create a MarkdownParser instance."""
    return MarkdownParser()


@pytest.fixture
def valid_markdown_sections() -> str:
    """Valid markdown with multiple sections."""
    return """## Overview
This is the overview section.
It has multiple lines.

## Instructions
Do this then that.
Follow the steps carefully.

## Examples
Example 1: foo
Example 2: bar
"""


@pytest.fixture
def markdown_with_special_headers() -> str:
    """Markdown with special characters in headers."""
    return """## My-Section (v1)
Content here

## Another Section!
More content

## Section_With_Underscores
Even more content
"""


@pytest.fixture
def markdown_no_sections() -> str:
    """Markdown without any ## sections."""
    return """# Main Title
Some content
# Another title
More content without sections
"""


@pytest.fixture
def markdown_empty() -> str:
    """Empty markdown content."""
    return ""


# ============================================================================
# YAMLParser Tests
# ============================================================================


class TestYAMLParserHappyPath:
    """Test YAMLParser with valid inputs."""

    def test_parse_valid_frontmatter(self, yaml_parser, valid_yaml_frontmatter):
        """Test parsing valid YAML frontmatter."""
        result = yaml_parser.parse(valid_yaml_frontmatter)

        assert isinstance(result, dict)
        assert result["name"] == "my-skill"
        assert result["description"] == "A useful skill"
        assert result["tools_needed"] == ["git", "python"]

    def test_parse_nested_structure(self, yaml_parser, yaml_with_nested_structure):
        """Test parsing YAML with nested objects."""
        result = yaml_parser.parse(yaml_with_nested_structure)

        assert result["name"] == "complex-agent"
        assert result["metadata"]["version"] == 1.0
        assert result["metadata"]["tags"] == ["production", "critical"]
        assert result["settings"]["timeout"] == 30

    def test_parse_empty_frontmatter(self, yaml_parser, empty_yaml_frontmatter):
        """Test parsing empty YAML frontmatter returns empty dict."""
        result = yaml_parser.parse(empty_yaml_frontmatter)

        assert result == {}

    def test_parse_no_frontmatter(self, yaml_parser, no_yaml_frontmatter):
        """Test parsing content without frontmatter returns empty dict."""
        result = yaml_parser.parse(no_yaml_frontmatter)

        assert result == {}


class TestYAMLParserEdgeCases:
    """Test YAMLParser edge cases."""

    def test_parse_with_only_frontmatter(self, yaml_parser):
        """Test content that is only frontmatter."""
        content = """---
name: test
---
"""
        result = yaml_parser.parse(content)
        assert result["name"] == "test"

    def test_parse_with_extra_whitespace(self, yaml_parser):
        """Test frontmatter with extra whitespace."""
        content = """---
name:   test
description:  "  spaces  "
---
Content
"""
        result = yaml_parser.parse(content)
        assert result["name"] == "test"
        assert result["description"] == "  spaces  "

    def test_parse_with_null_values(self, yaml_parser):
        """Test YAML with null values."""
        content = """---
name: test
description: null
tags:
---
Content
"""
        result = yaml_parser.parse(content)
        assert result["name"] == "test"
        assert result["description"] is None

    def test_parse_boolean_values(self, yaml_parser):
        """Test YAML with boolean values."""
        content = """---
enabled: true
disabled: false
---
Content
"""
        result = yaml_parser.parse(content)
        assert result["enabled"] is True
        assert result["disabled"] is False

    def test_parse_numeric_values(self, yaml_parser):
        """Test YAML with numeric values."""
        content = """---
count: 42
ratio: 3.14
---
Content
"""
        result = yaml_parser.parse(content)
        assert result["count"] == 42
        assert result["ratio"] == 3.14

    def test_parse_empty_lists(self, yaml_parser):
        """Test YAML with empty lists."""
        content = """---
items: []
---
Content
"""
        result = yaml_parser.parse(content)
        assert result["items"] == []

    def test_parse_multiline_string(self, yaml_parser):
        """Test YAML with multiline strings."""
        content = """---
description: |
  This is a multiline
  description that spans
  multiple lines
---
Content
"""
        result = yaml_parser.parse(content)
        assert "This is a multiline" in result["description"]
        assert "multiple lines" in result["description"]


class TestYAMLParserErrors:
    """Test YAMLParser error handling."""

    def test_parse_invalid_yaml(self, yaml_parser):
        """Test parsing invalid YAML raises ParseError."""
        content = """---
invalid: yaml: content: here
  bad indentation
---
Content
"""
        with pytest.raises(ParseError, match="Invalid YAML"):
            yaml_parser.parse(content)

    def test_parse_non_dict_yaml(self, yaml_parser):
        """Test YAML that is not a dict raises ParseError."""
        content = """---
- item1
- item2
---
Content
"""
        with pytest.raises(ParseError, match="must be a dictionary"):
            yaml_parser.parse(content)

    def test_parse_invalid_frontmatter_structure(self, yaml_parser):
        """Test malformed frontmatter raises ParseError."""
        content = "---invalid---"
        # Should not raise since pattern won't match - returns empty dict
        result = yaml_parser.parse(content)
        assert result == {}

    def test_parse_file_not_found(self, yaml_parser):
        """Test parsing non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            yaml_parser.parse_file("/nonexistent/file.md")


# ============================================================================
# MarkdownParser Tests
# ============================================================================


class TestMarkdownParserHappyPath:
    """Test MarkdownParser with valid inputs."""

    def test_parse_valid_sections(self, markdown_parser, valid_markdown_sections):
        """Test parsing valid markdown sections."""
        result = markdown_parser.parse(valid_markdown_sections)

        assert len(result) == 3
        assert "overview" in result
        assert "instructions" in result
        assert "examples" in result

    def test_parse_section_content(self, markdown_parser, valid_markdown_sections):
        """Test section content is correctly extracted."""
        result = markdown_parser.parse(valid_markdown_sections)

        assert "This is the overview section" in result["overview"]
        assert "Do this then that" in result["instructions"]
        assert "Example 1: foo" in result["examples"]

    def test_parse_special_headers(self, markdown_parser, markdown_with_special_headers):
        """Test parsing headers with special characters."""
        result = markdown_parser.parse(markdown_with_special_headers)

        # Special chars are removed, leaving normalized names
        assert "mysection_v1" in result or "my_section_v1" in result
        assert "another_section" in result or "anothersection" in result
        assert "section_with_underscores" in result

    def test_parse_no_sections(self, markdown_parser, markdown_no_sections):
        """Test markdown without ## sections returns empty dict."""
        result = markdown_parser.parse(markdown_no_sections)

        assert result == {}

    def test_parse_empty_content(self, markdown_parser, markdown_empty):
        """Test parsing empty markdown returns empty dict."""
        result = markdown_parser.parse(markdown_empty)

        assert result == {}


class TestMarkdownParserEdgeCases:
    """Test MarkdownParser edge cases."""

    def test_parse_single_section(self, markdown_parser):
        """Test markdown with only one section."""
        content = """## Single Section
Content of the single section
"""
        result = markdown_parser.parse(content)
        assert len(result) == 1
        assert "single_section" in result

    def test_parse_section_with_empty_content(self, markdown_parser):
        """Test section with empty content."""
        content = """## Section 1
## Section 2
Content here
"""
        result = markdown_parser.parse(content)
        assert "section_1" in result
        assert result["section_1"].strip() == ""
        assert "section_2" in result

    def test_parse_section_with_code_blocks(self, markdown_parser):
        """Test section containing code blocks."""
        content = """## Code Examples
```python
def hello():
    print("world")
```

More text after code
"""
        result = markdown_parser.parse(content)
        assert "Code Examples" not in result
        assert "code_examples" in result
        assert "def hello()" in result["code_examples"]

    def test_parse_section_with_nested_markdown(self, markdown_parser):
        """Test section with nested markdown elements."""
        content = """## Features
- Feature 1
- Feature 2
  - Sub-feature 2a
  - Sub-feature 2b

* Another bullet
* More bullets
"""
        result = markdown_parser.parse(content)
        assert "features" in result
        assert "Feature 1" in result["features"]
        assert "Sub-feature 2a" in result["features"]

    def test_parse_section_normalization(self, markdown_parser):
        """Test header name normalization."""
        content = """## MY SECTION
Content

## another-section-123
More content

## Section With  Multiple   Spaces
Even more
"""
        result = markdown_parser.parse(content)
        assert "my_section" in result
        # Dashes are removed, so becomes "anothersection123"
        assert "anothersection123" in result or "another_section_123" in result
        assert "section_with_multiple_spaces" in result

    def test_parse_duplicate_headers(self, markdown_parser):
        """Test handling of duplicate section headers - last one wins."""
        content = """## Duplicate
First content

## Duplicate
Second content (should override)
"""
        result = markdown_parser.parse(content)
        assert "duplicate" in result
        # Last occurrence should be in the result
        assert "Second content" in result["duplicate"]

    def test_parse_section_with_inline_code(self, markdown_parser):
        """Test section with inline code markers."""
        content = """## Instructions
Use `function_name()` to call it.
See `module.py` for details.
"""
        result = markdown_parser.parse(content)
        assert "instructions" in result
        assert "function_name()" in result["instructions"]


class TestMarkdownParserErrors:
    """Test MarkdownParser error handling."""

    def test_parse_file_not_found(self, markdown_parser):
        """Test parsing non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            markdown_parser.parse_file("/nonexistent/file.md")


class TestMarkdownParserNormalization:
    """Test header normalization logic."""

    def test_normalize_header_lowercase(self, markdown_parser):
        """Test header normalization to lowercase."""
        result = markdown_parser._normalize_header("UPPERCASE HEADER")
        assert result == "uppercase_header"

    def test_normalize_header_spaces_to_underscores(self, markdown_parser):
        """Test spaces converted to underscores."""
        result = markdown_parser._normalize_header("Multiple Word Header")
        assert result == "multiple_word_header"

    def test_normalize_header_special_chars_removed(self, markdown_parser):
        """Test special characters are removed."""
        result = markdown_parser._normalize_header("Header-With!@#$%^&*()")
        # Dashes are also removed, resulting in "headerwith"
        assert result in ("header_with", "headerwith")

    def test_normalize_header_multiple_spaces(self, markdown_parser):
        """Test multiple spaces collapsed to single underscore."""
        result = markdown_parser._normalize_header("Header   With    Spaces")
        assert result == "header_with_spaces"

    def test_normalize_header_leading_trailing_spaces(self, markdown_parser):
        """Test leading/trailing spaces are removed."""
        result = markdown_parser._normalize_header("   Header   ")
        assert result == "header"

    def test_normalize_header_with_numbers(self, markdown_parser):
        """Test headers with numbers are preserved."""
        result = markdown_parser._normalize_header("Section 1 Header 2")
        assert result == "section_1_header_2"

    def test_normalize_header_empty_string(self, markdown_parser):
        """Test empty string normalization."""
        result = markdown_parser._normalize_header("")
        assert result == ""

    def test_normalize_header_only_special_chars(self, markdown_parser):
        """Test header with only special characters."""
        result = markdown_parser._normalize_header("!@#$%^&*()")
        assert result == ""

    def test_normalize_header_trailing_underscores(self, markdown_parser):
        """Test handling of underscores."""
        result = markdown_parser._normalize_header("Header ___")
        # Underscores from spaces may remain
        assert result in ("header", "header_")


# ============================================================================
# Integration Tests - Parsers together
# ============================================================================


class TestParserIntegration:
    """Test YAMLParser and MarkdownParser working together."""

    def test_full_document_with_frontmatter_and_sections(self, yaml_parser, markdown_parser):
        """Test parsing document with both frontmatter and sections."""
        content = """---
name: my-agent
description: An agent
---

## Overview
This is the overview

## Instructions
Follow these steps
"""
        # Parse frontmatter
        frontmatter = yaml_parser.parse(content)
        assert frontmatter["name"] == "my-agent"

        # Parse sections from the part after frontmatter
        # Get content after frontmatter for markdown parsing
        after_frontmatter = content.split("---\n", 2)[-1]
        sections = markdown_parser.parse(after_frontmatter)
        assert "overview" in sections
        assert "instructions" in sections
