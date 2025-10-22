def topdown(root, get_children):
    stack = [root]
    while stack:
        top = stack.pop()
        if not top.internal:
            continue # skipped by processing
        children = get_children(top)
        for c in children:
            if not c.internal:
                yield c
        for c in children:
            if c.internal:
                recurse = (yield c)
            if recurse:
                stack.append(c)
