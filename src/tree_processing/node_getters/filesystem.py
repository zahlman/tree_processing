from os import scandir as _scan_directory
from pathlib import Path
from ..actions import Node


# Rule to get children of a filesystem node.
def _children_of(node):
    to_scan = node.current
    if isinstance(to_scan, tuple): # "mirroring" traversal
        to_scan = to_scan[0]
    with _scan_directory(to_scan) as entries:
        for entry in entries:
            yield (entry.is_dir(), entry.name, entry.path)


def make(node, entry):
    internal, name, path = entry
    new_current, new_parent = Path(path), node.current
    if isinstance(new_parent, tuple): # "mirroring" traversal.
        new_current = (new_current, new_parent[1] / name)
    return Node(internal, name, new_current, new_parent)


def get(parent: Node, onerror=None):
    try:
        return [make(parent, e) for e in _children_of(parent)]
    except OSError as e:
        return [] if onerror is None else onerror(e)
