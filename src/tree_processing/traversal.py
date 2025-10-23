from .actions import Node, _rejected


def _reorder(children, stack):
    internal = []
    for c in children:
        if c.internal:
            internal.append(c) # for second pass
        else:
            yield c
    for c in internal:
        if (yield c) is not _rejected:
            stack.append(c)


def topdown(root, get_children):
    stack = [Node(True, None, root, None)]
    while stack:
        top = stack.pop()
        if not top.internal:
            continue # skipped by processing
        yield from _reorder(get_children(top), stack)
