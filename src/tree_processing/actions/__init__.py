from functools import partial, wraps
from operator import add
from typing import Any, Callable, NewType

from ..node_getters import Node, NodeError
from .. import rejected


Action = NewType('Action', Callable[[Node], Any])
Filter = NewType('Filter', Callable[[Node], bool])


class _filter_chain(tuple):
    def __and__(self, another):
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


def filterable(func: Action):
    '''A decorator to add filtering to an Action.'''
    def _filtered(filter_chain: _filter_chain, node: Node):
        # Main traversal logic must check for this sentinel value
        # as well as checking if `internal` was set False.
        return func(node) if filter_chain(node) else rejected
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


# Shared with the traversal module. Could become public later.
def _normalize_act(act):
    try:
        process_folder, process_file = act
    except TypeError: # not iterable, so a single callable
        return act
    except ValueError: # a single callable, or else propagate the error
        act, = act
        return act
    else: # create a simple dispatch for the two callables.
        return lambda n: (process_folder if n.internal else process_file)(n)


def accumulator(initial, accumulate):
    """Decorator for accumulating results from actions (or action-pairs).

    An internal accumulator is initialized at the start of the traversal,
    and updated each time the action is applied to a node. (Note: if this is
    done by modifying the accumulator's state, the `accumulate` function must
    explicitly `return` the same object.) The update is skipped whenever the
    action's result is `rejected`.

    initial -> the initial state of the accumulator. Cannot be `rejected`.
    accumulate(current, result) -> a function which updates the accumulator.
        Given the `current` value of the accumulator and the `result` of
        acting on the current node, returns an updated result (may or may
        not be the same object as before). May not return `rejected`.

    This can be used to decorate any callable used as an action (applied to
    all nodes), or called with a pair of functions (applied to internal and
    leaf nodes respectively).
    """
    if initial is rejected:
        raise ValueError("cannot initialize accumulator with `rejected`")
    def _wrapper(*args):
        act = _normalize_act(args)
        accumulated = initial
        @wraps(act)
        def _wrapped(node):
            nonlocal accumulated
            result = act(node)
            if result is rejected:
                return rejected
            accumulated = accumulate(accumulated, result)
            if initial is rejected:
                raise NodeError("accumulator returned `rejected`")
            return accumulated
        return _wrapped
    return _wrapper


# The most common case of accumulation.
sum_results = accumulator(0, add)
sum_results.__qualname__ = sum_results.__name__ = 'sum_results'
sum_results.__doc__ = """\
Sums the results of actions applied at each node.

Equivalent to using `accumulator(0, add)`.

args -> a single action applied to all nodes, or a pair of actions where
        the first is applied to internal nodes and the second to leaves.
"""
