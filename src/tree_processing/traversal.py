from .actions import Node
from . import rejected, traversal


def _reorder(children, stack):
    internal = []
    for c in children:
        if c.internal:
            internal.append(c) # for second pass
        else:
            yield c
    for c in internal:
        if (yield c) is not rejected:
            stack.append(c)


@traversal
def topdown(root, get_children):
    root_node = Node(True, None, root, None)
    # FIXME: The root node should get included, but in order for it to be
    # properly processed, it has to get named first somehow.
    # yield root_node
    stack = [root_node]
    while stack:
        top = stack.pop()
        yield from _reorder(get_children(top), stack)
