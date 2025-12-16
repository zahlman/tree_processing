from functools import partial, wraps

from . import rejected
from .actions import _normalize_act


def _process(traversal, act):
    node, act = next(traversal), _normalize_act(act)
    while True:
        result = act(node)
        try:
            node = traversal.send(result)
        except StopIteration:
            return result


def process(traverse, root, get_children, act, sort_key=None):
    return _process(iter(traverse(root, get_children, sort_key=sort_key)), act)


class Traversal:
    def __init__(self, traverse, root, get_children, sort_key=None):
        self._traverse = partial(traverse, root, get_children)
        self._sort_key = sort_key


    def __iter__(self):
        yield from self._traverse(sort_key=self._sort_key)


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


def _recurse_over(children, stack, sort_key):
    to_push, leaves = _partition(children)
    if sort_key is None:
        # The first internal node should go on the stack last, so that it will
        # be processed first. But children should be iterated in order,
        # because they're being yielded directly.
        # (We must use a stack in order to have a depth-first traversal.)
        for leaf in leaves:
            yield leaf # can't use `yield from`; need to swallow `send` values
        stack.extend(to_push[::-1])
    else:
        # Similarly, when the nodes are sorted, the internal nodes need to be
        # sorted in reverse order.
        for leaf in sorted(leaves, key=sort_key):
            yield leaf
        stack.extend(sorted(to_push, key=sort_key, reverse=True))


@traversal
def topdown(root_node, get_children, sort_key=None):
    stack = [root_node]
    while stack:
        top = stack.pop()
        if (yield top) is not rejected:
            yield from _recurse_over(get_children(top), stack, sort_key)
