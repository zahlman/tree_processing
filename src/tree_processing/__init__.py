class rejected:
    """A special value used to indicate that a node was "rejected"
    during the processing of a tree.

    An "action" callable can return this to indicate that a leaf node didn't
    produce a value that should be accumulated; for a top-down traversal,
    returning this for an internal node causes its children to be pruned.

    This is therefore not a valid result for accumulation; as an
    implementation detail, the accumulator is initialized with this value to
    signal that actions won't expect an accumulator argument.

    Likewise, a Node-creation function can return this value to skip creating
    a Node from a given raw-get result. (The raw-getter should not normally
    yield this value; the Node-creator will have to handle it if it does.)
    """
    # The object is intended to be singleton, so the name is re-bound so as to
    # avoid exposing a name for the class. This can't protect against
    # deliberate hacks like `tree_processing.rejected = ...` or
    # `rejected_copy = rejected.__class__()`, and doesn't try.
    # However, avoiding mutation of the singleton instance seems worthwhile,
    # and possibly saves a few bytes of memory.
    __slots__ = ()
rejected = rejected()


def _process_one(node, traversal, act, accumulator):
    act = act[0 if node.internal else 1]
    use_accumulator = (accumulator[0] is not rejected)
    result = act(node, accumulator[0]) if use_accumulator else act(node)
    if result is not rejected and use_accumulator:
        accumulator[0] = result
    return traversal.send(result)


def _process(traversal, act, accumulator):
    node = next(traversal)
    while True:
        try:
            node = _process_one(node, traversal, act, accumulator)
        except StopIteration:
            return accumulator[0]


def process(traverse, root, get_children, act, initial=rejected):
    traversal = traverse(root, get_children)
    try:
        process_folder, process_file = act
    except TypeError: # not iterable
        # If an iterable is provided but it has the wrong number of
        # callables, that `ValueError` should propagate.
        act = act, act
    return _process(traversal, act, [initial])
