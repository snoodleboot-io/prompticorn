"""Configuration YAML as untrusted input (PRO-165).

The failure these exist to prevent is not a crash. A wrong-shaped configuration
loads *successfully* into an empty mapping, and everything downstream then reads
"no personas were defined" as "no filtering was requested" — so `build` writes
every agent and every skill and exits 0. There is no error to notice.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from prompticorn.content.configuration_document import ConfigurationDocument
from prompticorn.content.content_resolver import (
    ContentResolver,
    install_resolver,
    reset_default_resolver,
)
from prompticorn.content.directory_content_source import DirectoryContentSource
from prompticorn.content.errors import MalformedConfigurationError, UnitNotFoundError

LAYER = "project"


@pytest.fixture
def layer(tmp_path: Path):
    """Install a single-source stack over ``tmp_path`` for the length of a test."""
    source = DirectoryContentSource(root=tmp_path, layer=LAYER)
    install_resolver(ContentResolver(sources=(source,)))
    yield tmp_path
    reset_default_resolver()


def write_configuration(root: Path, name: str, text: str) -> Path:
    path = root / "configurations" / f"{name}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.mark.unit
class TestLoading:
    def test_a_well_formed_document_loads(self, layer: Path) -> None:
        write_configuration(layer, "demo", "code:\n  skills: [a]\n")

        document = ConfigurationDocument.load("demo")

        assert document.data == {"code": {"skills": ["a"]}}

    def test_the_layer_that_supplied_it_is_recorded(self, layer: Path) -> None:
        """Which file is wrong is not answerable without it: a stack can have
        four directories holding the same relative path."""
        write_configuration(layer, "demo", "code: {}\n")

        assert ConfigurationDocument.load("demo").layer == LAYER

    def test_an_all_comments_document_is_an_empty_mapping_not_an_error(self, layer: Path) -> None:
        """A legitimate way to say "no entries". Distinct from a document whose
        required section is empty, which the caller rejects."""
        write_configuration(layer, "demo", "# nothing yet\n")

        assert ConfigurationDocument.load("demo").data == {}

    def test_an_absent_configuration_is_still_a_miss(self, layer: Path) -> None:
        """Absent and present-but-wrong are different conditions, and consumers
        treat them differently — several tolerate absence with a default."""
        with pytest.raises(UnitNotFoundError):
            ConfigurationDocument.load("never-written")


@pytest.mark.unit
class TestRejection:
    def test_unparseable_yaml_is_rejected(self, layer: Path) -> None:
        write_configuration(layer, "demo", "personas: [oops\n")

        with pytest.raises(MalformedConfigurationError):
            ConfigurationDocument.load("demo")

    def test_a_non_mapping_top_level_is_rejected(self, layer: Path) -> None:
        write_configuration(layer, "demo", "- one\n- two\n")

        with pytest.raises(MalformedConfigurationError, match="must be a mapping"):
            ConfigurationDocument.load("demo")

    @pytest.mark.parametrize(
        "text",
        ["personas: [oops\n", "- one\n"],
        ids=["unparseable", "wrong-shape"],
    )
    def test_the_message_names_the_file_and_the_layer(self, layer: Path, text: str) -> None:
        path = write_configuration(layer, "demo", text)

        with pytest.raises(MalformedConfigurationError) as caught:
            ConfigurationDocument.load("demo")

        assert str(path) in str(caught.value)
        assert LAYER in str(caught.value)

    def test_it_is_not_a_content_error(self, layer: Path) -> None:
        """Load-bearing. Consumers catch ContentError to mean "this configuration
        is absent, carry on with a default"; a present-and-wrong document caught
        by one of those handlers is the silent build this whole boundary exists
        to prevent."""
        from prompticorn.content.errors import ContentError

        assert not issubclass(MalformedConfigurationError, ContentError)


@pytest.mark.unit
class TestStructuralChecks:
    def test_a_missing_section_is_rejected(self, layer: Path) -> None:
        write_configuration(layer, "demo", "something_else: {}\n")

        document = ConfigurationDocument.load("demo")

        with pytest.raises(MalformedConfigurationError, match="no 'personas' section"):
            document.require_mapping("personas")

    def test_an_empty_section_is_rejected(self, layer: Path) -> None:
        """`personas: {}` parses, loads, and filters nothing — which at the output
        is indistinguishable from having asked for every agent."""
        write_configuration(layer, "demo", "personas: {}\n")

        document = ConfigurationDocument.load("demo")

        with pytest.raises(MalformedConfigurationError, match="empty"):
            document.require_mapping("personas")

    def test_a_section_of_the_wrong_type_is_rejected(self, layer: Path) -> None:
        write_configuration(layer, "demo", "personas:\n  - one\n")

        document = ConfigurationDocument.load("demo")

        with pytest.raises(MalformedConfigurationError, match="mapping of names"):
            document.require_mapping("personas")

    def test_a_non_mapping_entry_is_named(self, layer: Path) -> None:
        """Naming the key rather than the file, so the message points at a line."""
        write_configuration(layer, "demo", "personas:\n  ok: {}\n  broken: 3\n")

        document = ConfigurationDocument.load("demo")

        with pytest.raises(MalformedConfigurationError, match="'broken'"):
            document.require_mapping_values("personas")

    def test_a_string_list_may_be_absent(self, layer: Path) -> None:
        write_configuration(layer, "demo", "personas: {}\n")

        ConfigurationDocument.load("demo").require_string_list("universal_agents")

    def test_a_string_list_of_the_wrong_shape_is_rejected(self, layer: Path) -> None:
        write_configuration(layer, "demo", "universal_agents:\n  ask: yes\n")

        document = ConfigurationDocument.load("demo")

        with pytest.raises(MalformedConfigurationError, match="list of names"):
            document.require_string_list("universal_agents")
