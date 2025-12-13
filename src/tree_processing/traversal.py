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


def process(traverse, root, get_children, act):
    return _process(iter(traverse(root, get_children)), act)


class Traversal:
    def __init__(self, traverse, root, get_children):
        self._traverse, self._root, self._get = traverse, root, get_children


    def __iter__(self):
        yield from self._traverse(self._root, self._get)


    def __call__(self, *act):
        return _process(iter(self), act)


def traversal(func):
    """Converts traversal generators into `Traversal` constructors."""
    return wraps(func)(partial(Traversal, func))


def _recurse_over(children, stack):
    # The first internal node should go on the stack last, so that it will be
    # processed first. But children should be iterated in order, because
    # they're being yielded directly.
    # (We must use a stack in order to have a depth-first traversal.)
    to_push = []
    for c in children:
        if c.internal:
            to_push.append(c)
        else:
            yield c
    stack.extend(to_push[::-1])


@traversal
def topdown(root_node, get_children):
    stack = [root_node]
    while stack:
        top = stack.pop()
        if (yield top) is not rejected:
            yield from _recurse_over(get_children(top), stack)
