from collections import deque
from functools import partial, wraps

from . import rejected
from .actions import _normalize_act


def _process(nodes, act):
    node, act = next(nodes), _normalize_act(act)
    while True:
        result = act(node)
        try:
            node = nodes.send(result)
        except StopIteration:
            return result


def process(walk, root, get, act, *, sort_key=None):
    return _process(walk(root, get, sort_key=sort_key), act)


class Traversal:
    def __init__(self, walk, root, get, *, sort_key=None):
        self._walk = partial(walk, root, get, sort_key=sort_key)


    def __iter__(self):
        yield from self._walk()


    def __call__(self, *act):
        return _process(iter(self), act)


def traversal(func):
    """Converts traversal generators into `Traversal` constructors."""
    return wraps(func)(partial(Traversal, func))


def _partition(children):
    internal_nodes, leaves = [], []
    for c in children:
        if c.internal:
            internal_nodes.append(c)
        else:
            leaves.append(c)
    return internal_nodes, leaves


def _organize(children, sort_key, depth_first):
    to_push, leaves = _partition(children)
    if sort_key is not None:
        leaves.sort(key=sort_key)
        # When a sort key is provided, we must be careful about the order of
        # internal nodes. For depth-first traversals, the first node in
        # `to_push` will be pushed first, meaning it will be processed *last*.
        # Therefore we must reverse the list as well during sorting.
        # For breadth-first traversals, the first node in `to_push` is still
        # enqueued first, but it will also be processed first as a result.
        to_push.sort(key=sort_key, reverse=depth_first)
    return to_push, leaves


def _topdown_step(top, get, sort_key, depth_first, enqueue):
    if (yield top) is rejected:
        return
    to_push, leaves = _organize(get(top), sort_key, depth_first)
    # We can't use `yield from` here, because the caller may use
    # `.send` which the list iterator doesn't support.
    for leaf in leaves:
        yield leaf
    enqueue(to_push)


def _topdown(root, get, depth_first, sort_key):
    stack = deque([root])
    pop = stack.pop if depth_first else stack.popleft
    enqueue = stack.extend
    while stack:
        yield from _topdown_step(pop(), get, sort_key, depth_first, enqueue)


@traversal
def topdown(root, get, *, sort_key=None):
    yield from _topdown(root, get, True, sort_key)
top_down = topdown
topdown_depth_first = topdown
top_down_depth_first = topdown


@traversal
def topdown_breadth_first(root, get, *, sort_key=None):
    yield from _topdown(root, get, False, sort_key)
top_down_breadth_first = topdown_breadth_first
