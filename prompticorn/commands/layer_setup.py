"""Installing a project's content layers for the length of one command (PRO-117).

Kept out of ``cli.py`` (PRO-133). Every command reads content through
``default_resolver()``; this swaps that for the project's layer stack before the
command runs, so a build and the lock it writes resolve from the same layers.

This is also the one place the process environment is read for layering. The
providers receive it as data through :class:`LayerContext`, which is what lets
their tests describe a machine without touching the real one.
"""

from __future__ import annotations

import os
from pathlib import Path

from prompticorn.content.content_resolver import install_resolver
from prompticorn.layers import LayerContext, LayerStack


def install_project_layers(project_root: Path) -> list[str]:
    """Resolve content for ``project_root`` through its layer stack.

    Returns:
        The active layers, highest first — for anything that wants to say
        which are in play.
    """
    context = LayerContext(project_root=project_root, environment=dict(os.environ))
    stack = LayerStack.default()
    install_resolver(stack.resolver(context))
    return stack.describe(context)
