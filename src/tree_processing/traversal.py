from .actions import Node
from . import rejected, traversal


def _recurse_over(children, stack):
    for c in children:
        if c.internal:
            stack.append(c)
        else:
            yield c


@traversal
def topdown(root_node, get_children):
    stack = [root_node]
    while stack:
        top = stack.pop()
        if (yield top) is not rejected:
            yield from _recurse_over(get_children(top), stack)
