"""What a generated file says about where it came from (PRO-112)."""

from __future__ import annotations

from dataclasses import dataclass

UNIT_KEY = "unit"
LAYER_KEY = "layer"
VERSION_KEY = "version"
DIGEST_KEY = "digest"

# Field order in the rendered header. Fixed rather than derived from the
# dataclass so that reordering the attributes cannot silently rewrite every
# generated file in the repository.
FIELD_ORDER = (UNIT_KEY, LAYER_KEY, VERSION_KEY, DIGEST_KEY)


@dataclass(frozen=True)
class ProvenanceRecord:
    """The provenance of one generated file.

    Attributes:
        unit: The source unit this was generated from, e.g. ``agent/code``.
        layer: Which source supplied that unit — the answer to "which layer won"
            at the moment of generation.
        version: The artifact version the unit came from.
        digest: sha256 of the generated body **with the header stripped**.
            Computed that way because writing the digest into the header would
            otherwise change the digest.
    """

    unit: str
    layer: str
    version: str
    digest: str

    def to_mapping(self) -> dict[str, str]:
        """Plain data for the sidecar. A fresh dict every call."""
        return {
            UNIT_KEY: self.unit,
            LAYER_KEY: self.layer,
            VERSION_KEY: self.version,
            DIGEST_KEY: self.digest,
        }

    def to_header_body(self) -> str:
        """The ``key=value`` run that goes inside a comment.

        Values are not quoted or escaped, so anything containing whitespace
        would make the header ambiguous to parse back. Nothing that reaches here
        can: unit ids, layer names and versions are all restricted charsets, and
        a digest is hex.
        """
        pairs = self.to_mapping()
        return " ".join(f"{key}={pairs[key]}" for key in FIELD_ORDER)

    @classmethod
    def from_mapping(cls, mapping: dict[str, str]) -> ProvenanceRecord:
        """Rebuild from sidecar data."""
        return cls(
            unit=mapping[UNIT_KEY],
            layer=mapping[LAYER_KEY],
            version=mapping[VERSION_KEY],
            digest=mapping[DIGEST_KEY],
        )
