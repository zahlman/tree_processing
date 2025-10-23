from tree_processing.actions import _rejected


def _process_one(node, traversal, act, accumulate, total):
    result = act[0 if node.internal else 1](node)
    next_node = traversal.send(result)
    if result is not _rejected and accumulate is not None:
        total = accumulate(total, result)
    return next_node, total


def _process(traversal, act, accumulate, total):
    node = next(traversal)
    while True:
        try:
            node, total = _process_one(node, traversal, act, accumulate, total)
        except StopIteration:
            return total


def process(traverse, root, get_children, act, accumulate=None, total=None):
    traversal = traverse(root, get_children)
    try:
        process_folder, process_file = act
    except TypeError: # not iterable
        # If an iterable is provided but it has the wrong number of
        # callables, that `ValueError` should propagate.
        act = act, act
    return _process(traversal, act, accumulate, total)
