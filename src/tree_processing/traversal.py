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


def _organize(children, sort_key):
    to_push, leaves = _partition(children)
    if sort_key is not None:
        leaves.sort(key=sort_key)
        # When a sort key is provided, we must be careful about the order of
        # internal nodes. The first node in `to_push` will be pushed (or
        # queued) first, meaning it will be processed *last*. Therefore we
        # must reverse the list as well during sorting.
        to_push.sort(key=sort_key, reverse=True)
    return to_push, leaves


def _topdown_step(top, get, sort_key, enqueue):
    if (yield top) is rejected:
        return
    to_push, leaves = _organize(get(top), sort_key)
    # We can't use `yield from` here, because the caller may use
    # `.send` which the list iterator doesn't support.
    for leaf in leaves:
        yield leaf
    enqueue(to_push)


@traversal
def topdown(root, get, *, sort_key=None):
    stack = [root]
    while stack:
        top, enqueue = stack.pop(), stack.extend
        yield from _topdown_step(top, get, sort_key, enqueue)
