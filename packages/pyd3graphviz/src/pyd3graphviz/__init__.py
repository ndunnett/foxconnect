"""
This module contains the d3-graphviz distribution files.
"""

import importlib.resources
from importlib.abc import Traversable

__all__ = ("d3graphviz_node_modules",)


def d3graphviz_node_modules() -> Traversable:
    """Returns a traversable to the `node_modules` directory for d3-graphviz distribution files."""
    return importlib.resources.files("pyd3graphviz") / "node_modules"
