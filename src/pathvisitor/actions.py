from functools import partial
from os import PathLike
from pathlib import Path
from shutil import copy
from typing import Any, Callable, NamedTuple, NewType


class Node(NamedTuple):
    internal: bool
    name: Any # a relationship between the parent and current nodes.
    current: Any # The current node in the traversal.
    parent: Any # The parent of the current node in the traversal.
    parent_result: Any # The return value from processing the parent.
    # May be used for example to keep track of position in a destination
    # tree for copying operations.


def node_from_paths(path: PathLike):
    path = Path(path).absolute()
    return Node(path.is_dir(), path.name, path, path.parent)


Action = NewType('Action', Callable[[Node], Any])


class _chain(tuple):
    def __and__(self, another):
        if isinstance(another, _chain):
            return _chain(self + another)
        if callable(another):
            return _chain(self + (another,))
        raise TypeError("can only concatenate a callable or another chain")


    def __call__(self, node: Node):
        return all(f(node) for f in self)


def chainable(func: Action):
    '''A decorator to make a Action chainable.'''
    return _chain() & func


_rejected = object()
def filterable(func: Action):
    '''A decorator to add filtering to an Action.'''
    def _filtered(filter_chain: _chain, node: Node):
        return func(node) if filter_chain(node) else _rejected
    def _result(filter_chain: _chain):
        result = partial(_filtered, filter_chain)
        result.which = lambda another: _result(filter_chain & another)
        return result
    return _result(_chain())


# Some useful actions specifically for filesystem traversals.


@chainable
def not_hidden(node: Node):
    return not node.name.startswith('.')


@filterable
def recurse_into_folders(node: Node):
    '''A helper to do nothing special with folders.'''
    pass


# Adapt a function that accepts src and dst paths,
# into one that works with the above interface.
def _reflect_regular_file(func: Action):
    def reflected(node: Node):
        src, dst = node.current, (node.parent_result / node.name)
        if not src.is_file():
            raise ValueError(f"non-regular file {src} not supported")
        func(src, dst)
        return dst
    return reflected


#hardlink_or_copy_files = _reflect_regular_file(hardlink_or_copy)
copy_files = _reflect_regular_file(copy)


@_reflect_regular_file
def fake_copy_files(src, dst): # For testing.
    print(f'Would copy {src} to {dst}')


def copy_folder(node: Node):
    assert node.current.is_dir()
    dst = node.parent_result / node.name
    dst.mkdir(exist_ok=True)
    return dst
