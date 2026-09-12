"""The profile model (PRO-130).

The digest is the load-bearing part. A profile is hand-editable, and a reordered
key or an added comment must not read as a changed configuration — every lock
that references one would churn on formatting alone.
"""

from __future__ import annotations

import pytest

from prompticorn.profiles import Profile

PAYLOAD = {
    "repository": {"type": "single-language"},
    "spec": {"language": "python", "runtime": "3.14"},
    "variant": "verbose",
    "active_personas": ["software_engineer"],
    "ai_tool": "claude",
}


def profile(**overrides) -> Profile:
    fields = {"name": "backend", "version": 1, "payload": dict(PAYLOAD)}
    fields.update(overrides)
    return Profile(**fields)


class TestDigest:
    def test_key_order_does_not_change_the_digest(self):
        """The AC. Two captures of the same setup must agree however the YAML
        happened to be ordered."""
        forward = profile(payload={"a": 1, "b": 2})
        backward = profile(payload={"b": 2, "a": 1})

        assert forward.digest() == backward.digest()

    def test_nested_key_order_does_not_change_the_digest(self):
        """Sorting only the top level would leave every nested mapping unstable."""
        one = profile(payload={"spec": {"language": "python", "runtime": "3.14"}})
        two = profile(payload={"spec": {"runtime": "3.14", "language": "python"}})

        assert one.digest() == two.digest()

    def test_a_changed_value_changes_the_digest(self):
        """Guards the premise: a digest insensitive to content is not a digest."""
        assert profile().digest() != profile(payload={**PAYLOAD, "variant": "minimal"}).digest()

    def test_metadata_does_not_affect_the_digest(self):
        """Name, version and timestamp describe the capture, not the
        configuration. Including them would make two identical setups saved a
        minute apart look like different things."""
        early = profile(version=1, created_at="2026-01-01T00:00:00Z", description="first")
        late = profile(version=9, created_at="2026-09-12T00:00:00Z", description="ninth")

        assert early.digest() == late.digest()

    def test_the_digest_is_hex_sha256(self):
        digest = profile().digest()

        assert len(digest) == 64
        assert digest == digest.lower()
        int(digest, 16)


class TestRoundTrip:
    def test_a_profile_survives_a_mapping_round_trip(self):
        original = profile(description="house standard", created_at="2026-09-12T00:00:00Z")

        assert Profile.from_mapping(original.to_mapping()) == original

    def test_to_mapping_returns_a_fresh_payload(self):
        """A shared dict would let a caller mutate a stored profile in place."""
        original = profile()

        original.to_mapping()["payload"]["variant"] = "clobbered"

        assert original.payload["variant"] == "verbose"


class TestRejection:
    @pytest.mark.parametrize(
        "mapping",
        [
            {"name": "x", "version": 1},
            {"name": "x", "version": 1, "payload": "not a mapping"},
            {"name": "x", "payload": {}},
            {"version": 1, "payload": {}},
            {"name": "", "version": 1, "payload": {}},
            {"name": "x", "version": "not a number", "payload": {}},
        ],
        ids=["no payload", "payload not a mapping", "no version", "no name", "empty name", "bad version"],
    )
    def test_an_unusable_document_is_refused(self, mapping):
        """A half-understood profile applied to a project writes a half-correct
        manifest, which is worse than refusing to read it."""
        with pytest.raises(ValueError):
            Profile.from_mapping(mapping)

    def test_a_non_mapping_is_refused(self):
        with pytest.raises(ValueError):
            Profile.from_mapping(["not", "a", "mapping"])  # type: ignore[arg-type]
