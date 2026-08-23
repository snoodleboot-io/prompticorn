"""Regenerating a tree from the lock — the mechanism that makes output disposable.

``prompticorn regenerate`` is the documented answer to a hand-edited generated
file: recompile, don't edit. It rebuilds from what the lock already recorded
rather than re-resolving the project, and refuses if the sources have moved,
because a rebuild from moved sources cannot reproduce the locked tree.
"""

from prompticorn.regenerate.regeneration_report import RegenerationReport
from prompticorn.regenerate.regeneration_service import RegenerationService

__all__ = ["RegenerationReport", "RegenerationService"]
