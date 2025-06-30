from functools import partial
from os import PathLike, walk
from pathlib import Path
from shutil import copy
from typing import Any, Callable, NamedTuple, NewType, Optional


class Node(NamedTuple):
    root: Any # The root node of the tree being traversed.
    current: Any # The current node in the traversal.
    path: Any # A representation of where the current node is in the tree.


def node_from_paths(root: PathLike, relative: PathLike):
    return Node(Path(root), Path(root) / relative, Path(relative))


Action = NewType('Action', Callable[[Node], Any])
# The callable takes the root of the "destination" tree as well as a Node.
TargetedAction = NewType('TargetedAction', Callable[[Any, Node], Any])


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


def targetable(func: TargetedAction):
    '''A decorator to add targeting (and filtering) to a TargetedAction.'''
    func.to = lambda target: filterable(partial(func, target))
    return func


# Some useful actions specifically for filesystem traversals.


@chainable
def not_hidden(node: Node):
    return not node.path.name.startswith('.')


@filterable
def recurse_into_folders(src: Path, item: Path):
    '''A helper to do nothing special with folders.'''
    pass


# Adapt a function that accepts src and dst paths,
# into one that works with the above interface.
def _reflect_regular_file(func: Callable[[Path, Path], Any]):
    def reflected(dst: Path, src: Node):
        src, dst = src.current, (dst / src.path)
        if not src.is_file():
            raise ValueError(f"non-regular file {src} not supported")
        func(src, dst)
        return dst
    return reflected


#hardlink_or_copy_files = targetable(_reflect_regular_file(hardlink_or_copy))
copy_files = targetable(_reflect_regular_file(copy))


@targetable
@_reflect_regular_file
def fake_copy_files(src, dst): # For testing.
    print(f'Would copy {src} to {dst}')


@targetable
def copy_folder(dst: Path, src: Node):
    assert src.current.is_dir()
    (dst / src.path).mkdir(exist_ok=True)
