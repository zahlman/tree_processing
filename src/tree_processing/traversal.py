def _reorder(children, stack):
    internal = []
    for c in children:
        if c.internal:
            internal.append(c) # for second pass
        else:
            yield c
    for c in internal:
        if (yield c):
            stack.append(c)


def topdown(root, get_children):
    stack = [root]
    while stack:
        top = stack.pop()
        if not top.internal:
            continue # skipped by processing
        yield from _reorder(get_children(top), stack)
