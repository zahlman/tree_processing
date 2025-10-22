from os import scandir as _scan_directory
from pathlib import Path

from . import make_getter
from ..actions import Node, _rejected


# Client code can customize the get and make routines by attaching filters
# and/or error handling and then calling make_getter().


def raw_get(node):
    to_scan = node.current
    if isinstance(to_scan, tuple): # "mirroring" traversal
        to_scan = to_scan[0]
    yield from _scan_directory(to_scan)


def make_node(parent_node, entry):
    new_current, new_parent = Path(entry.path), parent_node.current
    if isinstance(new_parent, tuple): # "mirroring" traversal.
        new_current = (new_current, new_parent[1] / entry.name)
    return Node(entry.is_dir(), entry.name, new_current, new_parent)


default_get = make_getter(raw_get, make_node)


def make_root(src, dst=None):
    return (Path(src),) if dst is None else (Path(src), Path(dst))
