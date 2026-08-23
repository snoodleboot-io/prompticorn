"""Resolving the current project into a lock (PRO-111).

Turns "what this project is right now" into a :class:`LockFile`: the manifest's
digest, the artifacts its requirements resolve to, every content unit with its
layer and digest, and the files a build produced.

Resolution is deliberately **pure with respect to time**. The caller supplies
``resolved_at`` rather than the resolver reading the clock, so a test can compare
two resolutions without one of them being a moving target — and so the writer's
timestamp-preservation rule stays the only thing deciding when the stamp advances.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from prompticorn.artifact.bundled_identity import BundledIdentity
from prompticorn.artifact.package_version import bundled_version
from prompticorn.artifact.pinned_artifact import PinnedArtifact
from prompticorn.content.content_resolver import ContentResolver, default_resolver
from prompticorn.content.digest import digest_text
from prompticorn.lockfile.lock_file import LockFile
from prompticorn.lockfile.locked_artifact import LockedArtifact
from prompticorn.lockfile.locked_output import LockedOutput
from prompticorn.lockfile.locked_unit import LockedUnit
from prompticorn.manifest.manifest_schema import ManifestSchema
from prompticorn.provenance.output_format import OutputFormat
from prompticorn.provenance.provenance_header import ProvenanceHeader

LOCK_FILENAME = "prompticorn.lock"


@dataclass(frozen=True)
class LockResolver:
    """Builds a :class:`LockFile` from the project as it stands.

    Attributes:
        resolver: Where content comes from. Injectable so a test can resolve
            against a fixture tree rather than the bundled one.
        identity: Assigns artifact identities to bundled content.
    """

    resolver: ContentResolver
    identity: BundledIdentity

    @classmethod
    def create(cls, resolver: ContentResolver | None = None) -> LockResolver:
        """A resolver over the default content stack."""
        return cls(
            resolver=resolver if resolver is not None else default_resolver(),
            identity=BundledIdentity(),
        )

    def resolve(
        self,
        config: dict,
        resolved_at: str,
        manifest_text: str | None = None,
        output_root: Path | None = None,
        output_paths: tuple[str, ...] = (),
    ) -> LockFile:
        """Resolve the current project state into a lock.

        Args:
            config: The loaded manifest.
            resolved_at: Timestamp for this resolution, ISO-8601 UTC. Supplied
                rather than read from the clock — see the module docstring.
            manifest_text: Raw manifest bytes, for the digest. None when there is
                no file on disk, in which case manifest drift is undecidable and
                left so rather than guessed.
            output_root: Directory generated files live under.
            output_paths: Roots a build emits, e.g. ``.claude/``, ``CLAUDE.md``.

        Returns:
            The resolved lock, with every sequence in canonical order.
        """
        return LockFile(
            prompticorn_version=bundled_version().render(),
            resolved_at=resolved_at,
            artifacts=self._resolve_artifacts(config),
            units=self._resolve_units(),
            outputs=_digest_outputs(output_root, output_paths),
            manifest_digest=digest_text(manifest_text) if manifest_text is not None else None,
        ).canonical()

    def _resolve_artifacts(self, config: dict) -> tuple[LockedArtifact, ...]:
        """Every declared requirement, resolved to an exact artifact.

        Only the ``local`` namespace exists today, so a declaration resolves to
        the bundled artifact of the same coordinate at the package version. When
        real sources arrive this is where they plug in; the shape of the result
        does not change.
        """
        schema = ManifestSchema.parse(config)
        resolved = []
        for declaration in schema.artifacts:
            artifact_id = self.identity.for_coordinate(declaration.name)
            resolved.append(
                LockedArtifact(
                    pinned=PinnedArtifact(
                        artifact_id=artifact_id,
                        digest=self._artifact_digest(declaration.name),
                    ),
                    source=declaration.source,
                )
            )
        return tuple(resolved)

    def _artifact_digest(self, coordinate: str) -> str:
        """Digest covering everything the artifact contains.

        Built from the units' own digests rather than by re-reading content: the
        unit digests are already canonical, so composing them keeps one
        definition of canonicalisation in the codebase instead of two that can
        drift apart.
        """
        members = [
            f"{unit.id.render()}:{self.resolver.digest(unit.id)}"
            for unit in self.resolver.units()
            if self.identity.for_unit(unit.id).coordinate == coordinate
        ]
        return digest_text("\n".join(sorted(members)))

    def _resolve_units(self) -> tuple[LockedUnit, ...]:
        """Every resolvable unit, with the layer that supplied it."""
        return tuple(
            LockedUnit(id=unit.id, layer=unit.layer, digest=self.resolver.digest(unit.id))
            for unit in self.resolver.units()
        )


def _digest_outputs(root: Path | None, paths: tuple[str, ...]) -> tuple[LockedOutput, ...]:
    """Digest every generated file under the given roots.

    Paths are recorded POSIX-relative to ``root`` so a lock written on Windows
    and one written on Linux describe the same tree.
    """
    if root is None or not paths:
        return ()

    outputs = []
    for raw_path in sorted(paths):
        target = root / raw_path.rstrip("/")
        if target.is_file():
            outputs.append(_locked_output(root, target))
        elif target.is_dir():
            outputs.extend(
                _locked_output(root, found)
                for found in sorted(target.rglob("*"))
                if found.is_file()
            )
    return tuple(outputs)


def _locked_output(root: Path, path: Path) -> LockedOutput:
    """Digest one output, with its provenance header stripped (PRO-115).

    Stripped rather than whole-file for two reasons. The header embeds the
    artifact version, so hashing it would move every output's digest on a
    version bump that changed no content. And `.prompticorn/provenance.json`
    digests the body the same way — two mechanisms describing the same file and
    disagreeing about it is worse than either one alone.
    """
    relative = path.relative_to(root).as_posix()
    return LockedOutput(
        path=relative,
        digest=ProvenanceHeader.body_digest(
            path.read_text(encoding="utf-8"), OutputFormat.of(relative)
        ),
    )
