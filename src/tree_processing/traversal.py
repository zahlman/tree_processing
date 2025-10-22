def topdown(root, get_children):
    stack = [root]
    while stack:
        top = stack.pop()
        if not top.internal:
            continue # skipped by processing
        children = get_children(top)
        internal = []
        for c in children:
            if not c.internal:
                yield c
            else:
                internal.append(c) # for second pass
        for c in internal:
            recurse = (yield c)
            if recurse:
                stack.append(c)
