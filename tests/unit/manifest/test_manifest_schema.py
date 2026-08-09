"""Validation of the v2 manifest keys (PRO-109).

The rejection table is the load-bearing part. A manifest is hand-edited YAML, so
every error has to name the key path that is at fault — an error without a
location sends the author scanning the file by eye.
"""

import pytest

from prompticorn.manifest import (
    ManifestSchema,
    ManifestSchemaError,
    ManifestVersionError,
    SourceType,
)


def test_a_v1_config_yields_an_empty_schema() -> None:
    """The overwhelmingly common case: neither new key is present."""
    schema = ManifestSchema.parse({"version": "1.0", "spec": {"language": "python"}})

    assert schema.artifacts == ()
    assert schema.sources == ()


def test_an_empty_config_yields_an_empty_schema() -> None:
    assert ManifestSchema.parse({}) == ManifestSchema()


@pytest.mark.parametrize("absent", [{}, {"artifacts": None, "sources": None}])
def test_explicit_null_counts_as_absent(absent: dict) -> None:
    """The shape left behind by commenting out every entry under a key."""
    assert ManifestSchema.parse(absent) == ManifestSchema()


def test_artifacts_parse_into_requirements() -> None:
    schema = ManifestSchema.parse(
        {"artifacts": [{"name": "acme/security-agent", "version": ">=2.1,<3"}]}
    )

    assert len(schema.artifacts) == 1
    assert schema.artifacts[0].requirement.render() == "acme/security-agent@>=2.1.0,<3.0.0"
    assert schema.artifacts[0].source is None


def test_an_unqualified_name_gets_the_default_namespace() -> None:
    """Same rule as everywhere else: namespace defaults to `local`."""
    schema = ManifestSchema.parse({"artifacts": [{"name": "threat-skills", "version": "==1.4.0"}]})

    assert schema.artifacts[0].name == "local/threat-skills"


def test_sources_parse_into_declarations() -> None:
    schema = ManifestSchema.parse({"sources": [{"name": "acme-internal", "type": "builtin"}]})

    assert schema.sources[0].name == "acme-internal"
    assert schema.sources[0].type is SourceType.BUILTIN


def test_declaration_order_is_preserved() -> None:
    """Order is the author's; nothing here should quietly re-sort their file."""
    schema = ManifestSchema.parse(
        {
            "artifacts": [
                {"name": "b", "version": "==1.0.0"},
                {"name": "a", "version": "==1.0.0"},
            ]
        }
    )

    assert [a.name for a in schema.artifacts] == ["local/b", "local/a"]


def test_an_artifact_may_name_a_declared_source() -> None:
    schema = ManifestSchema.parse(
        {
            "sources": [{"name": "acme-internal", "type": "builtin"}],
            "artifacts": [{"name": "a", "version": "==1.0.0", "source": "acme-internal"}],
        }
    )

    assert schema.artifacts[0].source == "acme-internal"


# ── the rejection table ────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("config", "key_path", "reason_fragment"),
    [
        # Wrong container types.
        ({"artifacts": {"a": "1"}}, "artifacts", "expected a list, got a mapping"),
        ({"sources": "acme"}, "sources", "expected a list, got a string"),
        ({"artifacts": ["a@1.0.0"]}, "artifacts[0]", "expected a mapping"),
        # Missing and blank required fields.
        ({"artifacts": [{"version": "==1.0.0"}]}, "artifacts[0].name", "required but missing"),
        ({"artifacts": [{"name": "a"}]}, "artifacts[0].version", "required but missing"),
        ({"artifacts": [{"name": "", "version": "==1.0.0"}]}, "artifacts[0].name", "is empty"),
        ({"sources": [{"name": "s"}]}, "sources[0].type", "required but missing"),
        # Wrong scalar types.
        (
            {"artifacts": [{"name": ["a"], "version": "==1.0.0"}]},
            "artifacts[0].name",
            "expected a string, got a list",
        ),
        ({"version": 2.0}, "version", "expected a string"),
        # Typos are named, never silently ignored.
        (
            {"artifacts": [{"name": "a", "version": "==1.0.0", "versoin": "x"}]},
            "artifacts[0]",
            "unknown key(s) 'versoin'",
        ),
        ({"sources": [{"name": "s", "type": "builtin", "url": "x"}]}, "sources[0]", "unknown key"),
        # Delegated grammar failures, re-pointed at the key actually at fault.
        ({"artifacts": [{"name": "a", "version": ">=oops"}]}, "artifacts[0].version", "invalid"),
        ({"artifacts": [{"name": "A/B", "version": ">=1.0.0"}]}, "artifacts[0].name", "uppercase"),
        # Unknown source type lists what is legal.
        (
            {"sources": [{"name": "s", "type": "git"}]},
            "sources[0].type",
            "expected one of: builtin",
        ),
    ],
)
def test_invalid_manifests_are_rejected_with_a_key_path(
    config: dict, key_path: str, reason_fragment: str
) -> None:
    with pytest.raises(ManifestSchemaError) as caught:
        ManifestSchema.parse(config)

    assert caught.value.key_path == key_path
    assert reason_fragment in caught.value.reason
    # The path leads the message, so it is the first thing the author reads.
    assert str(caught.value).startswith(f"{key_path}: ")


def test_duplicate_artifacts_are_rejected() -> None:
    """The chosen list-of-mappings shape makes duplicates syntactically legal.

    Two entries for one artifact have no defined winner, so silently taking one
    would be a coin flip the author never sees.
    """
    with pytest.raises(ManifestSchemaError) as caught:
        ManifestSchema.parse(
            {
                "artifacts": [
                    {"name": "a", "version": ">=1.0.0"},
                    {"name": "a", "version": "==2.0.0"},
                ]
            }
        )

    assert caught.value.key_path == "artifacts[1].name"
    assert "duplicate" in caught.value.reason


def test_duplicates_are_detected_across_namespace_spellings() -> None:
    """`a` and `local/a` are the same artifact, so declaring both is a duplicate."""
    with pytest.raises(ManifestSchemaError):
        ManifestSchema.parse(
            {
                "artifacts": [
                    {"name": "a", "version": ">=1.0.0"},
                    {"name": "local/a", "version": "==2.0.0"},
                ]
            }
        )


def test_duplicate_sources_are_rejected() -> None:
    with pytest.raises(ManifestSchemaError) as caught:
        ManifestSchema.parse(
            {"sources": [{"name": "s", "type": "builtin"}, {"name": "s", "type": "builtin"}]}
        )

    assert caught.value.key_path == "sources[1].name"


def test_an_undeclared_source_reference_is_rejected() -> None:
    """Otherwise this fails much later, at resolution, pointing at nothing."""
    with pytest.raises(ManifestSchemaError) as caught:
        ManifestSchema.parse({"artifacts": [{"name": "a", "version": "==1.0.0", "source": "nope"}]})

    assert caught.value.key_path == "artifacts[0].source"
    assert "undeclared source 'nope'" in caught.value.reason


def test_the_undeclared_source_message_lists_what_is_available() -> None:
    with pytest.raises(ManifestSchemaError) as caught:
        ManifestSchema.parse(
            {
                "sources": [{"name": "acme-internal", "type": "builtin"}],
                "artifacts": [{"name": "a", "version": "==1.0.0", "source": "typo"}],
            }
        )

    assert "acme-internal" in caught.value.reason


# ── schema versioning ──────────────────────────────────────────────────────────


@pytest.mark.parametrize("version", ["1.0", "2.0"])
def test_supported_versions_are_accepted(version: str) -> None:
    assert ManifestSchema.parse({"version": version}) == ManifestSchema()


def test_an_absent_version_is_treated_as_v1() -> None:
    """`version` was inert before this ticket, so its absence says nothing."""
    assert ManifestSchema.parse({"spec": {}}) == ManifestSchema()


def test_a_future_schema_version_is_an_upgrade_error_not_a_syntax_error() -> None:
    """Telling the user to fix a typo that is not there would waste their time."""
    with pytest.raises(ManifestVersionError) as caught:
        ManifestSchema.parse({"version": "3.0"})

    assert caught.value.found == "3.0"
    assert "Upgrade prompticorn" in str(caught.value)


def test_the_version_error_is_not_a_schema_error() -> None:
    """A caller distinguishing them must not have to parse the message."""
    with pytest.raises(ManifestVersionError):
        ManifestSchema.parse({"version": "99.0"})

    assert not issubclass(ManifestVersionError, ManifestSchemaError)
