from functools import partial
from shutil import copy
from typing import Any, Callable, NamedTuple, NewType, Self


class Node(NamedTuple):
    '''Structure representing a node in a traversal.'''
    internal: bool # whether the node may potentially have children.
    # In top-down traversals, this value is checked after processing,
    # so it can be set to False to prevent recursing over children.
    name: Any # a relationship between the parent and current nodes.
    current: Any # The current node in the traversal.
    parent: Any # The parent of the current node in the traversal.
    # N.B. For "mirroring" operations, `current` and `parent` could be
    # (src, dst) tuples rather than single values.


class NodeError(ValueError):
    '''Represents encountering a node in a traversal which should abort
    the entire traversal with an error (which can be detected to
    trigger any necessary cleanup).'''
    pass


Action = NewType('Action', Callable[[Node], Any])
Filter = NewType('Filter', Callable[[Node], bool])


class _filter_chain(tuple):
    def __and__(self, another: Filter | Self):
        # Attempt to "flatten" concatenated chains.
        # Chains are callable (and in fact Filters), so it's not a real
        # problem if this fails.
        if isinstance(another, _filter_chain):
            return _filter_chain(self + another)
        if callable(another):
            return _filter_chain(self + (another,))
        raise TypeError("can only concatenate a callable or another chain")


    def __call__(self, node: Node):
        return all(f(node) for f in self)


def chainable(func: Filter):
    '''A decorator to make a Filter chainable.'''
    return _filter_chain() & func


_rejected = object()
def filterable(func: Action):
    '''A decorator to add filtering to an Action.'''
    def _filtered(filter_chain: _filter_chain, node: Node):
        # Main traversal logic must check for this sentinel value
        # as well as checking if `internal` was set False.
        return func(node) if filter_chain(node) else _rejected
    def _result(filter_chain: _filter_chain):
        result = partial(_filtered, filter_chain)
        result.which = lambda another: _result(filter_chain & another)
        return result
    return _result(_filter_chain())


def require(f: Filter):
    def wrapper(node: Node):
        if not f(node):
            raise NodeError 
        return True
    return wrapper
