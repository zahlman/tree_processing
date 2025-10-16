from os import scandir
from pathlib import Path
from shutil import copy
from typing import Tuple
from .actions import chainable, filterable, Node


# Rule to get children of a filesystem node.
def _wrap_scandir(node):
    to_scan = node.current
    if isinstance(to_scan, tuple): # "mirroring" traversal
        to_scan = to_scan[0]
    with scandir(to_scan) as entries:
        for entry in entries:
            yield (entry.is_dir(), entry.name, entry.path)


def make(node, entry):
    internal, name, path = entry
    new_current, new_parent = Path(path), node.current
    if isinstance(new_parent, tuple): # "mirroring" traversal.
        new_current = (new_current, new_parent[1] / name)
    return Node(internal, name, new_current, new_parent)


def get_children(parent: Node, onerror=None):
    try:
        return [make(parent, e) for e in _wrap_scandir(parent)]
    except OSError as e:
        return [] if onerror is None else onerror(e)


# Some useful actions and filters specifically for filesystem traversals.


@chainable
def not_hidden(node: Node):
    return not node.name.startswith('.')


@chainable
def src_is_regular_file(node: Node):
    src, dst = node.current
    return src.is_file()


@filterable
def recurse_into_folders(node: Node):
    '''A helper to do nothing special with folders.'''
    pass


# Adapt a function that accepts src and dst paths,
# into one that expects a `(src, dst)` pair in `node.current`.
def _mirror(func):
    return filterable(lambda node: func(*node.current))


#hardlink_or_copy_files = _reflect_regular_file(hardlink_or_copy)
copy_files = _mirror(filterable(copy).which(src_is_regular_file))


def _fake_copy(src, dst): # For testing.
    print(f'Would copy {src} to {dst}')


fake_copy_files = filterable(_mirror(_fake_copy)).which(src_is_regular_file)


@filterable
def propagate_folders(node: Node):
    src, dst = node.current
    assert src.is_dir()
    dst.mkdir(exist_ok=True)


@filterable
def fake_propagate_folders(node: Node):
    src, dst = node.current
    assert src.is_dir()
    print(f'Would create folder {dst} if missing')
