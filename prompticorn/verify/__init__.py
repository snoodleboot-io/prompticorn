"""Verification — proving a generated tree is still what the lock says it is.

The source/generated wall is only a wall if something enforces it. This module
is that enforcement: it answers whether every recorded output still exists with
the content the lock captured, whether anything exists that the lock does not
account for, and whether the lock can answer for itself.

Digests here are taken over the body with the provenance header stripped, which
is how `.prompticorn/provenance.json` digests too. Hashing the header would make
an output's digest move on a version bump that changed no content.
"""

from prompticorn.verify.errors import (
    OutputTamperedError,
    UnknownOutputError,
    VerificationError,
)
from prompticorn.verify.output_verifier import OutputVerifier
from prompticorn.verify.verification_finding import VerificationFinding
from prompticorn.verify.verification_kind import VerificationKind
from prompticorn.verify.verification_report import VerificationReport

__all__ = [
    "OutputTamperedError",
    "OutputVerifier",
    "UnknownOutputError",
    "VerificationError",
    "VerificationFinding",
    "VerificationKind",
    "VerificationReport",
]
