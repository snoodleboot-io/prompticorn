"""CLI commands that live outside ``cli.py``.

``cli.py`` is where the original commands grew up and it is long enough that
adding to it is no longer free. Everything new goes here, one concern per
module, and registers into the click group — so ``cli.py`` gains an import
rather than another few hundred lines (PRO-133).

Modules here hold *wiring and presentation*. The behaviour they invoke lives in
services, which is what lets it be tested without a terminal.
"""

from prompticorn.commands.profile_group import profile_group

__all__ = ["profile_group"]
