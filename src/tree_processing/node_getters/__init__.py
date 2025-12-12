from os import scandir as _scan_directory
from pathlib import Path
from ..actions import Node
from .. import rejected


def _gen(raw_get, make_node, parent):
    nodes = (make_node(parent, child) for child in raw_get(parent))
    return (node for node in nodes if node is not rejected)


def make_getter(raw_get, make_node):
    return lambda parent: _gen(raw_get, make_node, parent)
