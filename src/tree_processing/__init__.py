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
