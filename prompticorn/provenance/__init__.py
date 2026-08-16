"""Provenance — making every generated file say where it came from.

Two mechanisms, deliberately unequal. The **sidecar**
(``.prompticorn/provenance.json``) is general and covers every output. **Inline
headers** are a convenience for formats that can carry a comment.

That split exists because JSON has none. Amazon Q, Bedrock and Gemini ship JSON
agents, and a `_prompticorn` key would pollute a schema the consuming tool
validates. Provenance that stopped at the formats with comment syntax would have
its gap exactly where a human is least able to notice it.
"""

from prompticorn.provenance.output_format import OutputFormat
from prompticorn.provenance.provenance_header import MARKER, ProvenanceHeader
from prompticorn.provenance.provenance_record import ProvenanceRecord
from prompticorn.provenance.provenance_sidecar import SIDECAR_FILENAME, ProvenanceSidecar

__all__ = [
    "MARKER",
    "SIDECAR_FILENAME",
    "OutputFormat",
    "ProvenanceHeader",
    "ProvenanceRecord",
    "ProvenanceSidecar",
]
