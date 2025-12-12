from .actions import Node
from . import rejected, traversal


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
